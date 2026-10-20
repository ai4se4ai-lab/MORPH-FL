"""Score pre-fix predictions separately from inference and export paired measurements."""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from morph_fl.application import read_rows
from morph_fl.evaluation.metrics import metrics, set_metrics

OUT = Path("experiments/baselines/results")
OUT.mkdir(parents=True, exist_ok=True)
rows = []
provenance = []


def collect(path, phase, model, variant, labels_path):
    labels = {r["instance_id"]: r for r in read_rows(labels_path)}
    provenance.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for r in read_rows(path):
        label = labels[r["instance_id"]]
        if r["revision"] != label["revision"]:
            raise ValueError("Revision mismatch")
        file_score = metrics(r["ranking"], label["files"])
        function_score = metrics(r.get("function_ranking", []), label["functions"])
        row = dict(
            phase=phase,
            model=model,
            variant=variant,
            instance_id=r["instance_id"],
            repo=r["repo"],
            revision=r["revision"],
            **{"file_" + k: v for k, v in file_score.items()},
            **{"function_" + k: v for k, v in function_score.items()},
            **{
                "file_set5_" + k: v
                for k, v in set_metrics(r["ranking"][:5], label["files"]).items()
            },
            **{
                "function_set5_" + k: v
                for k, v in set_metrics(
                    r.get("function_ranking", [])[:5], label["functions"]
                ).items()
            },
            input_tokens=r["input_tokens"],
            output_tokens=r["output_tokens"],
            tokens=r["input_tokens"] + r["output_tokens"],
            seconds=r["seconds"],
            resets=r.get("resets", 0),
            probe_count=r.get("probe_count", 0),
            duplicate_probes=r.get("duplicate_probes", 0),
            hypothesis_switches=r.get("hypothesis_switches"),
            status=r.get("status", r.get("stop_reason")),
            truncated_calls=sum(t["shown_chars"] < t["original_chars"] for t in r.get("trace", [])),
            calls=len(r.get("trace", [])) or None,
            ranking=json.dumps(r["ranking"]),
            function_ranking=json.dumps(r.get("function_ranking", [])),
        )
        if row["tokens"] > (48000 if phase == "mechanism" else 16000):
            raise ValueError("Budget violation")
        rows.append(row)


for p in sorted(Path("artifacts/baselines").glob("*__*.jsonl")):
    phase, model, variant = p.stem.split("__")
    labels = (
        Path("artifacts/baselines/fresh-data/labels.jsonl")
        if phase == "fresh"
        else Path(f"artifacts/local/data/{phase}/labels.jsonl")
    )
    collect(p, phase, model, variant, labels)
for p in sorted(Path("artifacts/baselines/fulltree").glob("*.jsonl")):
    model, variant = p.stem.split("__")
    collect(
        p,
        "fresh_sensitivity",
        model,
        variant.replace("_adapted", "_fulltree"),
        Path("artifacts/baselines/fresh-data/labels.jsonl"),
    )
for phase in ["dev", "test", "fresh", "mechanism"]:
    base = (
        Path(f"artifacts/local/validated-{phase}")
        if phase in ["dev", "test"]
        else Path(f"artifacts/baselines/{phase}")
    )
    labels = (
        Path("artifacts/local/data/dev/labels.jsonl")
        if phase == "mechanism"
        else Path("artifacts/baselines/fresh-data/labels.jsonl")
        if phase == "fresh"
        else Path(f"artifacts/local/data/{phase}/labels.jsonl")
    )
    for p in sorted(base.glob("*/predictions.jsonl")):
        model, variant = p.parent.name.split("__")
        collect(p, phase, model, variant, labels)


def write_csv(path, data):
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


write_csv(OUT / "case_scores.csv", rows)
groups = defaultdict(list)
for row in rows:
    groups[row["phase"], row["model"], row["variant"]].append(row)
summary = []
for (phase, model, variant), values in sorted(groups.items()):
    summary.append(
        dict(
            phase=phase,
            model=model,
            variant=variant,
            cases=len(values),
            file_eligible=sum(bool(r["file_eligible"]) for r in values),
            function_eligible=sum(bool(r["function_eligible"]) for r in values),
            **{
                k: mean(r[k] for r in values if r[k] is not None)
                if any(r[k] is not None for r in values)
                else None
                for k in [
                    "file_top1",
                    "file_top5",
                    "file_top10",
                    "file_mrr",
                    "file_recall10",
                    "function_top1",
                    "function_top5",
                    "function_top10",
                    "function_mrr",
                    "function_recall10",
                    "tokens",
                    "input_tokens",
                    "output_tokens",
                    "seconds",
                    "resets",
                    "probe_count",
                    "duplicate_probes",
                    "truncated_calls",
                ]
            },
            median_seconds=median(r["seconds"] for r in values),
        )
    )
write_csv(OUT / "summary.csv", summary)
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
lines = [
    "# Measured upstream-adaptation comparisons",
    "",
    "Patch-change proxy labels; equal 16,000-token ceilings, one seed; mechanism diagnostic uses 48,000. Models and source snapshots match, but algorithms select different context and external adaptations use free-text decoding. Latency timer boundaries differ: external adaptations exclude initial indexing, MORPH-FL includes analysis; no end-to-end speed comparison is valid.",
    "",
]
for phase in ["test", "fresh", "fresh_sensitivity", "dev", "mechanism"]:
    lines += [
        f"## {phase}",
        "",
        "| Model | Method | n | File Top-1 | File Top-5 | MRR | Function Top-1 | Tokens/case | Median seconds | Resets/case |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary:
        if r["phase"] != phase:
            continue

        def score(k):
            return f"{100 * r[k]:.1f}%" if r[k] is not None else "N/A"

        lines.append(
            f"| {r['model']} | {r['variant']} | {r['cases']} | {score('file_top1')} | {score('file_top5')} | {r['file_mrr']:.3f} | {score('function_top1')} | {r['tokens']:,.0f} | {r['median_seconds']:.1f} | {r['resets']:.1f} |"
        )
    lines += [""]
(OUT / "report.md").write_text("\n".join(lines) + "\n")
print("Scored", len(rows), "case-runs", flush=True)

paired = []
for phase in ["test", "fresh"]:
    for model in sorted({r["model"] for r in rows}):
        current = {
            r["instance_id"]: r
            for r in rows
            if r["phase"] == phase and r["model"] == model and r["variant"] == "morph"
        }
        for variant in ["agentless_adapted", "rgfl_adapted", "stateless_summary", "bm25"]:
            other = {
                r["instance_id"]: r
                for r in rows
                if r["phase"] == phase and r["model"] == model and r["variant"] == variant
            }
            shared = sorted(current.keys() & other.keys())
            eligible = [
                i for i in shared if current[i]["file_eligible"] and other[i]["file_eligible"]
            ]
            if not eligible:
                continue
            paired.append(
                dict(
                    phase=phase,
                    model=model,
                    against=variant,
                    cases=len(eligible),
                    morph_only_correct=sum(
                        current[i]["file_top1"] > other[i]["file_top1"] for i in eligible
                    ),
                    baseline_only_correct=sum(
                        current[i]["file_top1"] < other[i]["file_top1"] for i in eligible
                    ),
                    both_correct=sum(
                        current[i]["file_top1"] == other[i]["file_top1"] == 1 for i in eligible
                    ),
                    both_wrong=sum(
                        current[i]["file_top1"] == other[i]["file_top1"] == 0 for i in eligible
                    ),
                )
            )
if paired:
    write_csv(OUT / "paired.csv", paired)
