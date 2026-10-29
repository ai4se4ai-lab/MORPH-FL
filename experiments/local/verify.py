"""Gate HPC smoke on completed real-model plumbing, never on a desired score."""

import hashlib
import json
from pathlib import Path

protocol = json.loads(Path("experiments/local/protocol.json").read_text())
expected_hash = protocol["held_out_source_sha256"]
rows = 0
baseline_abstentions = 0
for phase in ("dev", "test"):
    base = Path(f"artifacts/local/validated-{phase}")
    manifest = json.loads((base / "manifest.json").read_text())
    if manifest["sha256"] != expected_hash or manifest["phase"] != phase:
        raise ValueError("Results do not match locked source/split")
    for model in protocol["models"]:
        for variant in protocol["variants"]:
            path = base / (model.replace(":", "_") + "__" + variant) / "predictions.jsonl"
            predictions = [
                json.loads(line) for line in path.read_text().splitlines() if line.strip()
            ]
            if {r["instance_id"] for r in predictions} != set(protocol["cases"][phase]) or len(
                predictions
            ) != len(protocol["cases"][phase]):
                raise ValueError(f"Incomplete or duplicated cell: {path}")
            for row in predictions:
                if row["input_tokens"] + row["output_tokens"] > protocol["tokens"]:
                    raise ValueError("Inference exceeded declared token cap")
                if variant not in {"bm25", "graph"}:
                    if not row["output_tokens"] or not any(
                        event["type"] == "agent_response" for event in row["audit"]
                    ):
                        raise ValueError("A model produced no valid decoded response")
                    if not row["hypotheses"]:
                        if variant == "morph":
                            raise ValueError("MORPH produced no valid hypotheses")
                        baseline_abstentions += 1
                if variant == "morph" and not row["observations"]:
                    raise ValueError("MORPH produced no verified observations")
            rows += len(predictions)
source = Path(protocol["held_out_source"])
hasher = hashlib.sha256()
for path in sorted(source.rglob("*.py")):
    hasher.update(str(path.relative_to(source)).encode())
    hasher.update(path.read_bytes())
if hasher.hexdigest() != expected_hash:
    raise ValueError("Frozen source was modified")
record = dict(
    source_sha256=expected_hash,
    case_runs=rows,
    ready_for_hpc_smoke=True,
    baseline_abstentions=baseline_abstentions,
    criteria="Completed cells, valid decoded inference, MORPH hypotheses/evidence, token caps and source integrity. Baseline localization abstentions remain scored outcomes; no accuracy threshold or significance claim",
)
Path("experiments/local/results/verification.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
