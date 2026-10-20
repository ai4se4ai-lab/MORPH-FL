"""Serialize local GPU pilots; use pidfd rather than polling or overlapping runs."""

import argparse
import json
import os
import select
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--after-pid", type=int)
a = p.parse_args()
if a.after_pid:
    try:
        descriptor = os.pidfd_open(a.after_pid)
        poller = select.poll()
        poller.register(descriptor, select.POLLIN)
        print(f"Waiting for prior pilot PID {a.after_pid}", flush=True)
        poller.poll()
        os.close(descriptor)
    except ProcessLookupError:
        pass
source = json.loads(Path("artifacts/local/final-source.json").read_text())["source"]
for phase in ("dev", "test"):
    log = Path(f"artifacts/local/final-{phase}.log")
    command = [
        sys.executable,
        "experiments/local/run.py",
        "--source",
        source,
        "--phase",
        phase,
        "--out",
        f"artifacts/local/final-{phase}",
        "--models",
        "qwen2.5-coder:7b,qwen3-coder:30b",
    ]
    print("Starting", phase, flush=True)
    with log.open("a") as stream:
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True)
    print("Completed", phase, flush=True)
subprocess.run(
    [
        sys.executable,
        "experiments/local/report.py",
        "--runs",
        "artifacts/local/before-dev",
        "artifacts/local/compact-dev",
        "artifacts/local/final-dev",
        "artifacts/local/final-test",
        "--out",
        "experiments/local/results",
    ],
    check=True,
)
print("LOCAL_PIPELINE_COMPLETE", flush=True)
