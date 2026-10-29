"""BM25 candidate retrieval and conservative Python structural extraction."""

import ast
import math
import re
from collections import Counter


def tokens(text):
    return re.findall(r"[a-z][a-z0-9_]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", text).lower())


def index(root):
    files, edges, symbols = {}, [], []
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        if (
            p.is_symlink()
            or any(
                x in {".git", ".venv", "venv", "__pycache__", "tests", "test"}
                for x in p.relative_to(root).parts
            )
            or p.name.startswith("test_")
        ):
            continue
        text = p.read_text(errors="replace")
        files[rel] = text
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append(
                    dict(path=rel, name=node.name, line=node.lineno, end=node.end_lineno)
                )
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = (
                    [node.module]
                    if isinstance(node, ast.ImportFrom)
                    else [a.name for a in node.names]
                )
                for module in modules:
                    if module:
                        edges.append(
                            dict(
                                source=rel,
                                target=module.replace(".", "/") + ".py",
                                type="imports",
                                status="derived",
                                line=node.lineno,
                            )
                        )
    return files, edges, symbols


def bm25(report, files):
    docs = {p: Counter(tokens(p + " " + s)) for p, s in files.items()}
    n = len(docs)
    avg = sum(map(lambda c: sum(c.values()), docs.values())) / max(n, 1)
    query = set(tokens(report))
    df = {t: sum(t in d for d in docs.values()) for t in query}
    scores = {}
    for p, d in docs.items():
        length = sum(d.values())
        scores[p] = sum(
            math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            * d[t]
            * 2.5
            / (d[t] + 1.5 * (0.25 + 0.75 * length / max(avg, 1)))
            for t in query
            if d[t]
        )
    return sorted(scores, key=lambda p: (-scores[p], p))
