"""Development-only PPF window sensitivity, frozen before model execution."""

import hashlib
import json
from pathlib import Path

from morph_fl.application import read_rows, run_cases
from morph_fl.inference.ollama import OllamaModel

protocol = json.loads(Path("experiments/alignment/protocol.json").read_text())
h = hashlib.sha256()
for p in sorted(Path("src").rglob("*.py")):
    h.update(str(p.relative_to("src")).encode())
    h.update(p.read_bytes())
if h.hexdigest() != protocol["source_sha256"]:
    raise ValueError("Alignment source changed")
root = Path("artifacts/alignment")
root.mkdir(parents=True, exist_ok=True)
case = next(
    r
    for r in read_rows("artifacts/local/data/dev/cases.jsonl")
    if r["instance_id"] == protocol["case"]
)
cases = root / "cases.jsonl"
cases.write_text(json.dumps(case) + "\n")
for model in protocol["models"]:
    backend = OllamaModel(model)
    for window in protocol["windows"]:
        policy = dict(reset_window=window, reset_min_rounds=4, reset_min_fraction=0.15)
        print("START", model, policy, flush=True)
        run_cases(
            cases,
            root / (model.replace(":", "_") + f"__window{window}") / "predictions.jsonl",
            backend,
            variant="morph",
            seed=1,
            budget=48000,
            rounds=8,
            wall_seconds=600,
            reset_policy=policy,
        )
        print("DONE", model, window, flush=True)
print("ALIGNMENT COMPLETE", flush=True)
