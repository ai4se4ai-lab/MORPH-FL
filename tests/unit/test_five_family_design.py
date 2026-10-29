import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hpc.scripts.hpclib import resolve, validate

ROOT = Path(__file__).resolve().parents[2]


class FiveFamilyTests(unittest.TestCase):
    def test_reused_data_checks_actual_coverage_before_linking(self):
        pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            archive = source / "case.tar.gz"
            archive.touch()
            membership = {
                "SWE-bench_Lite": [f"case-{i}" for i in range(300)],
                "SWE-bench_Verified": [f"case-{i}" for i in range(207, 707)],
            }
            manifest = dict(
                datasets=pins["datasets"],
                smoke=False,
                benchmark_sizes={k: len(v) for k, v in membership.items()},
                unique_cases=707,
                overlap=93,
            )
            (source / "manifest.json").write_text(json.dumps(manifest))
            (source / "membership.json").write_text(json.dumps(membership))
            cases = [
                dict(instance_id=f"case-{i}", revision="v", archive=str(archive))
                for i in range(707)
            ]
            labels = [dict(instance_id=r["instance_id"], revision="v") for r in cases]

            def write(name, rows):
                (source / name).write_text("".join(json.dumps(r) + "\n" for r in rows))

            write("cases.jsonl", cases)
            write("labels.jsonl", labels)
            for index, broken in enumerate(
                [
                    labels[:-1],
                    labels + [labels[0]],
                    [dict(r, revision="wrong") for r in labels],
                    labels,
                ]
            ):
                write("labels.jsonl", broken)
                out = Path(tmp) / f"data-{index}"
                process = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "hpc/ufv/reuse_data.py"),
                        "--source",
                        str(source),
                        "--out",
                        str(out),
                    ],
                    capture_output=True,
                    text=True,
                )
                if index < 3:
                    self.assertNotEqual(process.returncode, 0)
                    self.assertFalse(out.exists())
                else:
                    self.assertEqual(process.returncode, 0, process.stderr)
                    self.assertEqual(out.resolve(), source)

    def test_all_five_families_and_complete_resource_matrix(self):
        pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
        models = pins["models"]
        self.assertEqual(len(models), 5)
        self.assertEqual(len({m["family"] for m in models}), 5)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for folder in ("hpc/ufv", "hpc/config", "experiments/full"):
                (target / folder).mkdir(parents=True)
            for name in (
                "hpc/ufv/full_config.py",
                "hpc/config/experiments.json",
                "experiments/full/pins.json",
            ):
                shutil.copy(ROOT / name, target / name)
            subprocess.run([sys.executable, str(target / "hpc/ufv/full_config.py")], check=True)
            config = resolve(
                json.loads((target / "hpc/config/experiments.json").read_text()), False
            )
            self.assertFalse(validate(config))
            self.assertEqual(len(config["stages"]), 34)
            self.assertEqual(sum(len(s["cells"]) for s in config["stages"]), 733)
            collect = next(s for s in config["stages"] if s["name"] == "collect")
            for index in range(len(models)):
                self.assertIn(
                    dict(stage=f"model_preflight_m{index}", type="afterany"), collect["depends"]
                )
            for index, model in enumerate(models):
                main = next(s for s in config["stages"] if s["name"] == f"main_m{index}")
                self.assertEqual(len(main["cells"]), 96)
                self.assertEqual({c["model"] for c in main["cells"]}, {index})
                self.assertEqual(main["resources"]["gpus"], f"nvidia_a30:{model['ufv_gpus']}")
