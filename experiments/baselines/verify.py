"""Fail closed on missing cells, mismatched models, overspending or lost evidence."""

import hashlib
import json
from pathlib import Path

from morph_fl.application import read_rows

root = Path("artifacts/baselines")
protocol = json.loads(Path("experiments/baselines/protocol.json").read_text())
fresh = json.loads(Path("experiments/baselines/fresh_protocol.json").read_text())
expected_digests = {
    "qwen2.5-coder:7b": "dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364",
    "qwen3-coder:30b": "06c1097efce0431c2045fe7b2e5108366e43bee1b4603a7aded8f21689e90bca",
}
checked = []
resets = []
tokenizers = {}
for phase in ["dev", "test", "fresh", "mechanism"]:
    ids = set(
        fresh["cases"]
        if phase == "fresh"
        else ["pydicom__pydicom-901"]
        if phase == "mechanism"
        else protocol["cases"][phase]
    )
    variants = (
        ["morph", "no_forgetting", "fixed_reset", "stateless_summary"]
        if phase == "mechanism"
        else fresh["variants"]
        if phase == "fresh"
        else protocol["variants"]
    )
    for model in protocol["models"]:
        for variant in variants:
            external = variant.endswith("_adapted")
            key = model.replace(":", "_") + "__" + variant
            path = (
                root / f"{phase}__{key}.jsonl"
                if external
                else root / phase / key / "predictions.jsonl"
            )
            records = read_rows(path)
            if len(records) != len(ids) or {r["instance_id"] for r in records} != ids:
                raise ValueError(f"Coverage: {path}")
            if external:
                metadata = records[0]["backend"]
                if any(
                    r["backend"] != metadata or r["source_sha256"] != protocol["source_sha256"]
                    for r in records
                ):
                    raise ValueError("Inconsistent provenance")
            else:
                metadata = json.loads(path.with_suffix(".jsonl.config.json").read_text())[
                    "settings"
                ]["backend"]
            if variant not in ["bm25", "graph"] and metadata["digest"] != expected_digests[model]:
                raise ValueError("Model digest changed")
            if metadata:
                signature = (
                    metadata["tokenizer_sha256"],
                    metadata["tokenizer_revision"],
                    metadata["context"],
                    metadata["temperature"],
                    metadata["server"],
                )
                if model in tokenizers and tokenizers[model] != signature:
                    raise ValueError("Tokenizer or sampling settings changed")
                tokenizers[model] = signature
            for r in records:
                cap = 48000 if phase == "mechanism" else 16000
                if r["input_tokens"] + r["output_tokens"] > cap:
                    raise ValueError("Token overspend")
                if external:
                    if (
                        sum(t["input_tokens"] for t in r["trace"]) != r["input_tokens"]
                        or sum(t["output_tokens"] for t in r["trace"]) != r["output_tokens"]
                    ):
                        raise ValueError("Trace accounting mismatch")
                else:
                    final = {e["id"] for e in r["observations"]}
                    for event in r["audit"]:
                        if event.get("type") == "reset":
                            if not set(event["observations"]) <= final:
                                raise ValueError("Reset lost observation")
                            resets.append(
                                dict(
                                    model=model,
                                    variant=variant,
                                    phase=phase,
                                    case=r["instance_id"],
                                    retained_observations=len(event["observations"]),
                                )
                            )
            checked.append(
                dict(
                    path=str(path),
                    cases=len(records),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                )
            )
profile = json.loads(Path("experiments/baselines/full_tree_protocol.json").read_text())
if (
    hashlib.sha256(Path("experiments/baselines/full_tree.py").read_bytes()).hexdigest()
    != profile["runner_sha256"]
):
    raise ValueError("Sensitivity runner changed")
for model in protocol["models"]:
    for variant in protocol["variants"]:
        path = root / "fulltree" / (model.replace(":", "_") + "__" + variant + ".jsonl")
        records = read_rows(path)
        if len(records) != 6 or {r["instance_id"] for r in records} != set(fresh["cases"]):
            raise ValueError("Sensitivity coverage incomplete")
        for r in records:
            if (
                r["profile_sha256"] != profile["runner_sha256"]
                or r["source_sha256"] != protocol["source_sha256"]
            ):
                raise ValueError("Sensitivity source mismatch")
            if r["backend"]["digest"] != expected_digests[model]:
                raise ValueError("Sensitivity model mismatch")
            if r["input_tokens"] + r["output_tokens"] > 16000:
                raise ValueError("Sensitivity budget violation")
            if (
                sum(t["input_tokens"] + t["output_tokens"] for t in r["trace"])
                != r["input_tokens"] + r["output_tokens"]
            ):
                raise ValueError("Sensitivity trace accounting mismatch")
        checked.append(
            dict(
                path=str(path),
                cases=len(records),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
Path("experiments/baselines/results/verification.json").write_text(
    json.dumps(dict(complete=True, checked=checked, reset_retention=resets), indent=2) + "\n"
)
print(
    "Verified",
    sum(c["cases"] for c in checked),
    "new case-runs;",
    len(resets),
    "reset retention events",
)
