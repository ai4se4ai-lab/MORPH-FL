"""Publish compact predictions/settings; retain source-containing full traces locally."""

import hashlib
import json
import shutil
from pathlib import Path

from morph_fl.application import read_rows

out = Path("experiments/baselines/results/predictions")
out.mkdir(parents=True, exist_ok=True)
metadata = {}
paths = (
    list(Path("artifacts/baselines/fulltree").glob("*.jsonl"))
    + list(Path("artifacts/baselines").glob("*__*.jsonl"))
    + list(Path("artifacts/baselines/fresh").glob("*/predictions.jsonl"))
    + list(Path("artifacts/baselines/mechanism").glob("*/predictions.jsonl"))
)
for path in sorted(paths):
    rows = []
    raw_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    for r in read_rows(path):
        row = {
            k: r[k]
            for k in [
                "source_sha256",
                "profile_sha256",
                "instance_id",
                "repo",
                "revision",
                "variant",
                "seed",
                "ranking",
                "function_ranking",
                "input_tokens",
                "output_tokens",
                "seconds",
                "status",
                "stop_reason",
                "resets",
                "probe_count",
                "duplicate_probes",
                "hypothesis_switches",
                "abstained",
                "confidence",
            ]
            if k in r
        }
        row["raw_source"] = str(path)
        row["raw_sha256"] = raw_digest
        if "backend" in r:
            metadata[r["model"] + ":free-text"] = r["backend"]
        else:
            manifest = path.with_suffix(".jsonl.config.json")
            row["settings"] = json.loads(manifest.read_text())["settings"]
            if row["settings"]["backend"]:
                metadata[path.parent.name.split("__")[0] + ":structured"] = row["settings"][
                    "backend"
                ]
        rows.append(row)
    name = (
        ("fulltree__" + path.name if path.parent.name == "fulltree" else path.name)
        if path.name != "predictions.jsonl"
        else path.parent.parent.name + "__" + path.parent.name + ".jsonl"
    )
    (out / name).write_text("".join(json.dumps(r) + "\n" for r in rows))
(out.parent / "model_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
shutil.copy("src/morph_fl/baselines/vendor/manifest.json", out.parent / "upstream_sources.json")
