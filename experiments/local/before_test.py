"""Prospectively registered old-source held-out comparison, run after locked evaluation."""

import argparse
import json
import os
import select
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--after-pid", type=int, required=True)
a = p.parse_args()
try:
    descriptor = os.pidfd_open(a.after_pid)
    poller = select.poll()
    poller.register(descriptor, select.POLLIN)
    poller.poll()
    os.close(descriptor)
except ProcessLookupError:
    pass
protocol = json.loads(Path("experiments/local/protocol.json").read_text())
source = protocol["held_out_before_comparison"]["source"]
print("Starting original-source held-out control", flush=True)
with Path("artifacts/local/before-test.log").open("a") as stream:
    subprocess.run(
        [
            sys.executable,
            "experiments/local/run.py",
            "--source",
            source,
            "--phase",
            "test",
            "--out",
            "artifacts/local/before-test",
            "--models",
            "qwen2.5-coder:7b",
            "--variants",
            "morph",
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        check=True,
    )
subprocess.run(
    [
        sys.executable,
        "experiments/local/report.py",
        "--runs",
        "artifacts/local/before-dev",
        "artifacts/local/compact-dev",
        "artifacts/local/final-dev",
        "artifacts/local/validated-dev",
        "artifacts/local/validated-test",
        "artifacts/local/before-test",
        "--out",
        "experiments/local/results",
    ],
    check=True,
)
subprocess.run([sys.executable, "experiments/local/verify.py"], check=True)
print("HELD_OUT_COMPARISON_COMPLETE", flush=True)
