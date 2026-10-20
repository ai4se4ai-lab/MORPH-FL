"""Longer real-model development diagnostic; never tune against held-out results."""

import argparse
import json
import os
import select
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
if (
    "HELD_OUT_COMPARISON_COMPLETE"
    not in Path("artifacts/local/before-test-pipeline.log").read_text()
):
    raise RuntimeError("Local evaluation did not finish; diagnostic not started")
protocol = json.loads(Path("experiments/local/protocol.json").read_text())
plan = protocol["development_stress"]
sys.path.insert(0, str(Path(protocol["held_out_source"]).resolve()))
from morph_fl.application import read_rows, run_cases, score_predictions  # noqa: E402
from morph_fl.inference.ollama import OllamaModel  # noqa: E402

base = Path("artifacts/local/data/stress")
base.mkdir(parents=True, exist_ok=True)
for name in ("cases", "labels"):
    rows = [
        row
        for row in read_rows(Path("artifacts/local/data/dev") / f"{name}.jsonl")
        if row["instance_id"] == plan["instance_id"]
    ]
    (base / f"{name}.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
out = Path("artifacts/local/stress-dev")
out.mkdir(parents=True, exist_ok=True)
(out / "manifest.json").write_text(
    json.dumps(
        dict(
            phase="development-stress",
            source=protocol["held_out_source"],
            sha256=protocol["held_out_source_sha256"],
            models=plan["model"],
            variants=",".join(plan["variants"]),
            tokens=plan["tokens"],
            rounds=plan["rounds"],
            seeds=[1],
        ),
        indent=2,
    )
    + "\n"
)
backend = OllamaModel(plan["model"])
for variant in plan["variants"]:
    print("Stress", variant, flush=True)
    cell = out / (plan["model"].replace(":", "_") + "__" + variant)
    run_cases(
        base / "cases.jsonl",
        cell / "predictions.jsonl",
        backend,
        variant=variant,
        seed=1,
        budget=plan["tokens"],
        rounds=plan["rounds"],
        wall_seconds=300,
    )
    score_predictions(cell / "predictions.jsonl", base / "labels.jsonl", cell / "scores.csv")
    record = read_rows(cell / "predictions.jsonl")[0]
    print(
        json.dumps(
            {
                key: record[key]
                for key in (
                    "variant",
                    "resets",
                    "probe_count",
                    "duplicate_probes",
                    "input_tokens",
                    "output_tokens",
                    "stop_reason",
                )
            }
        ),
        flush=True,
    )
print("STRESS_DIAGNOSTIC_COMPLETE", flush=True)
