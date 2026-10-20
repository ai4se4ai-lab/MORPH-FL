"""Standalone publication-style pilot plots; never pool development with fresh cases."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

base = Path("experiments/baselines/results")
rows = list(csv.DictReader((base / "summary.csv").open()))
variants = [
    "bm25",
    "agentless_adapted",
    "agentless_fulltree",
    "rgfl_adapted",
    "rgfl_fulltree",
    "stateless_summary",
    "morph",
]
labels = ["BM25", "Agentless*", "Agentless†", "RGFL*", "RGFL†", "Stateless", "MORPH-FL"]
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for ax, model in zip(axes, ["qwen2.5-coder_7b", "qwen3-coder_30b"]):
    selected = {
        r["variant"]: r
        for r in rows
        if r["phase"] in {"fresh", "fresh_sensitivity"} and r["model"] == model
    }
    values = [100 * float(selected[v]["file_top1"]) for v in variants]
    ax.bar(
        range(len(variants)),
        values,
        color=["#999999", "#3977ac", "#3977ac", "#59a89c", "#59a89c", "#c59a43", "#965a77"],
    )
    ax.set_xticks(range(len(variants)), labels, rotation=25, ha="right")
    ax.set_title(model.replace("_", " "))
    ax.set_ylim(0, 110)
    for i, value in enumerate(values):
        ax.text(i, value + 2, f"{round(value * 6 / 100)}/6", ha="center")
axes[0].set_ylabel("File Top-1 (%)")
fig.suptitle(
    "Six fresh SWE-bench Lite issues • one seed • 16,000-token ceiling\n*Initial upstream adaptation; †post-hoc larger-tree control; patch-change proxy labels",
    fontsize=11,
)
fig.tight_layout()
for suffix in ["png", "pdf"]:
    fig.savefig(base / f"fresh_comparison.{suffix}", dpi=180, bbox_inches="tight")
