"""Sequential fresh replication followed by a predeclared development diagnostic."""

import hashlib
import json
import os
from pathlib import Path

from morph_fl.application import read_rows, run_cases
from morph_fl.baselines.local import TextOllama, localize
from morph_fl.inference.ollama import OllamaModel

root = Path("artifacts/baselines")
protocol = json.loads(Path("experiments/baselines/fresh_protocol.json").read_text())
h = hashlib.sha256()
measured_source = Path(os.environ.get("MORPH_FL_SOURCE", "src")).resolve()
for p in sorted(measured_source.rglob("*.py")):
    h.update(str(p.relative_to(measured_source)).encode())
    h.update(p.read_bytes())
if h.hexdigest() != protocol["source_sha256"]:
    raise ValueError("Frozen source mismatch")
cases = root / "fresh-data/cases.jsonl"
for model in protocol["models"]:
    backend = TextOllama(model)
    backend.metadata["structured_outputs"] = False
    for variant in ["agentless_adapted", "rgfl_adapted"]:
        out = root / f"fresh__{model.replace(':', '_')}__{variant}.jsonl"
        done = {r["instance_id"] for r in read_rows(out)} if out.exists() else set()
        for case in read_rows(cases):
            if case["instance_id"] in done:
                continue
            print("START", model, variant, case["instance_id"], flush=True)
            backend.set_seed(
                int(hashlib.sha256(f"1:{case['instance_id']}".encode()).hexdigest()[:8], 16)
            )
            row = localize(case, backend, variant)
            row.update(
                model=model,
                phase="fresh",
                seed=1,
                backend=backend.metadata,
                source_sha256=h.hexdigest(),
            )
            with out.open("a") as f:
                f.write(json.dumps(row) + "\n")
                f.flush()
                os.fsync(f.fileno())
            print("DONE", row["status"], row["seconds"], flush=True)
    backend = OllamaModel(model)
    for variant in ["bm25", "graph", "stateless_summary", "morph"]:
        print("START", model, variant, "fresh", flush=True)
        run_cases(
            cases,
            root / "fresh" / f"{model.replace(':', '_')}__{variant}" / "predictions.jsonl",
            None if variant in ["bm25", "graph"] else backend,
            variant=variant,
            seed=1,
            budget=16000,
            rounds=2,
            wall_seconds=300,
        )
        print("DONE", model, variant, "fresh", flush=True)
# One original development case only; choose by public ID, no planted gold-informed clue.
case = next(
    r
    for r in read_rows("artifacts/local/data/dev/cases.jsonl")
    if r["instance_id"] == "pydicom__pydicom-901"
)
case_path = root / "mechanism-cases.jsonl"
case_path.write_text(json.dumps(case) + "\n")
for model in protocol["models"]:
    backend = OllamaModel(model)
    for variant in ["morph", "no_forgetting", "fixed_reset", "stateless_summary"]:
        print("START", model, variant, "mechanism", flush=True)
        run_cases(
            case_path,
            root / "mechanism" / f"{model.replace(':', '_')}__{variant}" / "predictions.jsonl",
            backend,
            variant=variant,
            seed=1,
            budget=48000,
            rounds=8,
            wall_seconds=600,
        )
        print("DONE", model, variant, "mechanism", flush=True)
print("EXTENDED COMPLETE", flush=True)
