import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from morph_fl.application import run_cases
from morph_fl.datasets.labels import patch_labels
from morph_fl.domain import Prediction
from morph_fl.evaluation.statistics import clustered_sign_flip, holm_adjust
from morph_fl.infrastructure.artifacts import ArtifactStore
from morph_fl.investigation import ProbeExecutor, SandboxConfig
from morph_fl.program_analysis import analyze_python
from morph_fl.transformations import evidence_update, synthesize


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        (self.root / "a.py").write_text("def calculate(total):\n    return total\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_run_resumes_and_rejects_setting_changes(self):
        cases = self.base / "cases.jsonl"
        cases.write_text(
            json.dumps(
                dict(
                    instance_id="case",
                    repo="toy/repo",
                    revision="v",
                    root=str(self.root),
                    report="calculate total",
                )
            )
            + "\n"
        )
        out = self.base / "predictions.jsonl"
        run_cases(cases, out, None, variant="bm25")
        run_cases(cases, out, None, variant="bm25")
        self.assertEqual(len(out.read_text().splitlines()), 1)
        with self.assertRaises(ValueError):
            run_cases(cases, out, None, variant="bm25", budget=20000)

    def test_patch_proxy_maps_old_lines_to_functions_and_excludes_tests(self):
        patch_text = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n def calculate(total):\n-    return total\n+    return total * .9\n"
        labels = patch_labels(patch_text, self.root)
        self.assertEqual(labels["files"], ["a.py"])
        self.assertEqual(labels["functions"], ["a.py::calculate"])
        self.assertEqual(labels["status"], "patch_proxy_requires_manual_review")

    def test_cluster_statistics_and_multiplicity(self):
        self.assertEqual(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        self.assertEqual(clustered_sign_flip([1, 1]), 0.5)

    def test_container_failure_is_not_a_reproduced_test_failure(self):
        image = self.base / "image.sif"
        image.write_bytes(b"fixture")
        sandbox = SandboxConfig(
            str(image), hashlib.sha256(b"fixture").hexdigest(), {"reproduce": ["pytest", "-q"]}
        )
        system = analyze_python(self.root, "v")
        hypothesis, probe = synthesize(
            dict(
                path="a.py",
                mechanism="wrong result",
                prediction=dict(description="test fails", predicate="test_fails", expected=True),
                probe=dict(path="a.py", line=2, kind="test", procedure_id="reproduce"),
            ),
            system,
        )

        class Process:
            returncode = 1
            pid = 123

            def wait(self, timeout=None):
                return 1

        captured = []

        def launch(command, **kwargs):
            captured.append(command)
            return Process()

        executor = ProbeExecutor(self.root, "v", ArtifactStore(self.base / "artifacts"), sandbox)
        with (
            patch("morph_fl.investigation.executor.shutil.which", return_value="/bin/apptainer"),
            patch("morph_fl.investigation.executor.subprocess.Popen", side_effect=launch),
        ):
            evidence = executor.execute(probe)
        self.assertTrue(evidence.observation["blocked"])
        self.assertEqual(evidence_update(hypothesis, probe, evidence).verdict, "inconclusive")
        self.assertIn("--cleanenv", captured[0])
        self.assertIn("--containall", captured[0])
        self.assertIn("none", captured[0])
        self.assertIn(f"{self.root}:/workspace:ro", captured[0])

    def test_dynamic_observation_requires_completed_inner_procedure(self):
        from dataclasses import replace

        image = self.base / "image.sif"
        image.write_bytes(b"fixture")
        sandbox = SandboxConfig(
            str(image), hashlib.sha256(b"fixture").hexdigest(), {"reproduce": ["pytest", "-q"]}
        )
        system = analyze_python(self.root, "v")
        hypothesis, probe = synthesize(
            dict(
                path="a.py",
                mechanism="wrong result",
                prediction="test fails",
                probe=dict(path="a.py", line=2),
            ),
            system,
        )
        probe = replace(
            probe,
            kind="test",
            parameters=dict(line=2, procedure_id="reproduce"),
            prediction=Prediction(
                "p", "test fails", "test_fails", True, ["original failure reproduces"]
            ),
        )

        class Process:
            returncode = 0
            pid = 123

            def wait(self, timeout=None):
                return 0

        def launch(command, **kwargs):
            mounts = [command[i + 1] for i, x in enumerate(command) if x == "--bind"]
            results = Path(next(m.split(":")[0] for m in mounts if ":/results:" in m))
            (results / "completed.json").write_text('{"returncode":1}')
            (results / "procedure.log").write_text("AssertionError: expected discounted total")
            return Process()

        executor = ProbeExecutor(self.root, "v", ArtifactStore(self.base / "artifacts"), sandbox)
        with (
            patch("morph_fl.investigation.executor.shutil.which", return_value="/bin/apptainer"),
            patch("morph_fl.investigation.executor.subprocess.Popen", side_effect=launch),
        ):
            evidence = executor.execute(probe)
        self.assertFalse(evidence.observation["blocked"])
        self.assertEqual(evidence_update(hypothesis, probe, evidence).verdict, "supports")
        self.assertEqual(evidence.observation["returncode"], 1)


class CounterfactualTests(unittest.TestCase):
    def test_counterfactual_requires_and_compares_baseline(self):
        from dataclasses import replace

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.py").write_text("def value():\n    return 100\n")
            system = analyze_python(root, "v")
            hypothesis, probe = synthesize(
                dict(
                    path="a.py",
                    mechanism="wrong total",
                    prediction=dict(
                        description="intervention changes outcome",
                        predicate="counterfactual_changes_outcome",
                        expected=True,
                        assumptions=["same input"],
                    ),
                    probe=dict(
                        path="a.py", line=2, kind="counterfactual", procedure_id="intervene"
                    ),
                ),
                system,
            )
            executor = ProbeExecutor(root, "v", ArtifactStore(root / "artifacts"))
            blocked = executor.execute(probe)
            self.assertTrue(blocked.observation["blocked"])
            probe = replace(
                probe, parameters=dict(probe.parameters, baseline_procedure_id="baseline")
            )
            with patch.object(
                executor,
                "_dynamic",
                side_effect=[dict(returncode=1, blocked=False), dict(returncode=0, blocked=False)],
            ):
                observation = executor.execute(probe)
            self.assertEqual(evidence_update(hypothesis, probe, observation).verdict, "supports")
            self.assertEqual(observation.observation["baseline"]["returncode"], 1)
