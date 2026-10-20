"""Local synthetic plumbing check; never an experimental benchmark result."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PipelineTests(unittest.TestCase):
    def test_cli_scoring_statistics_and_collection(self):
        repo = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            hpc = base / "hpc"
            shutil.copytree(repo / "hpc", hpc, ignore=shutil.ignore_patterns("logs", "__pycache__"))
            run = "synthetic-fixture"
            cfg = hpc / "logs" / run / "config"
            cfg.mkdir(parents=True)
            sys.path.insert(0, str(hpc / "scripts"))
            # Resolve using the copied helper in a subprocess to avoid cached module paths.
            code = "import json,sys; sys.path.insert(0,sys.argv[1]); import hpclib as H; print(json.dumps(H.resolve(json.load(open(sys.argv[2])),True)))"
            resolved = subprocess.check_output(
                [
                    sys.executable,
                    "-c",
                    code,
                    str(hpc / "scripts"),
                    str(hpc / "config/experiments.json"),
                ],
                text=True,
            )
            (cfg / "experiments.resolved.json").write_text(resolved)
            (cfg / "cluster.env").write_text(
                f'ACCOUNT="fixture"\nWORK="{base}/work"\nRESULTS_DEST="{base}/collected"\n'
            )
            results = base / "work" / "runs" / run / "results"
            results.mkdir(parents=True)
            labels = base / "labels.jsonl"
            labels.write_text(
                json.dumps(
                    dict(
                        instance_id="toy",
                        revision="abc",
                        files=["a.py"],
                        status="synthetic_fixture",
                    )
                )
                + "\n"
            )
            env = dict(os.environ, PYTHONPATH=str(repo / "src"))
            for variant in ("morph", "bm25"):
                preds = base / f"{variant}.jsonl"
                preds.write_text(
                    json.dumps(
                        dict(
                            instance_id="toy",
                            repo="toy/repo",
                            revision="abc",
                            variant=variant,
                            seed=1,
                            ranking=["a.py"],
                            input_tokens=0,
                            output_tokens=0,
                            seconds=0.01,
                            resets=0,
                            duplicate_probes=0,
                            abstained=False,
                        )
                    )
                    + "\n"
                )
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "morph_fl.cli",
                        "score",
                        "--predictions",
                        str(preds),
                        "--labels",
                        str(labels),
                        "--out",
                        str(results / "scores" / f"{variant}.csv"),
                    ],
                    check=True,
                    env=env,
                    capture_output=True,
                )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "morph_fl.cli",
                    "analyze",
                    "--results",
                    str(results),
                    "--out",
                    str(results / "analysis/paired.json"),
                ],
                check=True,
                env=env,
                capture_output=True,
            )
            subprocess.run(
                [sys.executable, str(hpc / "scripts/collect_results.py"), run],
                check=True,
                env=env,
                capture_output=True,
            )
            out = base / "collected"
            for path in (
                "summary.md",
                "csv/scores.csv",
                "csv/measured.csv",
                "tables/measured.md",
                "tables/measured.tex",
                "figures/top1.png",
                "figures/top1.pdf",
                "raw/analysis/paired.json",
            ):
                self.assertTrue((out / path).stat().st_size > 0, path)
            self.assertIn("SMOKE: not for reporting", (out / "summary.md").read_text())
