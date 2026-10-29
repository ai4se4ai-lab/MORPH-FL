"""Post-hoc evaluator: was a gold proxy file visible in the truncated tree?"""

import csv
import json
from pathlib import Path

from morph_fl.application import read_rows

rows = []
for path in sorted(
    list(Path("artifacts/baselines").glob("fresh__*.jsonl"))
    + list(Path("artifacts/baselines/fulltree").glob("*.jsonl"))
):
    labels = {r["instance_id"]: r for r in read_rows("artifacts/baselines/fresh-data/labels.jsonl")}
    for r in read_rows(path):
        trace = next(t for t in r["trace"] if t["stage"] == "file_selection")
        content = (
            trace["prompt"][0]["content"]
            .split("### Repository Structure ###", 1)[1]
            .split("###", 1)[0]
        )
        stack = []
        visible = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            depth = (len(line) - len(line.lstrip())) // 4
            stack = stack[:depth]
            if stripped.endswith("/"):
                stack.append(stripped[:-1])
            elif stripped.endswith(".py"):
                visible.append("/".join(stack + [stripped]))
        gold = set(labels[r["instance_id"]]["files"])
        rows.append(
            dict(
                model=r["model"],
                variant=r["variant"],
                instance_id=r["instance_id"],
                tree_truncated=trace["shown_chars"] < trace["original_chars"],
                original_chars=trace["original_chars"],
                shown_chars=trace["shown_chars"],
                visible_files=len(visible),
                any_gold_visible=bool(gold & set(visible)),
                all_gold_visible=gold <= set(visible),
                any_gold_selected=bool(gold & set(r["ranking"])),
                file_top1=bool(r["ranking"] and r["ranking"][0] in gold),
            )
        )
out = Path("experiments/baselines/results/visibility.csv")
with out.open("w") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps(rows, indent=2))
