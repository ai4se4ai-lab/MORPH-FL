"""Prepare public issue inputs separately from patch-derived evaluation labels."""

import hashlib
import json
import re
import subprocess
from pathlib import Path


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True).strip()


def prepare(out, limit=300, revision=None):
    from datasets import load_dataset

    if not revision:
        raise ValueError("A pinned Hugging Face dataset revision is required")
    data = load_dataset("princeton-nlp/SWE-bench_Lite", split="test", revision=revision)
    return prepare_rows(list(data)[:limit], out, revision)


def prepare_rows(rows, out, revision, split="test"):
    """Export explicitly selected rows without importing the datasets runtime."""
    if not revision:
        raise ValueError("Pinned dataset revision required")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cases, labels = [], []
    for row in rows:
        iid, repo, commit = row["instance_id"], row["repo"], row["base_commit"]
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]+", iid)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or not re.fullmatch(r"[0-9a-f]{40}", commit)
        ):
            raise ValueError("Invalid repository or revision")
        checkout = out / "repos" / iid
        if not checkout.exists():
            checkout.parent.mkdir(exist_ok=True)
            checkout.mkdir()
            subprocess.run(["git", "init", str(checkout)], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(checkout),
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{repo}.git",
                ],
                check=True,
            )
        subprocess.run(
            ["git", "-C", str(checkout), "fetch", "--depth=1", "origin", commit], check=True
        )
        subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", commit], check=True)
        if git("-C", checkout, "rev-parse", "HEAD") != commit:
            raise ValueError("Incorrect pre-fix checkout")
        # Remove Git history from the agent-visible snapshot. No gold tests or patches copied.
        snapshot = out / "snapshots" / iid
        if not snapshot.exists():
            import shutil

            shutil.copytree(
                checkout, snapshot, symlinks=True, ignore=shutil.ignore_patterns(".git")
            )
        cases.append(
            dict(
                instance_id=iid,
                repo=repo,
                revision=commit,
                root=str(snapshot.resolve()),
                report=row["problem_statement"],
            )
        )
        from .labels import patch_labels

        labels.append(
            dict(
                instance_id=iid,
                revision=commit,
                **patch_labels(row["patch"], snapshot),
                dataset_revision=revision,
                patch_sha256=hashlib.sha256(row["patch"].encode()).hexdigest(),
            )
        )
    for name, rows in [("cases", cases), ("labels", labels)]:
        (out / f"{name}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (out / "manifest.json").write_text(
        json.dumps(
            dict(
                dataset="princeton-nlp/SWE-bench_Lite",
                revision=revision,
                split=split,
                cases=len(cases),
                ground_truth="unreviewed patch proxy",
            ),
            indent=2,
        )
    )
