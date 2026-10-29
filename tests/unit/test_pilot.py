import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments.pilot import manage
from experiments.pilot.finalize import verify_receipts
from experiments.pilot.snapshot import completed_rows, snapshot


class PilotTests(unittest.TestCase):
    def test_snapshot_rejects_self_consistent_but_unfrozen_settings(self):
        from experiments.full import suite

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in ["data", "predictions", "experiments/full"]:
                (root / relative).mkdir(parents=True)
            protocol = root / "experiments/full/protocol.json"
            protocol.write_text("{}")
            spec = dict(id="unit-model", revision="pinned-commit")
            manage.write_json(root / "experiments/full/pins.json", dict(models=[spec]))
            case = dict(
                instance_id="case",
                repo="unit/repo",
                revision="source-commit",
                report="public report",
                archive_sha256="archive-hash",
            )
            (root / "data/cases.jsonl").write_text(json.dumps(case) + "\n")
            (root / "data/labels.jsonl").write_text(
                json.dumps(
                    dict(
                        instance_id="case", revision=case["revision"], files=["a.py"], functions=[]
                    )
                )
                + "\n"
            )
            manage.write_json(
                root / "pilot.json",
                dict(
                    selected_ids=["case"],
                    models=[0],
                    seed=1,
                    shards=32,
                    budget=32000,
                    variants=manage.VARIANTS,
                    protocol_sha256=manage.digest(protocol),
                    wrapper_sha256=manage.digest(manage.__file__),
                    cases_sha256=manage.digest(root / "data/cases.jsonl"),
                ),
            )
            path = root / "predictions/main__m0__s1__p0.jsonl"
            settings = dict(
                track="main",
                model=spec,
                seed=1,
                shard=0,
                shards=32,
                smoke=0,
                protocol_sha256=manage.digest(protocol),
            )

            def write_predictions(config):
                signature = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
                manage.write_json(path.with_suffix(".config.json"), config)
                records = [
                    dict(
                        instance_id="case",
                        repo=case["repo"],
                        revision=case["revision"],
                        report_digest=hashlib.sha256(case["report"].encode()).hexdigest(),
                        source_archive_sha256=case["archive_sha256"],
                        run_signature=signature,
                        track="main",
                        seed=1,
                        model_id=spec["id"],
                        model_revision=config["model"]["revision"],
                        budget=32000,
                        variant=v,
                        ranking=["a.py"],
                    )
                    for v in manage.VARIANTS
                ]
                path.write_text("".join(json.dumps(r) + "\n" for r in records))

            with patch.object(suite, "ROOT", root), patch.object(suite, "locked"):
                write_predictions(settings)
                snapshot(root)
                self.assertTrue(
                    json.loads((root / "interim-analysis/completeness.json").read_text())[
                        "complete"
                    ]
                )
                for changed in [
                    dict(settings, model=dict(spec, revision="different-commit")),
                    dict(settings, shards=16),
                    dict(settings, shard=-1),
                    dict(settings, shard=32),
                    dict(settings, shard=True),
                    dict(settings, preflight=True),
                ]:
                    write_predictions(changed)
                    with self.subTest(settings=changed), self.assertRaises(ValueError):
                        snapshot(root)
                write_predictions(settings)
                other = path.with_name("main__m0__s1__p1.jsonl")
                path.rename(other)
                path.with_suffix(".config.json").rename(other.with_suffix(".config.json"))
                with self.assertRaisesRegex(ValueError, "filename"):
                    snapshot(root)
                other.rename(path)
                other.with_suffix(".config.json").rename(path.with_suffix(".config.json"))
                protocol.write_text('{"changed": true}')
                with self.assertRaisesRegex(ValueError, "protocol"):
                    snapshot(root)

    def test_receipts_cover_partial_reuse_without_double_counting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "predictions").mkdir()
            (root / "receipts").mkdir()
            cell = "main__m0__s1__p0"
            records = [dict(instance_id="case", variant=v) for v in manage.VARIANTS]
            (root / "predictions" / (cell + ".jsonl")).write_text(
                "".join(json.dumps(r) + "\n" for r in records)
            )
            manage.write_json(
                root / "reuse.json", dict(records=[dict(file=cell + ".jsonl", **records[0])])
            )
            receipt = root / "receipts" / (cell + ".json")
            manage.write_json(receipt, dict(cell=cell, records=4, complete=True))
            self.assertEqual(
                verify_receipts(root),
                dict(imported_primary_records=1, successful_new_cells=1, new_receipt_records=3),
            )
            for bad in [
                dict(cell=cell, records=3, complete=True),
                dict(cell="another-cell", records=4, complete=True),
                dict(cell=cell, records=4, complete=False),
            ]:
                manage.write_json(receipt, bad)
                with self.subTest(receipt=bad), self.assertRaises(ValueError):
                    verify_receipts(root)
            receipt.unlink()
            with self.assertRaisesRegex(ValueError, "lack import provenance"):
                verify_receipts(root)
            manage.write_json(
                root / "reuse.json",
                dict(records=[dict(file=cell + ".jsonl", **r) for r in records]),
            )
            self.assertEqual(verify_receipts(root)["new_receipt_records"], 0)
            for invalid in [
                records + [records[0]],
                records + [dict(instance_id="missing", variant="morph")],
            ]:
                manage.write_json(
                    root / "reuse.json",
                    dict(records=[dict(file=cell + ".jsonl", **r) for r in invalid]),
                )
                with self.assertRaisesRegex(ValueError, "Duplicate or missing imported"):
                    verify_receipts(root)

    def test_live_snapshot_ignores_incomplete_tail_and_later_appends(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "predictions.jsonl"
            path.write_bytes(b'{"id": 1}\n{"id":')
            limit = path.stat().st_size
            with path.open("ab") as stream:
                stream.write(b" 2}\n")
            self.assertEqual(list(completed_rows(path, limit)), [{"id": 1}])
            self.assertEqual(
                list(completed_rows(path, path.stat().st_size)), [{"id": 1}, {"id": 2}]
            )

    def test_selection_is_order_independent_balanced_and_excludes_prior_cases(self):
        cases = [
            dict(instance_id=f"{repo}-{i}", repo=repo)
            for repo in ["a", "b", "c"]
            for i in range(30)
        ]
        selected = manage.select(cases, {"a-0"})
        self.assertEqual(selected, manage.select(list(reversed(cases)), {"a-0"}))
        self.assertEqual(len(set(selected)), 50)
        self.assertNotIn("a-0", selected)
        counts = [sum(i.startswith(r + "-") for i in selected) for r in ["a", "b", "c"]]
        self.assertLessEqual(max(counts) - min(counts), 1)

    def test_subset_preserves_original_shards_and_full_settings(self):
        from experiments import full

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "experiments/full").mkdir(parents=True)
            protocol = root / "experiments/full/protocol.json"
            protocol.write_text("{}")
            (root / "data").mkdir()
            cases = [dict(instance_id=str(i)) for i in range(100)]
            data = root / "data/cases.jsonl"
            data.write_text("".join(json.dumps(c) + "\n" for c in cases))
            manage.write_json(
                root / "pilot.json",
                dict(
                    selected_ids=["1", "33", "66"],
                    models=[0, 1],
                    variants=manage.VARIANTS,
                    wrapper_sha256=manage.digest(manage.__file__),
                    cases_sha256=manage.digest(data),
                    protocol_sha256=manage.digest(protocol),
                ),
            )

            def check(args):
                selected = fake.selected_cases(cases, "main", 0)[args.shard :: args.shards]
                self.assertEqual([c["instance_id"] for c in selected], ["1", "33"])
                self.assertEqual((args.seed, args.shards, args.smoke), (1, 32, 0))
                self.assertEqual(
                    fake.jobs_for("main", 0), [(v, 32000, None) for v in manage.VARIANTS]
                )

            fake = SimpleNamespace(
                ROOT=root,
                run=check,
                jobs_for=lambda *a: [(v, 32000, None) for v in manage.VARIANTS + ["rgfl_adapted"]],
            )
            with patch.object(full, "suite", fake, create=True):
                manage.run(SimpleNamespace(results=str(root), model=0, shard=1))

    def test_report_excludes_unpaired_cases(self):
        records = []
        for variant in manage.VARIANTS:
            records.append(
                dict(
                    model_id="q",
                    seed=1,
                    instance_id="paired",
                    repo="r",
                    variant=variant,
                    eligible=True,
                    top1=int(variant == "morph"),
                    top5=1,
                    function_top1=None,
                    tokens=100,
                    end_to_end_seconds=2,
                    resets=0,
                )
            )
        records.append(dict(records[0], instance_id="unpaired"))
        with tempfile.TemporaryDirectory() as temporary:
            manage.report(records, Path(temporary), "test")
            summary = json.loads((Path(temporary) / "summary.json").read_text())
            self.assertTrue(all(r["paired_issues"] == 1 for r in summary))
            self.assertEqual(summary[0]["top1"], 1)
            self.assertEqual(summary[1]["top1"], 0)


if __name__ == "__main__":
    unittest.main()
