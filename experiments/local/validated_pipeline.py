"""Run the locked corrected source after earlier local experiments finish."""

import argparse
import json
import os
import select
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--after-pid", type=int)
args = p.parse_args()
if args.after_pid:
    try:
        descriptor = os.pidfd_open(args.after_pid)
        poller = select.poll()
        poller.register(descriptor, select.POLLIN)
        print("Waiting for development diagnostic run", flush=True)
        poller.poll()
        os.close(descriptor)
    except ProcessLookupError:
        pass
source = json.loads(Path("artifacts/local/validated-source.json").read_text())["source"]
for phase in ("dev", "test"):
    print("Starting locked", phase, flush=True)
    with Path(f"artifacts/local/validated-{phase}.log").open("a") as stream:
        subprocess.run(
            [
                sys.executable,
                "experiments/local/run.py",
                "--source",
                source,
                "--phase",
                phase,
                "--out",
                f"artifacts/local/validated-{phase}",
                "--models",
                "qwen2.5-coder:7b,qwen3-coder:30b",
            ],
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )
    print("Completed locked", phase, flush=True)
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
        "--out",
        "experiments/local/results",
    ],
    check=True,
)
print("LOCAL_PIPELINE_COMPLETE", flush=True)
