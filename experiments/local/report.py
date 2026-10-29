"""Collect real local pilot measurements without converting proxies into causal claims."""

import argparse
import csv
import json
import statistics
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--runs", nargs="+", required=True)
p.add_argument("--out", type=Path, required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
summary = []
raw = []
provenance = []
for directory in a.runs:
    root = Path(directory)
    manifest = json.loads((root / "manifest.json").read_text())
    provenance.append(dict(run=root.name, **manifest))
    for score in sorted(root.glob("*/scores.csv")):
        with score.open() as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            continue
        predictions = [
            json.loads(line)
            for line in (score.parent / "predictions.jsonl").read_text().splitlines()
            if line.strip()
        ]
        eligible = [r for r in rows if r["eligible"] == "True"]
        funcs = [r for r in rows if r["function_eligible"] == "True"]
        model = score.parent.name.split("__")[0]

        def mean(rows, key):
            return statistics.mean(float(r[key]) for r in rows) if rows else None

        actual_calls = sum(
            sum(event["type"] in {"agent_response", "invalid_response"} for event in r["audit"])
            for r in predictions
        )
        summary.append(
            dict(
                run=root.name,
                phase=manifest["phase"],
                model=model,
                variant=rows[0]["variant"],
                cases=len(rows),
                eligible=len(eligible),
                top1=mean(eligible, "top1"),
                top5=mean(eligible, "top5"),
                mrr=mean(eligible, "mrr"),
                function_cases=len(funcs),
                function_top1=mean(funcs, "function_top1"),
                function_mrr=mean(funcs, "function_mrr"),
                mean_input_tokens=mean(rows, "input_tokens"),
                mean_input_per_call=(
                    sum(r["input_tokens"] for r in predictions) / actual_calls
                    if actual_calls
                    else 0
                ),
                model_calls=actual_calls,
                empty_hypothesis_cases=sum(not r["hypotheses"] for r in predictions)
                if rows[0]["variant"] not in {"bm25", "graph"}
                else 0,
                mean_output_tokens=mean(rows, "output_tokens"),
                median_seconds=statistics.median(float(r["seconds"]) for r in rows),
                invalid_probes=sum(r["invalid_probes"] for r in predictions),
                resets=sum(r["resets"] for r in predictions),
            )
        )
        raw.extend(dict(run=root.name, model=model, **r) for r in rows)
        target = a.out / root.name / score.parent.name / "scores.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(score.read_text())
        configuration = score.parent / "predictions.jsonl.config.json"
        if configuration.exists():
            (target.parent / "config.json").write_text(configuration.read_text())
for name, rows in [("summary", summary), ("case_scores", raw)]:
    if rows:
        with (a.out / f"{name}.csv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
(a.out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
lines = [
    "# DGXSpark localization pilot",
    "",
    "Real local Ollama inference on pre-fix SWE-bench Lite snapshots. Labels are unreviewed patch-change proxies. One seed and three cases per split: exploratory only; no statistical significance or SOTA superiority claim. Development and held-out repositories are disjoint.",
    "",
    "| Run | Model | Variant | n | File Top-1 | Function Top-1 (eligible n) | Mean input tokens | Median seconds | Invalid outputs/probes |",
    "|---|---|---|---:|---:|---:|---:|---:|---:|",
]
for r in summary:
    func = (
        "n/a" if r["function_top1"] is None else f"{r['function_top1']:.1%} ({r['function_cases']})"
    )
    lines.append(
        f"| {r['run']} | {r['model']} | {r['variant']} | {r['cases']} | {r['top1']:.1%} | {func} | {r['mean_input_tokens']:.0f} | {r['median_seconds']:.2f} | {r['invalid_probes']} |"
    )
lines += [
    "",
    "`rerank`, `stateless_summary` and `no_forgetting` are controlled in-repository baselines, not executions of published Agentless/AutoFL systems. All LLM conditions use the same model/backend/token and tool limits within each source version. When generated hypotheses are rejected or absent, the explicitly abstaining pipeline retains its retrieval fallback; invalid outputs/proposals remain counted. Before/after versions intentionally change context construction. Quantized Ollama/structured decoding is not numerically interchangeable with BF16 Transformers on Nibi.",
    "",
    "Full traces remain in ignored artifacts/local/. Model digests and generation settings are in each predictions.jsonl.config.json sidecar. Prompt/response/evidence artifacts and tamper-evident audits are preserved for each case.",
]
(a.out / "report.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
