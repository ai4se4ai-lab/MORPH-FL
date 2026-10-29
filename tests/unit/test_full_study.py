"""Full-study boundaries: structured parsing, safe snapshots, and side sampling."""

import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from experiments.full.inference import decode_object
from experiments.full.prepare import extract_python
from experiments.full.suite import jobs_for, selected_cases


class FullStudyTests(unittest.TestCase):
    def test_preflight_checks_all_workflows_not_only_morph(self):
        from experiments.full.suite import BUDGET_CORE, CORE, validate_preflight

        spec = dict(id="unit-model", revision="unit-commit")
        rows = [
            dict(
                variant=v,
                instance_id="unit",
                model_id=spec["id"],
                model_revision=spec["revision"],
                seed=1,
                budget=32000,
                track="main",
                input_tokens=100,
                output_tokens=50,
                hypotheses=[{"id": "unit-hypothesis"}] if v in BUDGET_CORE else [],
            )
            for v in CORE
        ]
        self.assertEqual(set(validate_preflight(rows, spec)), set(CORE))
        for variant, field, value in [
            ("fixed_reset", "hypotheses", []),
            ("agentless_adapted", "output_tokens", 0),
            ("morph", "model_revision", "different"),
            ("morph", "budget", 6000),
        ]:
            broken = [
                dict(row, **{field: value}) if row["variant"] == variant else dict(row)
                for row in rows
            ]
            with self.subTest(variant=variant, field=field), self.assertRaises(ValueError):
                validate_preflight(broken, spec)
        with self.assertRaises(ValueError):
            validate_preflight(rows[:-1] + [rows[0]], spec)

    def test_preflight_uses_primary_budget_without_changing_ordinary_smoke(self):
        from experiments.full.suite import CORE, resume_keys

        self.assertEqual(jobs_for("main", True, preflight=True), [(v, 32000, None) for v in CORE])
        self.assertEqual(jobs_for("main", True), [(v, 6000, None) for v in CORE])
        case = dict(
            instance_id="unit",
            repo="unit/repo",
            revision="v",
            report="public report",
            archive_sha256="archive-hash",
        )
        import hashlib

        settings = dict(
            track="main",
            seed=1,
            smoke=True,
            preflight=True,
            model=dict(id="model", revision="commit"),
        )
        row = dict(
            instance_id="unit",
            repo=case["repo"],
            revision="v",
            report_digest=hashlib.sha256(case["report"].encode()).hexdigest(),
            source_archive_sha256="archive-hash",
            run_signature="signature",
            track="main",
            seed=1,
            model_id="model",
            model_revision="commit",
            variant="morph",
            budget=32000,
            window=None,
        )
        self.assertEqual(len(resume_keys([row], [case], settings, "signature")), 1)
        with self.assertRaisesRegex(ValueError, "Unplanned"):
            resume_keys([dict(row, budget=6000)], [case], settings, "signature")

    def test_resume_rejects_changed_provenance_duplicate_and_unplanned_records(self):
        import hashlib

        from experiments.full.suite import resume_keys

        case = dict(
            instance_id="unit",
            repo="unit/repo",
            revision="v",
            report="public report",
            archive_sha256="archive-hash",
        )
        settings = dict(
            track="main", seed=1, smoke=False, model=dict(id="model", revision="model-commit")
        )
        row = dict(
            instance_id="unit",
            repo=case["repo"],
            revision="v",
            report_digest=hashlib.sha256(case["report"].encode()).hexdigest(),
            source_archive_sha256="archive-hash",
            run_signature="signature",
            track="main",
            seed=1,
            model_id="model",
            model_revision="model-commit",
            variant="morph",
            budget=32000,
            window=None,
        )
        self.assertEqual(
            resume_keys([row], [case], settings, "signature"), {("unit", "morph", 32000, None)}
        )
        for field, value in [
            ("revision", "changed"),
            ("report_digest", "changed"),
            ("source_archive_sha256", "changed"),
            ("seed", 2),
            ("model_revision", "changed"),
            ("run_signature", "changed"),
            ("budget", 16000),
            ("instance_id", "another-shard"),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                resume_keys([dict(row, **{field: value})], [case], settings, "signature")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            resume_keys([row, row], [case], settings, "signature")

    def test_json_fence_nested_brace_and_trailing_prose(self):
        self.assertEqual(
            decode_object('explain {bad}\n```json\n{"hypotheses":[{"x":"}"}]}\n```'),
            {"hypotheses": [{"x": "}"}]},
        )
        with self.assertRaises(ValueError):
            decode_object("no object")
        from morph_fl.inference.local import InvalidModelResponse

        with self.assertRaises(InvalidModelResponse) as failure:
            decode_object("original malformed generation")
        self.assertEqual(failure.exception.raw, "original malformed generation")

    def test_parser_rejects_nested_fragments_of_malformed_outer_responses(self):
        from morph_fl.inference.local import InvalidModelResponse

        for text in [
            '{"behavior":{"expected":null},"hypotheses":[],"relations":[...]}',
            '{"hypotheses":[{"path":"a.py"}]',
            '{"wrapper":{"hypotheses":[]}}',
        ]:
            with self.subTest(text=text), self.assertRaises(InvalidModelResponse) as failure:
                decode_object(text)
            self.assertEqual(failure.exception.raw, text)
        self.assertEqual(
            decode_object('{"metadata":{}} then {"hypotheses":[]}'), {"hypotheses": []}
        )

    def test_snapshot_extract_rejects_escape_links_and_non_python(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            out = Path(tmp) / "out"
            out.mkdir()
            with tarfile.open(archive, "w:gz") as tf:
                for name in ["safe/a.py", "../escape.py", "safe/hint.txt"]:
                    info = tarfile.TarInfo(name)
                    info.size = 4
                    tf.addfile(info, io.BytesIO(b"pass"))
                link = tarfile.TarInfo("safe/link.py")
                link.type = tarfile.SYMTYPE
                link.linkname = "../escape.py"
                tf.addfile(link)
            extract_python(archive, out)
            self.assertEqual(
                [str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()], ["safe/a.py"]
            )
            self.assertFalse((Path(tmp) / "escape.py").exists())

    def test_side_sample_is_deterministic_balanced_and_main_is_full(self):
        rows = [
            dict(instance_id=f"{repo}-{i}", repo=repo)
            for repo in ["a", "b", "c"]
            for i in range(80)
        ]
        side = selected_cases(rows, "ablations", False)
        self.assertEqual(len(side), 100)
        self.assertEqual(side, selected_cases(list(reversed(rows)), "ablations", False))
        counts = [sum(r["repo"] == repo for r in side) for repo in ["a", "b", "c"]]
        self.assertLessEqual(max(counts) - min(counts), 1)
        self.assertEqual(len(selected_cases(rows, "main", False)), 240)
        self.assertEqual(len(jobs_for("main", False)), 6)
        self.assertEqual(len(jobs_for("budgets", False)), 8)


if __name__ == "__main__":
    unittest.main()


class PaperPromotionTests(unittest.TestCase):
    def test_reject_duplicate_workflows_and_incomplete_seed_counts(self):
        import csv
        import json

        from experiments.full.paper_update import update
        from experiments.full.suite import CORE

        pins = json.loads(
            (Path(__file__).resolve().parents[2] / "experiments/full/pins.json").read_text()
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "analysis").mkdir()
            sizes = {"SWE-bench_Lite": 300, "SWE-bench_Verified": 500}
            (root / "analysis/completeness.json").write_text(
                json.dumps(
                    dict(
                        complete=True,
                        smoke=False,
                        planned={"main": 63630},
                        observed={"main": 63630},
                        benchmark_sizes=sizes,
                    )
                )
            )
            rows = [
                dict(
                    track="main",
                    benchmark=b,
                    model=m["id"],
                    variant=v,
                    observed_seeds=3,
                    unique_cases=n,
                    case_seed_records=3 * n,
                    budget=32000,
                )
                for b, n in sizes.items()
                for m in pins["models"]
                for v in CORE
            ]
            for field, value in [
                ("variant", "no_forgetting"),
                ("case_seed_records", 899),
                ("budget", 16000),
            ]:
                broken = [dict(row) for row in rows]
                broken[0][field] = value
                with (root / "analysis/summary.csv").open("w") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(broken)
                with self.assertRaises(ValueError):
                    update(root, root / "paper")
                self.assertFalse((root / "paper").exists())

    def test_reject_partial_and_smoke_results(self):
        import json

        from experiments.full.paper_update import require_complete

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "analysis").mkdir()
            for complete, smoke in [(False, False), (True, True)]:
                (root / "analysis/completeness.json").write_text(
                    json.dumps(dict(complete=complete, smoke=smoke))
                )
                with self.assertRaises(ValueError):
                    require_complete(root)


class FullAnalysisTests(unittest.TestCase):
    def test_partial_coverage_retention_and_conditional_recovery(self):
        import csv
        import json

        from experiments.full.analyze import analyze
        from morph_fl.domain.models import identity

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["analysis", "data", "predictions"]:
                (root / name).mkdir()
            case = dict(
                instance_id="synthetic-unit-case",
                repo="unit/repo",
                revision="v",
                report="unit fixture only",
            )
            (root / "data/cases.jsonl").write_text(json.dumps(case) + "\n")
            (root / "data/labels.jsonl").write_text(
                json.dumps(
                    dict(
                        instance_id=case["instance_id"],
                        revision="v",
                        status="synthetic unit fixture",
                        files=["right.py"],
                        functions=["right.py::f"],
                    )
                )
                + "\n"
            )
            memberships = {
                "SWE-bench_Lite": [case["instance_id"]],
                "SWE-bench_Verified": [case["instance_id"]],
            }
            (root / "data/membership.json").write_text(json.dumps(memberships))
            (root / "data/manifest.json").write_text(
                json.dumps(dict(benchmark_sizes={k: 1 for k in memberships}, overlap=1))
            )
            hypothesis = dict(
                path="wrong.py", mechanism="wrong clue", probe=dict(kind="source_quote")
            )
            leader = identity(("wrong.py", "wrong clue", "source_quote"))
            row = dict(
                instance_id=case["instance_id"],
                repo=case["repo"],
                revision="v",
                variant="morph",
                seed=1,
                model_id="Qwen/Qwen2.5-Coder-7B-Instruct",
                model_revision=json.loads(
                    (Path(__file__).resolve().parents[2] / "experiments/full/pins.json").read_text()
                )["models"][0]["revision"],
                budget=6000,
                window=None,
                ranking=["right.py"],
                function_ranking=[],
                input_tokens=100,
                output_tokens=10,
                end_to_end_seconds=1,
                observations=[dict(id="E1")],
                audit=[
                    dict(type="reset", observations=["E1"], step=4),
                    dict(type="agent_response", response=dict(hypotheses=[hypothesis])),
                    dict(type="round", leader=leader),
                ],
                initial_clue_path="wrong.py",
            )
            for track in ["main", "misdirection"]:
                (root / "predictions" / (track + ".jsonl")).write_text(
                    json.dumps(dict(**row, track=track)) + "\n"
                )
            # Empty failed cells and scores left by a removed cell must not
            # crash partial analysis or inflate its scientific summaries.
            (root / "predictions/empty.jsonl").touch()
            (root / "scores").mkdir()
            (root / "scores/empty.csv").write_text("invalid stale scores\n")
            (root / "scores/removed.csv").write_text("invalid stale scores\n")
            analyze(root, smoke=True)
            self.assertFalse((root / "scores/empty.csv").exists())
            self.assertFalse((root / "scores/removed.csv").exists())
            completeness = json.loads((root / "analysis/completeness.json").read_text())
            self.assertFalse(completeness["complete"])
            self.assertGreater(completeness["missing_keys"], 0)
            self.assertEqual(
                len(json.loads((root / "analysis/reset_retention.json").read_text())), 2
            )
            recovery = json.loads((root / "analysis/recovery.json").read_text())
            self.assertTrue(recovery[0]["proxy_recovered"])
            with (root / "analysis/summary.csv").open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual({r["benchmark"] for r in rows}, set(memberships))
            self.assertTrue(all(int(r["case_seed_records"]) == 1 for r in rows))
            mismatched = dict(row, track="main", model_revision="wrong-checkpoint")
            (root / "predictions/main.jsonl").write_text(json.dumps(mismatched) + "\n")
            with self.assertRaisesRegex(ValueError, "model revision"):
                analyze(root, smoke=True)
            # A missing retained observation is a verification failure, not silent success.
            broken = dict(row, observations=[], track="main")
            (root / "predictions/main.jsonl").write_text(json.dumps(broken) + "\n")
            with self.assertRaisesRegex(ValueError, "retention"):
                analyze(root, smoke=True)
            for path in (root / "predictions").glob("*.jsonl"):
                path.unlink()
            analyze(root, smoke=True)
            with (root / "analysis/summary.csv").open() as stream:
                self.assertEqual(list(csv.DictReader(stream)), [])
            self.assertFalse(
                json.loads((root / "analysis/completeness.json").read_text())["complete"]
            )


class ProgressDenominatorTests(unittest.TestCase):
    def test_exact_denominator_can_arrive_after_submission(self):
        import json

        from hpc.scripts.hpclib import progress_expected

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = dict(expected_file="cell-{id}.json")
            self.assertIsNone(progress_expected(spec, dict(id=2), root))
            (root / "cell-2.json").write_text(json.dumps(dict(expected=18)))
            self.assertEqual(progress_expected(spec, dict(id=2), root), 18)
            (root / "cell-2.json").write_text(json.dumps(dict(expected=-1)))
            with self.assertRaises(ValueError):
                progress_expected(spec, dict(id=2), root)


class SmokeSizingTests(unittest.TestCase):
    def test_smoke_changes_resources_without_changing_full_graph(self):
        import json

        from hpc.scripts.hpclib import resolve

        path = Path(__file__).resolve().parents[2] / "hpc/config/experiments.json"
        for smoke in [False, True]:
            config = resolve(json.loads(path.read_text()), smoke)
            main = next(s for s in config["stages"] if s["name"] == "main")
            self.assertEqual(main["resources"]["gpus"], "h100_2g.20gb:1" if smoke else "h100:1")


class FullContinuationTests(unittest.TestCase):
    def test_gate_requires_every_step_receipt_and_nonempty_collected_outputs(self):
        import json

        from hpc.scripts.continue_full import validate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hpc = root / "hpc"
            run = "am-smoke-20000101-000000"
            logs = hpc / "logs" / run
            (logs / "config").mkdir(parents=True)
            (logs / "config/experiments.resolved.json").write_text(
                json.dumps(
                    dict(
                        is_smoke=True,
                        stages=[dict(name="stage", cells=[{}], steps=[dict(name="check")])],
                    )
                )
            )
            work = root / "work"
            (logs / "config/cluster.env").write_text('WORK="' + str(work) + '"\n')
            results = work / "runs" / run / "results"
            (results / "analysis").mkdir(parents=True)
            (results / "models").mkdir()
            (results / "analysis/completeness.json").write_text(
                json.dumps(
                    dict(complete=True, smoke=True, planned=dict(main=1), observed=dict(main=1))
                )
            )
            (results / "models/0.preflight.json").write_text(
                json.dumps(dict(valid_hypotheses=1, output_tokens=10))
            )
            (logs / "results/csv").mkdir(parents=True)
            for name in ["summary.md", "csv/scores.csv", "csv/measured.csv"]:
                (logs / "results" / name).write_text("nonempty unit fixture\n")
            header = "stage\tcell\tstep\trc\n"
            (logs / "steps.tsv").write_text(header + "stage\tall\tcheck\t1\n")
            with self.assertRaises(ValueError):
                validate(hpc, run)
            (logs / "steps.tsv").write_text(header + "stage\tall\tcheck\t0\n")
            self.assertEqual(validate(hpc, run)["checked_steps"], ["stage/check"])
            (logs / "results/csv/measured.csv").write_text("")
            with self.assertRaises(ValueError):
                validate(hpc, run)

    def test_cluster_paper_export_defers_smoke(self):
        import json

        from experiments.full.paper_update import export_bundle

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "analysis").mkdir()
            (root / "analysis/completeness.json").write_text(
                json.dumps(dict(complete=True, smoke=True))
            )
            export_bundle(root, root / "nonexistent_template")
            self.assertEqual(
                json.loads((root / "paper_export.json").read_text())["state"], "deferred"
            )
            self.assertFalse((root / "paper").exists())
