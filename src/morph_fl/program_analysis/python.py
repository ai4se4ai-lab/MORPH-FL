"""Python AST symbols, imports, calls, reads/writes and local def-use.

Only syntactically resolved intra-module and explicit import calls are linked.
Dynamic dispatch is left unresolved; data-flow edges are intraprocedural and
flow-insensitive, not a claim of executable interprocedural slicing.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from morph_fl.domain import Relation, SourceLocation, SystemModel

EXCLUDED = {".git", ".venv", "venv", "__pycache__", "tests", "test", "node_modules"}


class _IterativeVisitor(ast.NodeVisitor):
    """Drive generator visitors with an explicit stack, retaining DFS ordering/scopes."""

    def visit(self, node):
        def dispatch(current):
            result = getattr(self, "visit_" + current.__class__.__name__, self.generic_visit)(
                current
            )
            return iter(()) if result is None else iter(result)

        stack = [dispatch(node)]
        while stack:
            try:
                child = next(stack[-1])
            except StopIteration:
                stack.pop()
            else:
                stack.append(dispatch(child))

    def generic_visit(self, node):
        yield from ast.iter_child_nodes(node)


def analyze_python(root: Path, revision: str) -> SystemModel:
    sources, symbols, relations, diagnostics = {}, [], [], []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root)
        if (
            path.is_symlink()
            or EXCLUDED.intersection(relative.parts)
            or path.name.startswith("test_")
        ):
            continue
        name = relative.as_posix()
        text = path.read_text(errors="replace")
        sources[name] = text
        digest = hashlib.sha256(text.encode()).hexdigest()

        def location(node, symbol=""):
            return SourceLocation(
                name,
                node.lineno,
                getattr(node, "end_lineno", node.lineno),
                revision,
                digest,
                symbol,
            )

        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            diagnostics.append(f"{name}:{exc.lineno}: {exc.msg}")
            continue

        class SymbolVisitor(_IterativeVisitor):
            def __init__(self):
                self.scope = []

            def visit_ClassDef(self, node):
                self.scope.append(node.name)
                symbols.append(location(node, ".".join(self.scope)))
                yield from self.generic_visit(node)
                self.scope.pop()

            def visit_FunctionDef(self, node):
                self.scope.append(node.name)
                symbols.append(location(node, ".".join(self.scope)))
                yield from self.generic_visit(node)
                self.scope.pop()

            visit_AsyncFunctionDef = visit_FunctionDef

        SymbolVisitor().visit(tree)
        definitions = {
            node.name: f"{name}::{node.name}"
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    aliases[alias.asname or alias.name] = alias.name.replace(".", "/") + ".py"
            if isinstance(node, ast.ImportFrom):
                module = (node.module or "").replace(".", "/")
                if node.level:
                    parent = relative.parent
                    for _ in range(node.level - 1):
                        parent = parent.parent
                    module = (parent / module).as_posix()
                target = module + ".py"
                relations.append(Relation(name, target, "imports", location(node)))
                for alias in node.names:
                    aliases[alias.asname or alias.name] = target + "::" + alias.name
        for alias, target in aliases.items():
            relations.append(
                Relation(
                    name,
                    target.split("::")[0],
                    "imports",
                    SourceLocation(name, 1, 1, revision, digest),
                )
            )

        class Visitor(_IterativeVisitor):
            def __init__(self):
                self.scope = name
                self.definitions = {}

            def visit_FunctionDef(self, node):
                old_scope, old_defs = self.scope, self.definitions
                self.scope, self.definitions = f"{name}::{node.name}", {}
                yield from self.generic_visit(node)
                self.scope, self.definitions = old_scope, old_defs

            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_Assign(self, node):
                yield node.value
                yield from node.targets

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    target = f"{self.scope}:{node.id}@{node.lineno}"
                    self.definitions[node.id] = target
                    relations.append(Relation(self.scope, target, "writes", location(node)))
                elif isinstance(node.ctx, ast.Load):
                    target = self.definitions.get(node.id, f"{self.scope}:{node.id}")
                    relations.append(Relation(self.scope, target, "reads", location(node)))
                    if node.id in self.definitions:
                        relations.append(
                            Relation(
                                target,
                                f"{self.scope}@{node.lineno}",
                                "data_flows_to",
                                location(node),
                            )
                        )

            def visit_Call(self, node):
                func = node.func
                target = None
                if isinstance(func, ast.Name):
                    target = definitions.get(func.id) or aliases.get(func.id)
                elif (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id in aliases
                ):
                    target = aliases[func.value.id] + "::" + func.attr
                if target is None:
                    try:
                        unresolved = ast.unparse(func)
                    except RecursionError:
                        # Preserve the exact source rather than discard a deep call expression.
                        unresolved = ast.get_source_segment(text, func) or "<unresolved call>"
                relations.append(
                    Relation(
                        self.scope,
                        target or unresolved,
                        "calls",
                        location(node),
                        resolution="syntactic" if target else "unresolved",
                    )
                )
                yield from self.generic_visit(node)

        Visitor().visit(tree)
    return SystemModel(revision, sources, symbols, relations, diagnostics)
