"""Recovery must wait for full coverage and submit each replacement stage once."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hpc.ufv.restore_after_retrieval import restore


class RestoreAfterRetrievalTests(unittest.TestCase):
    def test_waits_for_receipt_without_submitting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "hpc/logs/run/maintenance/ast-recovery-20261020").mkdir(parents=True)
            with patch("hpc.ufv.restore_after_retrieval.subprocess.run") as submit:
                state = restore(root, "run")
            self.assertFalse(state["complete"])
            submit.assert_not_called()

    def test_completed_recovery_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repair = root / "hpc/logs/run/maintenance/ast-recovery-20261020"
            repair.mkdir(parents=True)
            expected = dict(complete=True, jobs={"main_m0": "123"})
            (repair / "restored_graph.json").write_text(json.dumps(expected))
            with patch("hpc.ufv.restore_after_retrieval.subprocess.run") as submit:
                self.assertEqual(restore(root, "run"), expected)
            submit.assert_not_called()

    def test_successful_graph_and_restart_never_duplicate_stage_submission(self):
        from types import SimpleNamespace

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            repair = root / "hpc/logs/run/maintenance/ast-recovery-20261020"
            repair.mkdir(parents=True)
            (repair / "validation.json").write_text('{"complete": true}')
            (repair / "events.json").write_text("[]")
            results = Path(tmp) / "work/runs/run/results"
            for folder in ("receipts", "data", "models"):
                (results / folder).mkdir(parents=True)
            (results / "data/manifest.json").write_text('{"unique_cases": 1}')
            (results / "receipts/retrieval__m0__s1__p0.json").write_text(
                '{"complete": true, "records": 2}'
            )
            for i in range(5):
                (results / f"models/{i}.preflight.json").write_text(
                    '{"complete": true, "valid_hypotheses": 1, "output_tokens": 1, "budget": 32000}'
                )
            config = root / "hpc/logs/run/config"
            config.mkdir()
            (config / "experiments.resolved.json").write_text(
                json.dumps(
                    dict(
                        stages=[
                            dict(name="main_m0", cells=[{}], depends=[]),
                            dict(
                                name="ablations_m0",
                                cells=[{}],
                                depends=[dict(stage="main_m0", type="afterany")],
                            ),
                            dict(
                                name="collect",
                                cells=[{}],
                                depends=[dict(stage="ablations_m0", type="afterany")],
                            ),
                        ]
                    )
                )
            )
            submit = root / "hpc/slurm/submit.py"
            submit.parent.mkdir(parents=True)
            submit.write_text(
                "class H:\n @staticmethod\n def source_env(path): return {}\ndef sbatch_cmd(stage, config, cluster, run, deps, args): return ['sbatch',stage['name'],*deps]\n"
            )
            calls = []

            def launch(command, **kwargs):
                calls.append(command)
                if len(calls) == 2:
                    return SimpleNamespace(
                        returncode=1, stdout="", stderr="temporary scheduler error"
                    )
                return SimpleNamespace(returncode=0, stdout=str(100 + len(calls)), stderr="")

            with patch("hpc.ufv.restore_after_retrieval.subprocess.run", side_effect=launch):
                with self.assertRaisesRegex(RuntimeError, "sbatch failed"):
                    restore(root, "run", Path(tmp) / "work")
                state = restore(root, "run", Path(tmp) / "work")
                self.assertTrue(state["complete"])
                self.assertEqual(sum(c[1] == "main_m0" for c in calls), 1)
                self.assertIn("afterany:101", calls[2])
                restore(root, "run", Path(tmp) / "work")
                self.assertEqual(len(calls), 4)
