"""Run pinned upstream adaptations; score only after every inference completes."""

import hashlib
import json
import os
from pathlib import Path

from morph_fl.application import read_rows
from morph_fl.baselines.local import TextOllama, localize

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/baselines"
OUT.mkdir(parents=True, exist_ok=True)
protocol = json.loads((ROOT / "experiments/baselines/protocol.json").read_text())
source = hashlib.sha256()
measured_source = Path(os.environ.get("MORPH_FL_SOURCE", ROOT / "src")).resolve()
for p in sorted(measured_source.rglob("*.py")):
    source.update(str(p.relative_to(measured_source)).encode())
    source.update(p.read_bytes())
if source.hexdigest() != protocol["source_sha256"]:
    raise ValueError("Source changed after protocol lock")
for model in protocol["models"]:
    backend = TextOllama(model)
    backend.metadata["structured_outputs"] = False
    for phase in ["dev", "test"]:
        for variant in protocol["variants"]:
            out = OUT / f"{phase}__{model.replace(':', '_')}__{variant}.jsonl"
            previous = read_rows(out) if out.exists() else []
            done = {x["instance_id"] for x in previous}
            for case in read_rows(ROOT / f"artifacts/local/data/{phase}/cases.jsonl"):
                if case["instance_id"] in done:
                    continue
                backend.set_seed(
                    int(hashlib.sha256(f"1:{case['instance_id']}".encode()).hexdigest()[:8], 16)
                )
                print(
                    json.dumps(
                        dict(
                            event="start",
                            model=model,
                            phase=phase,
                            variant=variant,
                            case=case["instance_id"],
                        )
                    ),
                    flush=True,
                )
                result = localize(case, backend, variant, protocol["budget"])
                result.update(
                    model=model,
                    phase=phase,
                    seed=1,
                    backend=backend.metadata,
                    source_sha256=source.hexdigest(),
                )
                with out.open("a") as stream:
                    stream.write(json.dumps(result) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                print(
                    json.dumps(
                        {
                            k: result[k]
                            for k in [
                                "instance_id",
                                "ranking",
                                "status",
                                "seconds",
                                "input_tokens",
                                "output_tokens",
                            ]
                        }
                    ),
                    flush=True,
                )
print("ALL INFERENCE COMPLETE", flush=True)
