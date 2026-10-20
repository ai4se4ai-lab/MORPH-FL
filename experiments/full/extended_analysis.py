"""Predeclared comparisons and matched-subject budget curves; no model calls."""

import csv
import json
from collections import defaultdict

from experiments.full.suite import BUDGET_CORE, CORE, selected_cases
from morph_fl.evaluation.statistics import clustered_sign_flip, holm_adjust


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def extend(scored, recovery, membership, cases, out, smoke, complete):
    import matplotlib.pyplot as plt

    # File Top-1 primary family: 5 comparators x 5 model families x 2 benchmarks.
    tests = []
    for benchmark, ids in membership.items():
        for model in sorted({r["model_id"] for r in scored if r["track"] == "main"}):
            subset = [
                r
                for r in scored
                if r["track"] == "main"
                and r["model_id"] == model
                and r["instance_id"] in ids
                and r["top1"] != ""
            ]
            for comparator in CORE[1:]:
                per_case = defaultdict(list)
                for r in subset:
                    if r["variant"] in {"morph", comparator}:
                        per_case[(r["repo"], r["instance_id"], r["variant"])].append(
                            float(r["top1"])
                        )
                repo_sums = defaultdict(float)
                n = 0
                total = 0.0
                for repo, iid, variant in per_case:
                    if variant != "morph" or (repo, iid, comparator) not in per_case:
                        continue
                    a = per_case[(repo, iid, "morph")]
                    b = per_case[(repo, iid, comparator)]
                    delta = sum(a) / len(a) - sum(b) / len(b)
                    repo_sums[repo] += delta
                    n += 1
                    total += delta
                if repo_sums:
                    tests.append(
                        dict(
                            benchmark=benchmark,
                            model=model,
                            comparator=comparator,
                            paired_cases=n,
                            repositories=len(repo_sums),
                            delta=total / n,
                            p=clustered_sign_flip(repo_sums.values()),
                            holm_p=None,
                            confirmatory=complete and not smoke,
                        )
                    )
    if tests:
        adjusted = holm_adjust([r["p"] for r in tests])
        for r, p in zip(tests, adjusted):
            r["holm_p"] = p
    (out / "primary_comparisons.json").write_text(
        json.dumps(
            dict(
                family="File Top-1: all model x benchmark x five-comparator comparisons; no unadjusted significance claims",
                assumptions="Independent repository clusters, sign exchangeability; public benchmark overlap disclosed",
                comparisons=tests,
                complete=complete,
            ),
            indent=2,
        )
        + "\n"
    )
    # Reused main 32k point is restricted to exactly the same fixed side-study subjects.
    subjects = {r["instance_id"] for r in selected_cases(cases, "budgets", smoke)}
    groups = defaultdict(list)
    for row in scored:
        if row["variant"] not in BUDGET_CORE or row["instance_id"] not in subjects:
            continue
        if row["track"] != "budgets" and not (row["track"] == "main" and row["budget"] == "32000"):
            continue
        for benchmark, ids in membership.items():
            if row["instance_id"] in ids:
                groups[(benchmark, row["model_id"], row["variant"], int(row["budget"]))].append(row)
    points = []
    for (benchmark, model, variant, budget), rr in sorted(groups.items()):
        valid = [r for r in rr if r["top1"] != ""]
        points.append(
            dict(
                benchmark=benchmark,
                model=model,
                variant=variant,
                budget=budget,
                unique_cases=len({r["instance_id"] for r in rr}),
                case_seed_records=len(rr),
                file_top1=sum(float(r["top1"]) for r in valid) / len(valid) if valid else None,
                mean_actual_tokens=sum(float(r["tokens"]) for r in rr) / len(rr),
            )
        )
    write_csv(out / "budget_points.csv", points)
    if points:
        models = sorted({r["model"] for r in points})
        fig, axes = plt.subplots(
            len(models),
            len(membership),
            figsize=(10, max(3, len(models) * 2.5)),
            squeeze=False,
            sharey=True,
        )
        for i, model in enumerate(models):
            for j, benchmark in enumerate(membership):
                ax = axes[i, j]
                for variant in BUDGET_CORE:
                    pp = [
                        r
                        for r in points
                        if r["model"] == model
                        and r["benchmark"] == benchmark
                        and r["variant"] == variant
                    ]
                    if pp:
                        ax.plot(
                            [r["budget"] / 1000 for r in pp],
                            [r["file_top1"] for r in pp],
                            "-o",
                            label=variant,
                            markersize=3,
                        )
                ax.set_title(model.split("/")[-1] + " / " + benchmark, fontsize=7)
                ax.set(xlabel="Token ceiling (thousands)", ylabel="File Top-1", ylim=(0, 1))
                ax.legend(fontsize=5)
        fig.suptitle(
            "Matched-side-subject budget study"
            + (" (SMOKE)" if smoke else (" (partial)" if not complete else "")),
            fontsize=10,
        )
        fig.tight_layout()
        fig.savefig(out / "budget_curves.pdf")
        plt.close(fig)
    recovery_groups = defaultdict(list)
    for r in recovery:
        recovery_groups[(r["model"], r["variant"])].append(r)
    summaries = []
    for (model, variant), rr in sorted(recovery_groups.items()):
        eligible = [r for r in rr if r["wrong_proxy_lead"] and r["first_valid_leader_follows"]]
        summaries.append(
            dict(
                model=model,
                variant=variant,
                all_case_seed_trajectories=len(rr),
                unique_cases=len({r["instance_id"] for r in rr}),
                wrong_clue_trajectories=sum(r["wrong_proxy_lead"] for r in rr),
                followed_wrong_trajectories=len(eligible),
                recovered_trajectories=sum(r["proxy_recovered"] for r in eligible),
                conditional_recovery=sum(r["proxy_recovered"] for r in eligible) / len(eligible)
                if eligible
                else None,
            )
        )
    write_csv(out / "recovery_summary.csv", summaries)
