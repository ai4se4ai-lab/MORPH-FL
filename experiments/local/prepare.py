"""Select cases from public IDs only, before any localization result is inspected."""

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

from morph_fl.datasets.swebench import prepare_rows

base = Path("artifacts/local/data")
revision = "6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2"
subjects = {
    "dev": ["marshmallow-code/marshmallow", "pydicom/pydicom", "pvlib/pvlib-python"],
    "test": ["psf/requests", "pallets/flask", "pytest-dev/pytest"],
}
plan = {}
for split, repos in subjects.items():
    rows = pq.read_table(base / f"{split}.parquet").to_pylist()
    selected = [
        min(
            (r for r in rows if r["repo"] == repo),
            key=lambda r: hashlib.sha256(
                ("morph-local-v1:" + r["instance_id"]).encode()
            ).hexdigest(),
        )
        for repo in repos
    ]
    plan[split] = [r["instance_id"] for r in selected]
Path("experiments/local/protocol.json").write_text(
    json.dumps(
        dict(
            dataset_revision=revision,
            selection="one case per declared repository; minimum SHA256(morph-local-v1:instance_id), no label inspection",
            cases=plan,
            development_only=plan["dev"],
            held_out=plan["test"],
            models=["qwen2.5-coder:7b", "qwen3-coder:30b"],
            variants=["bm25", "graph", "rerank", "stateless_summary", "no_forgetting", "morph"],
            seeds=[1],
            tokens=16000,
            rounds=2,
            interpretation="small exploratory localization pilot; unreviewed patch proxies; no significance claim",
        ),
        indent=2,
    )
    + "\n"
)
for split, repos in subjects.items():
    rows = pq.read_table(base / f"{split}.parquet").to_pylist()
    selected = [r for r in rows if r["instance_id"] in plan[split]]
    print("Preparing", split, plan[split], flush=True)
    prepare_rows(selected, base / split, revision, split)
