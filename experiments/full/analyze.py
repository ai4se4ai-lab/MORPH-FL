"""Completeness-aware RQ summaries from full-study outputs, without model calls."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from experiments.full.suite import CORE, jobs_for, selected_cases
from morph_fl.application import read_rows
from morph_fl.domain.models import identity
from morph_fl.evaluation.statistics import paired_bootstrap


def numeric(values):
    values = [float(x) for x in values if x not in ("", None)]
    return sum(values) / len(values) if values else None


def analyze(results, smoke=False):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    results = Path(results)
    out = results / "analysis"
    out.mkdir(exist_ok=True)
    membership = json.loads((results / "data/membership.json").read_text())
    manifest = json.loads((results / "data/manifest.json").read_text())
    pins = json.loads(Path("experiments/full/pins.json").read_text())
    models = 1 if smoke else len(pins["models"])
    seeds = 1 if smoke else 3
    cases = read_rows(results / "data/cases.jsonl")
    planned = {
        track: len(selected_cases(cases, track, smoke))
        * len(jobs_for(track, smoke))
        * models
        * seeds
        for track in ["main", "ablations", "budgets", "misdirection", "policy"]
    }
    planned["retrieval"] = len(selected_cases(cases, "retrieval", smoke)) * 2
    records = []
    seen = set()
    verification = []
    for path in sorted((results / "predictions").glob("*.jsonl")):
        if path.name.startswith("preflight__"):
            continue
        for row in read_rows(path):
            key = (
                row["track"],
                row["model_id"],
                row["seed"],
                row["instance_id"],
                row["variant"],
                row["budget"],
                row.get("window"),
            )
            if key in seen:
                raise ValueError("Duplicate experimental record")
            seen.add(key)
            brief = {
                k: row.get(k)
                for k in [
                    "track",
                    "model_id",
                    "seed",
                    "instance_id",
                    "variant",
                    "budget",
                    "window",
                    "initial_clue_path",
                ]
            }
            brief["ranking"] = row.get("ranking", [])[:1] if row["track"] == "misdirection" else []
            brief["audit"] = []
            if row["track"] == "misdirection":
                # Retain only recovery linkage, not full prompts/graphs for every record.
                for event in row.get("audit", []):
                    if event.get("type") == "round":
                        brief["audit"].append({"type": "round", "leader": event.get("leader")})
                    elif event.get("type") == "agent_response":
                        hypotheses = []
                        for hypothesis in event.get("response", {}).get("hypotheses", []):
                            if isinstance(hypothesis, dict):
                                hypotheses.append(
                                    {k: hypothesis.get(k) for k in ["path", "mechanism", "probe"]}
                                )
                        brief["audit"].append(
                            {"type": "agent_response", "response": {"hypotheses": hypotheses}}
                        )
            records.append(brief)
            ids = {e["id"] for e in row.get("observations", [])}
            for event in row.get("audit", []):
                if event.get("type") == "reset":
                    old = set(event["observations"])
                    if not old.issubset(ids):
                        raise ValueError("Reset observation retention failed")
                    verification.append(
                        dict(
                            instance_id=row["instance_id"],
                            model=row["model_id"],
                            track=row["track"],
                            step=event["step"],
                            retained=len(old),
                        )
                    )
    observed = {track: sum(r["track"] == track for r in records) for track in planned}
    expected_keys = set()
    for track in planned:
        subjects = selected_cases(cases, track, smoke)
        model_ids = (
            ["deterministic"]
            if track == "retrieval"
            else [p["id"] for p in pins["models"][:models]]
        )
        for model_id in model_ids:
            for seed in [1] if track == "retrieval" else range(1, seeds + 1):
                for case in subjects:
                    for variant, budget, window in jobs_for(track, smoke):
                        expected_keys.add(
                            (track, model_id, seed, case["instance_id"], variant, budget, window)
                        )
    unexpected = seen - expected_keys
    if unexpected:
        raise ValueError("Unplanned experimental keys present")
    missing = len(expected_keys - seen)
    complete = missing == 0 and all(observed[k] == v for k, v in planned.items())
    (out / "completeness.json").write_text(
        json.dumps(
            dict(
                planned=planned,
                observed=observed,
                complete=complete,
                missing_keys=missing,
                smoke=smoke,
                unique_subjects=len(cases),
                benchmark_sizes=manifest["benchmark_sizes"],
                overlap=manifest["overlap"],
            ),
            indent=2,
        )
        + "\n"
    )
    # Score as needed after partial/failing cells; denominators stay visible.
    from types import SimpleNamespace

    from experiments.full.suite import score

    score(SimpleNamespace(results=str(results), pattern="*.jsonl"))
    scored = []
    for path in sorted((results / "scores").glob("*.csv")):
        with path.open() as f:
            scored.extend(csv.DictReader(f))
    groups = defaultdict(list)
    for row in scored:
        for benchmark, ids in membership.items():
            if row["instance_id"] in ids:
                groups[
                    (
                        benchmark,
                        row["track"],
                        row["model_id"],
                        row["variant"],
                        row["budget"],
                        row["window"],
                    )
                ].append(row)
    summary = []
    metrics = [
        "top1",
        "top5",
        "top10",
        "mrr",
        "function_top1",
        "function_mrr",
        "tokens",
        "resets",
        "duplicate_probes",
        "probe_count",
        "hypothesis_switches",
        "mechanism_diversity",
        "end_to_end_seconds",
    ]
    for key, rows in sorted(groups.items()):
        row = dict(zip(["benchmark", "track", "model", "variant", "budget", "window"], key))
        row.update(
            case_seed_records=len(rows),
            unique_cases=len({r["instance_id"] for r in rows}),
            observed_seeds=len({r["seed"] for r in rows}),
            file_eligible=sum(r["eligible"] == "True" for r in rows),
            function_eligible=sum(r["function_eligible"] == "True" for r in rows),
        )
        row.update({metric: numeric([r.get(metric) for r in rows]) for metric in metrics})
        summary.append(row)
    if summary:
        with (out / "summary.csv").open("w") as f:
            w = csv.DictWriter(f, fieldnames=list(summary[0]))
            w.writeheader()
            w.writerows(summary)
    paired = []
    for benchmark in membership:
        for model in {r["model_id"] for r in scored}:
            subset = [
                r
                for r in scored
                if r["track"] == "main"
                and r["model_id"] == model
                and r["instance_id"] in membership[benchmark]
            ]
            for right in CORE[1:]:
                for metric in ["top1", "function_top1", "tokens"]:
                    try:
                        report = paired_bootstrap(subset, right=right, metric=metric)
                    except ValueError:
                        continue
                    paired.append(dict(benchmark=benchmark, model=model, **report))
    (out / "paired.json").write_text(json.dumps(paired, indent=2) + "\n")
    (out / "reset_retention.json").write_text(json.dumps(verification, indent=2) + "\n")
    labels = {r["instance_id"]: r for r in read_rows(results / "data/labels.jsonl")}
    recovery = []
    for row in records:
        if row["track"] != "misdirection":
            continue
        paths = {}
        for e in row.get("audit", []):
            if e.get("type") == "agent_response":
                for h in e.get("response", {}).get("hypotheses", []):
                    try:
                        paths[
                            identity(
                                (
                                    h["path"],
                                    h["mechanism"].casefold(),
                                    h["probe"].get("kind", "source_quote"),
                                )
                            )
                        ] = h["path"]
                    except (KeyError, TypeError, AttributeError):
                        pass
        leaders = [
            paths.get(e.get("leader")) for e in row.get("audit", []) if e.get("type") == "round"
        ]
        clue = row["initial_clue_path"]
        gold = set(labels[row["instance_id"]]["files"])
        followed = bool(leaders and leaders[0] == clue)
        wrong = bool(gold and clue and clue not in gold)
        recovered = bool(wrong and followed and row["ranking"] and row["ranking"][0] in gold)
        recovery.append(
            dict(
                instance_id=row["instance_id"],
                model=row["model_id"],
                variant=row["variant"],
                seed=row["seed"],
                clue=clue,
                wrong_proxy_lead=wrong,
                first_valid_leader_follows=followed,
                proxy_recovered=recovered,
            )
        )
    (out / "recovery.json").write_text(json.dumps(recovery, indent=2) + "\n")
    # Honest RQ coverage: no inferred calibration, causal validity, or human judgments.
    coverage = dict(
        RQ1="Full Lite/Verified file/function patch-proxy comparison; overlap reported, complete only when all planned records present",
        RQ2="Long-round memory/ablation, policy sensitivity and disclosed report-blind misdirection; following a wrong lead is checked before counting recovery",
        RQ3="Actual tokens, matched timing boundary for MORPH workflows, source observation scopes and multi-budget accuracy; calibration unavailable because confidence is null",
        missing=[
            "Reviewed causal labels",
            "Independent human causal-chain/diversity annotations",
            "Executable benchmark-container probes",
            "Complete upstream embedding/tool pipelines",
            "Java/BugsInPy ecosystems",
        ],
        complete=complete,
    )
    (out / "rq_coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
    lines = [
        "# Full evaluation results",
        "",
        f"**Status: {'COMPLETE' if complete else 'PARTIAL'}; smoke={smoke}.**",
        f"Unique subjects: {len(cases)}; benchmark overlap: {manifest['overlap']}. Benchmark summaries reuse overlapping issues and are not independent replications.",
        "",
        "| Track | Observed records | Planned records |",
        "|---|---:|---:|",
    ]
    lines += [f"| {k} | {observed[k]} | {planned[k]} |" for k in planned]
    lines += [
        "",
        "## Research-question coverage",
        json.dumps(coverage, indent=2),
        "",
        "No significance, calibration or causal-label claim is inferred from partial or static-only results. Seeds are averaged within cases before paired repository-cluster intervals.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    from experiments.full.extended_analysis import extend

    extend(scored, recovery, membership, cases, out, smoke, complete)
    # Vector plots from measured points. Missing/partial cells stay absent.
    if summary:
        for benchmark in membership:
            fig, ax = plt.subplots(figsize=(9, 4))
            for model in sorted({r["model"] for r in summary}):
                rr = [
                    r
                    for r in summary
                    if r["benchmark"] == benchmark
                    and r["track"] == "main"
                    and r["variant"] == "morph"
                ]
                rr = [r for r in rr if r["model"] == model]
                if rr:
                    r = rr[0]
                    ax.plot(
                        [1, 5, 10],
                        [r[k] for k in ["top1", "top5", "top10"]],
                        "-o",
                        label=model.split("/")[-1],
                    )
            ax.set(
                xlabel="Rank cutoff",
                ylabel="Patch-proxy file accuracy",
                ylim=(0, 1),
                title=benchmark + (" (SMOKE)" if smoke else (" (partial)" if not complete else "")),
            )
            ax.legend(fontsize=7)
            fig.tight_layout()
            fig.savefig(out / (benchmark + "-topk.pdf"))
            plt.close(fig)
        heat = [r for r in summary if r["track"] == "main"]
        keys = sorted({(r["model"], r["benchmark"]) for r in heat})
        data = np.full((len(keys), len(CORE)), np.nan)
        for i, key in enumerate(keys):
            for j, v in enumerate(CORE):
                match = [
                    r for r in heat if (r["model"], r["benchmark"]) == key and r["variant"] == v
                ]
                if match:
                    data[i, j] = match[0]["top1"]
        fig, ax = plt.subplots(figsize=(9, max(3, len(keys) * 0.55)))
        im = ax.imshow(data, vmin=0, vmax=1, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(CORE)), CORE, rotation=35, ha="right", fontsize=8)
        ax.set_yticks(range(len(keys)), [m.split("/")[-1] + " / " + b for m, b in keys], fontsize=7)
        fig.colorbar(im, ax=ax, label="File Top-1")
        fig.tight_layout()
        fig.savefig(out / "heatmap.pdf")
        plt.close(fig)
    print(
        json.dumps(
            dict(
                complete=complete,
                observed=observed,
                planned=planned,
                reset_events=len(verification),
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--smoke", type=int, default=0)
    a = p.parse_args()
    analyze(a.results, bool(a.smoke))
