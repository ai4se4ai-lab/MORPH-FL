"""Submit a small Nibi smoke only after locked local matrix validation succeeds."""

import argparse
import json
import os
import re
import select
import shlex
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--after-pid", type=int, required=True)
args = p.parse_args()
try:
    descriptor = os.pidfd_open(args.after_pid)
    poller = select.poll()
    poller.register(descriptor, select.POLLIN)
    poller.poll()
    os.close(descriptor)
except ProcessLookupError:
    pass
subprocess.run([sys.executable, "experiments/local/verify.py"], check=True)
verification = json.loads(Path("experiments/local/results/verification.json").read_text())
ssh = [
    "ssh",
    "-o",
    "BatchMode=yes",
    "-o",
    f"ControlPath={Path.home()}/.ssh/controlmasters/%r@%h:%p",
]
host = "mbabaei@nibi.alliancecan.ca"
destination = "/project/def-mbabaei/mbabaei/MORPH-FL-dgxspark-v1"
command = ["rsync", "-az"] + [
    f"--exclude={pattern}"
    for pattern in (
        ".git",
        "artifacts/",
        "build/",
        "dist/",
        "__pycache__",
        "*.egg-info/",
        ".ruff_cache/",
        "hpc/logs/",
    )
]
subprocess.run(command + ["-e", shlex.join(ssh), "./", host + ":" + destination + "/"], check=True)
code = "import hashlib;from pathlib import Path;root=Path('src');h=hashlib.sha256();[(h.update(str(p.relative_to(root)).encode()),h.update(p.read_bytes())) for p in sorted(root.rglob('*.py'))];print(h.hexdigest())"
remote_hash = subprocess.check_output(
    ssh + [host, "cd " + shlex.quote(destination) + " && python3 -c " + shlex.quote(code)],
    text=True,
).strip()
if remote_hash != verification["source_sha256"]:
    raise ValueError("Remote source differs from the locked local implementation")
remote = (
    "cd "
    + shlex.quote(destination)
    + " && bash hpc/scripts/selftest.sh && python3 hpc/slurm/submit.py --smoke"
)
print("Submitting corrected Nibi smoke", flush=True)
output = subprocess.check_output(ssh + [host, remote], text=True)
Path("artifacts/local/nibi-submission.log").write_text(output)
match = re.search(r"RUN_ID (\S+)", output)
if not match:
    raise RuntimeError("Submission returned no run ID")
record = dict(
    run_id=match.group(1),
    source_sha256=remote_hash,
    deployment=destination,
    jobs={
        name: int(job)
        for name, job in re.findall(r"^\s*(setup|main|score|collect)\s+job (\d+)", output, re.M)
    },
    scope="small real-GPU smoke; full study not submitted",
)
Path("experiments/local/results/nibi_submission.json").write_text(
    json.dumps(record, indent=2) + "\n"
)
print(output, flush=True)
print("NIBI_SMOKE_SUBMITTED", flush=True)
