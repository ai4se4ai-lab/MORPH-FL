"""Evaluator-only mapping of patch edits to pre-fix source elements.

These are change-location proxies requiring manual root-cause review. This
module is never imported by the localization controller or model backend.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


def patch_labels(patch: str, snapshot: Path) -> dict:
    changed: dict[str, set[int]] = {}
    exclusions = []
    current = None
    old_line = 0
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            current = None
        elif line.startswith("--- a/"):
            current = line[6:]
            parts = Path(current).parts
            if (
                not current.endswith(".py")
                or {"test", "tests"}.intersection(parts)
                or Path(current).name.startswith("test_")
            ):
                current = None
            elif not (snapshot / current).resolve().is_relative_to(snapshot.resolve()):
                raise ValueError("Patch path escapes snapshot")
        elif line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", line)
            if match:
                old_line = int(match.group(1))
        elif current:
            if line.startswith("-") and not line.startswith("---"):
                changed.setdefault(current, set()).add(old_line)
                old_line += 1
            elif line.startswith("+") and not line.startswith("+++"):
                changed.setdefault(current, set()).add(max(1, old_line))
            elif line.startswith(" "):
                old_line += 1
    functions = []
    files = []
    for path, lines in changed.items():
        source = snapshot / path
        if not source.is_file():
            exclusions.append(dict(path=path, reason="No pre-fix source file"))
            continue
        files.append(path)
        try:
            tree = ast.parse(source.read_text(errors="replace"))
        except SyntaxError:
            exclusions.append(dict(path=path, reason="Pre-fix AST could not be parsed"))
            continue
        symbols = []

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.scope = []

            def visit_ClassDef(self, node):
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()

            def visit_FunctionDef(self, node):
                self.scope.append(node.name)
                symbols.append((node.lineno, node.end_lineno, ".".join(self.scope)))
                self.generic_visit(node)
                self.scope.pop()

            visit_AsyncFunctionDef = visit_FunctionDef

        Visitor().visit(tree)
        for line in lines:
            enclosing = [s for s in symbols if s[0] <= line <= s[1]]
            if enclosing:
                function = min(enclosing, key=lambda s: s[1] - s[0])[2]
                functions.append(f"{path}::{function}")
    return dict(
        files=sorted(files),
        functions=sorted(set(functions)),
        exclusions=exclusions,
        status="patch_proxy_requires_manual_review",
    )
