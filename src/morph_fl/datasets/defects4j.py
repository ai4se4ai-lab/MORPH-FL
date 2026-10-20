"""Defects4J public-case adapter for explicitly curated issue reports.

This adapter exports buggy snapshots without fixed revisions or trigger-test
metadata. Localization requires a registered analyzer for the source language;
Python is the built-in analyzer, so Java cases must not silently run through it.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def export_cases(manifest: Path, destination: Path, executable="defects4j") -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    cases = []
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        project, bug = str(row["project"]), str(row["bug"])
        if (
            not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", project)
            or not bug.isdigit()
            or not row.get("report")
        ):
            raise ValueError(
                "Defects4J requires a valid project, bug ID, and curated pre-fix issue report"
            )
        root = destination / f"{project}-{bug}b"
        if root.exists():
            raise ValueError("Refusing to reuse an unverified existing buggy checkout")
        subprocess.run(
            [executable, "checkout", "-p", project, "-v", bug + "b", "-w", str(root)], check=True
        )
        revision = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        # Repository history is evaluator-only. Expose a clean directory snapshot.
        import shutil

        public = destination / f"{project}-{bug}-public"
        shutil.copytree(
            root, public, ignore=shutil.ignore_patterns(".git", ".svn", ".defects4j.config")
        )
        cases.append(
            dict(
                instance_id=f"{project}-{bug}",
                repo=f"defects4j/{project}",
                revision=revision,
                root=str(public.resolve()),
                report=row["report"],
                language="java",
            )
        )
    output = destination / "cases.jsonl"
    output.write_text("".join(json.dumps(c) + "\n" for c in cases))
    return output
