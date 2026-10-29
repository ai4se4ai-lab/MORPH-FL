#!/usr/bin/env python3
"""One-shot Slurm continuation: validate a real smoke, then submit the authorized full graph.

Run in a tiny GPU allocation afterok:smoke_collect. No polling loop. Fail closed
on partial/empty outputs; never submit a second full graph on retry.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def validate(hpc, run):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hpclib as H

    config = json.loads((hpc / "logs" / run / "config/experiments.resolved.json").read_text())
    if not config.get("is_smoke"):
        raise ValueError("Expected smoke configuration")
    environment = H.source_env(hpc / "logs" / run / "config/cluster.env")
    base = H.run_dir(run, environment)
    complete = json.loads((base / "results/analysis/completeness.json").read_text())
    if (
        not complete.get("complete")
        or not complete.get("smoke")
        or complete["planned"] != complete["observed"]
    ):
        raise ValueError("Smoke exact-key coverage is incomplete")
    with (hpc / "logs" / run / "steps.tsv").open() as f:
        ledger = list(csv.DictReader(f, delimiter="\t"))
    checked = []
    for stage in config["stages"]:
        for number, cell in enumerate(stage["cells"]):
            for step in stage["steps"]:
                matches = [
                    r
                    for r in ledger
                    if r["stage"] == stage["name"]
                    and r["cell"] == H.cell_key(cell, number)
                    and r["step"] == step["name"]
                ]
                if not matches or matches[-1]["rc"] != "0":
                    raise ValueError(
                        "Missing successful step receipt: " + stage["name"] + "/" + step["name"]
                    )
                checked.append(stage["name"] + "/" + step["name"])
    pin = json.loads((base / "results/models/0.preflight.json").read_text())
    if not pin.get("valid_hypotheses") or not pin.get("output_tokens"):
        raise ValueError("No valid model preflight")
    collected = hpc / "logs" / run / "results"
    for name in ["summary.md", "csv/scores.csv", "csv/measured.csv"]:
        if (collected / name).stat().st_size < 2:
            raise ValueError("Empty collected output")
    return dict(smoke=run, checked_steps=checked, completeness=complete, valid_preflight=pin)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-run", required=True)
    args = parser.parse_args()
    hpc = Path(__file__).resolve().parents[1]
    receipt = hpc / "logs" / args.smoke_run / "full_continuation.json"
    if receipt.exists():
        print(receipt.read_text())
        return
    verification = validate(hpc, args.smoke_run)
    full_id = time.strftime("am-%Y%m%d-%H%M%S")
    payload = dict(
        state="submitting",
        full_run=full_id,
        gate_job=os.environ.get("SLURM_JOB_ID"),
        verification=verification,
    )
    with receipt.open("x") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    command = [
        sys.executable,
        str(hpc / "slurm/submit.py"),
        "--run-id",
        full_id,
        "--account",
        "def-mbabaei_gpu",
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    payload.update(
        state="submitted" if process.returncode == 0 else "submission_failed_needs_repair",
        stdout=process.stdout,
        stderr=process.stderr,
        returncode=process.returncode,
    )
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    if process.returncode:
        raise SystemExit(process.returncode)


if __name__ == "__main__":
    main()
