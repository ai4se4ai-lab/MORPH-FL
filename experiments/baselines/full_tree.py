"""Post-hoc context sensitivity; larger tree allocation, unchanged total budget.

The only intervention replaces the file_selection stage cap (2,600 -> 12,000).
The inherited investigator still enforces the shared 16,000 actual-token cap.
Run after extended.py to serialize GPU work. This is not new held-out validation.
"""

import argparse
import hashlib
import json
import os
import select
from pathlib import Path

from morph_fl.application import read_rows
from morph_fl.baselines import local


class FullTreeInvestigation(local.Investigation):
    def ask(self, stage, make_prompt, content, cap, output=512):
        if stage == "file_selection":
            cap = 12000
        return super().ask(stage, make_prompt, content, cap, output)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--after-pid", type=int)
    args = p.parse_args()
    protocol_path = Path("experiments/baselines/full_tree_protocol.json")
    protocol = json.loads(protocol_path.read_text())
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != protocol["runner_sha256"]:
        raise ValueError("Profile source changed")
    if args.after_pid:
        try:
            fd = os.pidfd_open(args.after_pid)
        except ProcessLookupError:
            pass
        else:
            poller = select.poll()
            poller.register(fd, select.POLLIN)
            poller.poll()
            os.close(fd)
    if "EXTENDED COMPLETE" not in Path("artifacts/baselines-extended.log").read_text():
        raise ValueError("Prior run incomplete")
    local.Investigation = FullTreeInvestigation
    out = Path("artifacts/baselines/fulltree")
    out.mkdir(exist_ok=True)
    for model in protocol["models"]:
        backend = local.TextOllama(model)
        backend.metadata["structured_outputs"] = False
        for variant in ["agentless_adapted", "rgfl_adapted"]:
            destination = out / (model.replace(":", "_") + "__" + variant + ".jsonl")
            done = (
                {r["instance_id"] for r in read_rows(destination)}
                if destination.exists()
                else set()
            )
            for case in read_rows("artifacts/baselines/fresh-data/cases.jsonl"):
                if case["instance_id"] in done:
                    continue
                print("START", model, variant, case["instance_id"], flush=True)
                backend.set_seed(
                    int(hashlib.sha256(f"1:{case['instance_id']}".encode()).hexdigest()[:8], 16)
                )
                row = local.localize(case, backend, variant)
                row.update(
                    model=model,
                    variant=variant.replace("_adapted", "_fulltree"),
                    phase="fresh_sensitivity",
                    seed=1,
                    backend=backend.metadata,
                    source_sha256=protocol["source_sha256"],
                    profile_sha256=protocol["runner_sha256"],
                )
                with destination.open("a") as f:
                    f.write(json.dumps(row) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                print("DONE", row["status"], row["seconds"], flush=True)
    print("FULLTREE COMPLETE", flush=True)


if __name__ == "__main__":
    main()
