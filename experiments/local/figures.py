"""Standalone pilot figures; always label proxy/coverage limitations."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path("experiments/local/results")
out = root / "figures"
out.mkdir(exist_ok=True)
rows = list(csv.DictReader((root / "summary.csv").open()))
selected = [
    row
    for row in rows
    if row["run"] == "validated-test" and row["variant"] in {"rerank", "stateless_summary", "morph"}
]
first = next(row for row in rows if row["run"] == "validated-test" and row["variant"] == "bm25")
selected = [first] + selected
labels = [
    (
        "BM25"
        if row["variant"] == "bm25"
        else ("7B" if "7b" in row["model"] else "30B")
        + " · "
        + {
            "rerank": "single-round shortlist",
            "stateless_summary": "stateless summary",
            "morph": "MORPH-FL",
        }[row["variant"]]
    )
    for row in selected
]
fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
values = [float(row["top1"]) for row in selected]
colors = [
    "#8A8F98" if row["variant"] == "bm25" else ("#386A96" if "7b" in row["model"] else "#B46B39")
    for row in selected
]
ax.barh(labels, values, color=colors, height=0.65)
ax.invert_yaxis()
ax.set_xlim(0, 1.17)
for i, (value, row) in enumerate(zip(values, selected)):
    ax.text(
        value + 0.02, i, f"{round(value * int(row['eligible']))}/{row['eligible']}", va="center"
    )
ax.set_xlabel("File Top-1 on patch-change proxies")
ax.set_title("Local held-out pilot: three cases, one seed")
ax.set_xticks([0, 1 / 3, 2 / 3, 1], ["0%", "33%", "67%", "100%"])
ax.spines[["top", "right"]].set_visible(False)
fig.savefig(out / "held_out_top1.png", dpi=180)
fig.savefig(out / "held_out_top1.pdf")
plt.close(fig)
storage = json.loads((root / "storage_check.json").read_text())
fig, ax = plt.subplots(figsize=(6, 3.7), layout="constrained")
values = [storage["before_bytes"] / 2**20, storage["after_bytes"] / 2**20]
ax.bar(["Repeated graphs", "Lossless shared graphs"], values, color=["#8A8F98", "#386A96"])
for i, value in enumerate(values):
    ax.text(i, value + 0.3, f"{value:.2f} MiB", ha="center")
ax.set_ylim(0, values[0] * 1.2)
ax.set_ylabel("Total output, including structural artifacts (MiB)")
ax.set_title(f"{storage['reduction']:.1%} smaller · three-case storage check")
ax.spines[["top", "right"]].set_visible(False)
fig.savefig(out / "storage.png", dpi=180)
fig.savefig(out / "storage.pdf")
plt.close(fig)
print(out)
