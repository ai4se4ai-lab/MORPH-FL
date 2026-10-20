"""Lock new case IDs by hash before preparing or evaluating their labels."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

from morph_fl.datasets.swebench import prepare_rows

root = Path("experiments/baselines")
rows = pq.read_table("artifacts/local/data/test.parquet").to_pylist()
previous = {
    json.loads(s)["repo"]
    for phase in ["dev", "test"]
    for s in Path(f"artifacts/local/data/{phase}/cases.jsonl").read_text().splitlines()
}
repos = sorted({r["repo"] for r in rows} - previous)[:6]
selected = [
    min(
        (r for r in rows if r["repo"] == repo),
        key=lambda r: hashlib.sha256(
            ("morph-upstream-fresh-v1:" + r["instance_id"]).encode()
        ).hexdigest(),
    )
    for repo in repos
]
protocol = dict(
    created_utc=datetime.now(UTC).isoformat(),
    selection="first six lexically sorted previously unused repositories; minimum SHA256(morph-upstream-fresh-v1:instance_id) per repo",
    cases=[r["instance_id"] for r in selected],
    models=["qwen2.5-coder:7b", "qwen3-coder:30b"],
    variants=["agentless_adapted", "rgfl_adapted", "morph", "stateless_summary", "bm25", "graph"],
    budget=16000,
    rounds=2,
    seeds=[1],
    source_sha256=json.loads((root / "protocol.json").read_text())["source_sha256"],
    notes="Exploratory fresh replication, same frozen implementations as pilot; no result-driven tuning. Six independent repositories, one case each. Unreviewed patch proxies.",
)
lock = root / "fresh_protocol.json"
if lock.exists():
    previous = json.loads(lock.read_text())
    if previous["cases"] != protocol["cases"]:
        raise ValueError("Selection changed")
else:
    lock.write_text(json.dumps(protocol, indent=2) + "\n")
print(protocol["cases"], flush=True)
prepare_rows(
    selected,
    Path("artifacts/baselines/fresh-data"),
    "6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2",
    "test",
)
