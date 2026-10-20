"""Promote complete non-smoke measurements into the manuscript; refuse partial data.

Run locally after collecting the project's full result tree. No model calls.
Historical exploratory results remain in the manuscript for comparison/provenance.
"""

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


def tex(value):
    return (
        str(value)
        .replace("\\", r"\textbackslash{}")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("#", r"\#")
    )


def require_complete(results):
    report = json.loads((results / "analysis/completeness.json").read_text())
    if report.get("smoke") or not report.get("complete"):
        raise ValueError("Paper promotion requires a complete, non-smoke evaluation")
    if report["planned"] != report["observed"]:
        raise ValueError("Planned/observed counts differ")
    if set(report.get("benchmark_sizes", {}).values()) != {300, 500}:
        raise ValueError("Full Lite/Verified benchmark size verification failed")
    return report


def update(results, paper):
    results = Path(results)
    paper = Path(paper)
    status = require_complete(results)
    with (results / "analysis/summary.csv").open() as f:
        rows = list(csv.DictReader(f))
    main = [r for r in rows if r["track"] == "main"]
    # Require every pinned model, six workflow cells per benchmark, and three seeds.
    pinned_models = json.loads((Path(__file__).parent / "pins.json").read_text())["models"]
    expected_models = {m["id"] for m in pinned_models}
    for benchmark in status["benchmark_sizes"]:
        subset = [r for r in main if r["benchmark"] == benchmark]
        if {r["model"] for r in subset} != expected_models or len(subset) != 6 * len(expected_models):
            raise ValueError("Main table is missing model/method cells")
        if any(
            int(r["observed_seeds"]) != 3
            or int(r["unique_cases"]) != status["benchmark_sizes"][benchmark]
            for r in subset
        ):
            raise ValueError("Main comparison missing full seed/subject coverage")
    generated = paper / "tables/full"
    generated.mkdir(parents=True, exist_ok=True)
    figs = paper / "figures/full"
    figs.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\subsection{Full-Benchmark Extension}",
        r"\label{sec:full-extension}",
        "A separately frozen extension evaluates all 300 SWE-bench Lite and 500 Verified instances, deduplicating shared instance IDs during execution. "
        + f"The union contains {status['unique_subjects']} issues, with {status['overlap']} shared issues. "
        + "Each benchmark is summarized separately; their overlapping outcomes are not independent replications. Five BF16 model families and three seeds replace the exploratory quantized single-seed settings. The primary ceiling is 32,000 input-plus-output tokens with up to 16 rounds. This extension retains static observations and unreviewed patch-change proxies; it does not establish causal labels, calibrated confidence, or dynamic probe validity.",
        "Eight component controls, measured budget levels, disclosed misdirection and policy sensitivity use a fixed report-blind, repository-balanced sample of 100 union issues. External Agentless/RGFL results remain restricted component adaptations, with a 12,000-token tree allowance selected before these outcomes. All planned record counts are present; that completeness is distinct from favorable outcomes.",
    ]
    for number, benchmark in enumerate(sorted(status["benchmark_sizes"])):
        table = [
            r"\begin{table*}[t]",
            r"\centering\footnotesize",
            r"\caption{Full "
            + tex(benchmark)
            + " extension. Means over three seeds; F@1/F@5 are file accuracy, U@1 exact-function accuracy. Targets are unreviewed patch proxies. No population superiority follows from the largest cell mean.}",
            r"\label{tab:full-" + str(number) + "}",
            r"\begin{tabular}{llrrrrr}",
            r"\toprule",
            r"Model & Workflow & F@1 & F@5 & MRR & U@1 & Mean tokens \\",
            r"\midrule",
        ]
        for row in sorted(
            [r for r in main if r["benchmark"] == benchmark],
            key=lambda r: (r["model"], r["variant"]),
        ):
            values = [tex(row["model"].split("/")[-1]), tex(row["variant"])]
            values += [
                f"{float(row[k]):.3f}" if row[k] else "--"
                for k in ["top1", "top5", "mrr", "function_top1"]
            ]
            values += [f"{float(row['tokens']):,.0f}"]
            table.append(" & ".join(values) + r" \\")
        table += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
        name = f"main-{number}.tex"
        (generated / name).write_text("\n".join(table) + "\n")
        lines.append(r"\input{tables/full/" + name + "}")
        plot = results / "analysis" / (benchmark + "-topk.pdf")
        if plot.exists():
            name = "topk-" + str(number) + ".pdf"
            shutil.copy2(plot, figs / name)
            lines += [
                r"\begin{figure*}[t]",
                r"\centering\includegraphics[width=.95\textwidth]{figures/full/" + name + "}",
                r"\caption{Measured full "
                + tex(benchmark)
                + " file Top-$k$ for MORPH-FL model configurations. Joined rank cutoffs are visual guides, not independent trials or budget points.}",
                r"\end{figure*}",
            ]
    for stem in ["heatmap", "budget_curves"]:
        source = results / "analysis" / (stem + ".pdf")
        if source.exists():
            shutil.copy2(source, figs / source.name)
            lines += [
                r"\begin{figure*}[t]",
                r"\centering\includegraphics[width=.95\textwidth]{figures/full/"
                + source.name
                + "}",
                r"\caption{Measured "
                + tex(stem.replace("_", " "))
                + r" for the frozen full-study design. Interpret alongside the paired intervals, coverage and evidence-scope limits.}",
                r"\end{figure*}",
            ]
    lines += [
        "The extension exports repository-cluster paired intervals after averaging seeds within cases. Misdirection recovery counts require a proxy-wrong clue and evidence that the first valid leader followed that clue; case/seed trajectories remain available. Exact numerical claims about the contribution of resetting must be assessed against observed reset incidence, paired accuracy, costs and these conditional denominators, rather than inferred from an unconditional table difference."
    ]
    (paper / "sections/full_results.tex").write_text("\n\n".join(lines) + "\n")
    evaluation = paper / "sections/evaluation.tex"
    text = evaluation.read_text()
    include = r"\input{sections/full_results}"
    if include not in text:
        evaluation.write_text(text + "\n" + include + "\n")
    receipt = dict(
        completeness=status,
        input_sha256=hashlib.sha256((results / "analysis/summary.csv").read_bytes()).hexdigest(),
        status="Generated full-results subsection; narrative/abstract conclusions require assessment of actual measurements before publication",
    )
    (paper / "full_results_provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--paper", type=Path, default=Path("docs/TSE"))
    a = p.parse_args()
    update(a.results, a.paper)


def export_bundle(results, template):
    """Cluster-side reviewable TeX export, without touching the historical paper."""
    results = Path(results)
    status = json.loads((results / "analysis/completeness.json").read_text())
    receipt = results / "paper_export.json"
    if status.get("smoke") or not status.get("complete"):
        receipt.write_text(
            json.dumps(
                dict(
                    state="deferred",
                    reason="smoke or incomplete evaluation; original paper unchanged",
                )
            )
            + "\n"
        )
        return
    destination = results / "paper"
    shutil.copytree(
        template,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.aux", "*.log", "*.out", "*.zip", "*.blg", "__pycache__"),
    )
    update(results, destination)
    receipt.write_text(
        json.dumps(
            dict(
                state="tex_exported_for_review",
                paper=str(destination),
                note="Outcome-level abstract/discussion revision and PDF review remain necessary",
            )
        )
        + "\n"
    )
