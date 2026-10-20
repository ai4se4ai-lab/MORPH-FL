"""Paired repository-cluster bootstrap; seeds averaged within case first."""

import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def paired_bootstrap(
    rows, left="morph", right="no_forgetting", metric="top1", samples=2000, seed=2026
):
    by_case = defaultdict(list)
    for row in rows:
        if row["variant"] in (left, right) and row.get(metric) not in ("", None):
            by_case[(row["repo"], row["instance_id"], row["variant"])].append(float(row[metric]))
    groups = defaultdict(list)
    for repo, iid, variant in by_case:
        if variant != left or (repo, iid, right) not in by_case:
            continue
        left_values, right_values = by_case[(repo, iid, left)], by_case[(repo, iid, right)]
        groups[repo].append(
            sum(left_values) / len(left_values) - sum(right_values) / len(right_values)
        )
    if not groups:
        raise ValueError("No paired cases")
    repos = sorted(groups)

    def average(selected):
        values = [x for repo in selected for x in groups[repo]]
        return sum(values) / len(values)

    rng = random.Random(seed)
    draws = sorted(average(rng.choices(repos, k=len(repos))) for _ in range(samples))
    return dict(
        left=left,
        right=right,
        metric=metric,
        delta=average(repos),
        ci95=[draws[int(samples * 0.025)], draws[min(samples - 1, int(samples * 0.975))]],
        repositories=len(repos),
        paired_cases=sum(map(len, groups.values())),
        inference="descriptive clustered interval; no multiplicity-adjusted significance claim",
    )


def analyze(results, out):
    rows = []
    for path in Path(results).glob("scores/*.csv"):
        with path.open() as f:
            rows.extend(csv.DictReader(f))
    if not rows:
        raise ValueError("No scores found")
    reports = []
    for variant in sorted({r["variant"] for r in rows} - {"morph"}):
        try:
            reports.append(paired_bootstrap(rows, right=variant))
        except ValueError:
            continue
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            dict(
                comparisons=reports,
                rows=len(rows),
                label_warning="Unreviewed patch-proxy labels are exploratory only",
            ),
            indent=2,
        )
        + "\n"
    )


def holm_adjust(pvalues):
    """Holm step-down family-wise adjustment for a declared comparison family."""
    if any(not 0 <= p <= 1 for p in pvalues):
        raise ValueError("Invalid p-value")
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted = [0.0] * len(pvalues)
    running = 0.0
    for position, index in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - position) * pvalues[index]))
        adjusted[index] = running
    return adjusted


def clustered_sign_flip(repository_differences, samples=10000, seed=2026):
    """Two-sided cluster-level randomization under the sign-exchangeability null.

    Requires independent repository clusters. With few repositories, p-values
    have coarse resolution and cannot establish broad generality.
    """
    import itertools

    values = list(repository_differences)
    if not values:
        raise ValueError("No repository differences")
    observed = abs(sum(values) / len(values))
    rng = random.Random(seed)
    exact = len(values) <= 16
    signs = (
        itertools.product((-1, 1), repeat=len(values))
        if exact
        else ([rng.choice((-1, 1)) for _ in values] for _ in range(samples))
    )
    count = total = 0
    for trial in signs:
        statistic = abs(sum(v * s for v, s in zip(values, trial)) / len(values))
        count += statistic >= observed - 1e-12
        total += 1
    return count / total if exact else (count + 1) / (total + 1)
