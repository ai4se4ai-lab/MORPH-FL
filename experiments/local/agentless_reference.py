"""Evaluate published Agentless artifacts as a separate, unmatched reference."""

import hashlib
import json
import zipfile
from pathlib import Path

from morph_fl.application import read_rows, score_predictions
from morph_fl.evaluation.external import import_agentless

archive = Path("artifacts/local/external/agentless_swebench_lite.zip")
cases = Path("artifacts/local/data/test/cases.jsonl")
labels = Path("artifacts/local/data/test/labels.jsonl")
ids = {row["instance_id"] for row in read_rows(cases)}
out = Path("experiments/local/results/agentless_reference")
out.mkdir(parents=True, exist_ok=True)
with archive.open("rb") as stream:
    digest = hashlib.file_digest(stream, "sha256").hexdigest()
manifest = dict(
    release="v1.5.0",
    upstream_commit="b150f28",
    source_url="https://github.com/OpenAutoCoder/Agentless/releases/tag/v1.5.0",
    archive_sha256=digest,
    comparison="UNMATCHED published artifacts, not a local reproduction",
    source_alignment="Instance-ID mapping to current pinned SWE-bench Lite cases; upstream source hashes not independently revalidated",
    limitations=[
        "GPT-4o rather than local Qwen",
        "Different retrieval/source scope and token/tool budgets",
        "Runtime/cost unavailable",
        "No superiority/significance inference",
    ],
)
with zipfile.ZipFile(archive) as z:
    manifest["file_level_settings"] = json.loads(
        z.read("agentless_swebench_lite/file_level/args.json")
    )
    for name, member in [
        ("file_level", "file_level/loc_outputs.jsonl"),
        ("combined", "file_level_combined/combined_locs.jsonl"),
    ]:
        rows = [
            json.loads(line)
            for line in z.read("agentless_swebench_lite/" + member).splitlines()
            if line.strip()
        ]
        selected = [row for row in rows if row["instance_id"] in ids]
        manifest[name + "_coverage"] = dict(
            requested=len(ids),
            found=len(selected),
            missing=sorted(ids - {r["instance_id"] for r in selected}),
        )
        raw = out / f"{name}_raw.jsonl"
        raw.write_text(
            "".join(
                json.dumps(dict(instance_id=r["instance_id"], found_files=r["found_files"])) + "\n"
                for r in selected
            )
        )
        predictions = out / f"{name}_predictions.jsonl"
        import_agentless(raw, cases, predictions)
        score_predictions(predictions, labels, out / f"{name}_scores.csv")
(out / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(
    json.dumps(
        {key: value for key, value in manifest.items() if key.endswith("_coverage")}, indent=2
    )
)
