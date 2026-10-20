"""Collect every predeclared policy cell and verify reset/accounting invariants."""

import csv
import hashlib
import json
from pathlib import Path

from morph_fl.application import read_rows
from morph_fl.evaluation.metrics import metrics

protocol = json.loads(Path("experiments/alignment/protocol.json").read_text())
source_hash = hashlib.sha256()
for path in sorted(Path("src").rglob("*.py")):
    source_hash.update(str(path.relative_to("src")).encode())
    source_hash.update(path.read_bytes())
if source_hash.hexdigest() != protocol["source_sha256"]:
    raise ValueError("Alignment source changed during measurement")
expected_digests = {
    "qwen2.5-coder:7b": "dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364",
    "qwen3-coder:30b": "06c1097efce0431c2045fe7b2e5108366e43bee1b4603a7aded8f21689e90bca",
}
labels = {r["instance_id"]: r for r in read_rows("artifacts/local/data/dev/labels.jsonl")}
out = Path("experiments/alignment/results")
out.mkdir(parents=True, exist_ok=True)
rows = []
decisions = []
retention = []
provenance = []
for model in protocol["models"]:
    for window in protocol["windows"]:
        path = (
            Path("artifacts/alignment")
            / (model.replace(":", "_") + f"__window{window}")
            / "predictions.jsonl"
        )
        values = read_rows(path)
        if len(values) != 1 or values[0]["instance_id"] != protocol["case"]:
            raise ValueError("Incomplete policy cell")
        r = values[0]
        config = json.loads(path.with_suffix(".jsonl.config.json").read_text())["settings"]
        if (
            config["reset_policy"]["reset_window"] != window
            or config["reset_policy"]["reset_min_fraction"] != 0.15
        ):
            raise ValueError("Policy mismatch")
        if config["backend"]["digest"] != expected_digests[model]:
            raise ValueError("Alignment model digest mismatch")
        if not r["output_tokens"] or not any(e["type"] == "reset_decision" for e in r["audit"]):
            raise ValueError("Missing actual inference/reset diagnostics")
        used = r["input_tokens"] + r["output_tokens"]
        if used > 48000:
            raise ValueError("Overspending")
        if r["revision"] != labels[r["instance_id"]]["revision"]:
            raise ValueError("Label revision mismatch")
        observations = {e["id"] for e in r["observations"]}
        reset_events = [e for e in r["audit"] if e["type"] == "reset"]
        if len(reset_events) != r["resets"]:
            raise ValueError("Reset counter mismatch")
        for event in reset_events:
            if not set(event["observations"]) <= observations:
                raise ValueError("Lost observations")
            retention.append(
                dict(
                    model=model,
                    window=window,
                    step=event["step"],
                    retained=len(event["observations"]),
                    followed_by_request=any(
                        e["type"] == "agent_request" and e["step"] > event["step"]
                        for e in r["audit"]
                    ),
                )
            )
        for event in r["audit"]:
            if event["type"] == "reset_decision":
                decisions.append(dict(model=model, window_setting=window, **event))
        fs = metrics(r["ranking"], labels[r["instance_id"]]["files"])
        fun = metrics(r["function_ranking"], labels[r["instance_id"]]["functions"])
        rows.append(
            dict(
                model=model,
                window=window,
                min_fraction=0.15,
                resets=r["resets"],
                probes=r["probe_count"],
                duplicates=r["duplicate_probes"],
                tokens=used,
                file_top1=fs["top1"],
                function_top1=fun["top1"],
                stop=r["stop_reason"],
                calls=sum(e["type"] == "agent_response" for e in r["audit"]),
            )
        )
        provenance.append(
            dict(
                path=str(path),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                settings=config,
            )
        )
with (out / "summary.csv").open("w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
(out / "reset_decisions.json").write_text(json.dumps(decisions, indent=2) + "\n")
(out / "verification.json").write_text(
    json.dumps(
        dict(
            complete=True,
            source_sha256=protocol["source_sha256"],
            case_runs=len(rows),
            resets=retention,
            provenance=provenance,
        ),
        indent=2,
    )
    + "\n"
)
lines = [
    "# Configurable PPF development diagnostic",
    "",
    "One previously studied development issue; one seed; 48,000 tokens; eight rounds. Window settings and 15% minimum original-budget expenditure were declared before these runs. This is operational sensitivity, not hyperparameter calibration or held-out accuracy evidence.",
    "",
    "| Model | Window | Resets | Distinct probes | Duplicate proposals | Tokens | File Top-1 | Function Top-1 |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
]
for r in rows:
    lines.append(
        f"| {r['model']} | {r['window']} | {r['resets']} | {r['probes']} | {r['duplicates']} | {r['tokens']:,} | {r['file_top1']} | {r['function_top1']} |"
    )
lines += [
    "",
    "All recorded reset observations remain available in the final ledger. See verification.json for whether each reset was followed by another model request. A reset on the terminal round does not demonstrate a subsequent fresh investigation. No thresholds were selected as optimal from these outcomes. Settings are a separate source version from the upstream-baseline study.",
    "",
]
(out / "report.md").write_text("\n".join(lines))
print("Verified", len(rows), "policy case-runs;", len(retention), "reset events")
