"""Budget-constrained Agentless and RGFL adaptations with upstream prompts.

No benchmark labels are accepted by this module. Free-text decoding preserves
upstream output conventions; model sampling/accounting matches the Ollama adapter.
"""

import ast
import json
import re
import time
from pathlib import Path

from morph_fl.inference.local import BudgetExceeded
from morph_fl.inference.ollama import OllamaModel
from morph_fl.program_analysis.retrieval import index

from .vendor import prompts
from .vendor.compress_file import get_skeleton


class TextOllama(OllamaModel):
    """Reuse verified token accounting while retaining upstream free-text outputs."""

    def _request(self, path, payload):
        if path != "/api/generate":
            return super()._request(path, payload)
        payload = dict(payload)
        payload.pop("format", None)
        answer = super()._request(path, payload)
        answer["response"] = json.dumps({"text": answer.get("response", "")})
        return answer


def extract_files(text, allowed):
    return list(dict.fromkeys(p for p in re.findall(r"[\w./-]+\.py", text) if p in allowed))


def functions(source):
    """Qualified names and exact pre-fix source, excluding class-only predictions."""
    result = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return result
    lines = source.splitlines()

    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                if not isinstance(child, ast.ClassDef):
                    result[name] = "\n".join(lines[child.lineno - 1 : child.end_lineno])
                visit(child, name + ".")
            else:
                visit(child, prefix)

    visit(tree)
    return result


def extract_functions(text, files):
    result, current = [], None
    for line in text.splitlines():
        paths = extract_files(line, files)
        if paths:
            current = paths[0]
        match = re.search(r"function:\s*([\w.]+)", line)
        if current and match and match[1] in functions(files[current]):
            result.append(current + "::" + match[1])
    return list(dict.fromkeys(result))


class Investigation:
    def __init__(self, backend, budget=16000):
        self.backend, self.budget = backend, budget
        self.trace = []
        self.started = time.monotonic()

    def ask(self, stage, make_prompt, content, cap, output=512):
        """Trim supplied context only, with exact token counts and visible audit."""
        b = self.backend
        remaining = self.budget - b.input_tokens - b.output_tokens
        cap = min(cap, remaining)
        original = len(content)
        while content:
            message = [{"role": "user", "content": make_prompt(content)}]
            count = len(b.tokenizer.encode(b.render(message), add_special_tokens=False).ids)
            if count + output + 32 <= cap:
                break
            content = content[: int(len(content) * 0.85)]
        else:
            raise BudgetExceeded()
        before = (b.input_tokens, b.output_tokens)
        decoded, _ = b.ask(message, cap, max_new=output)
        text = decoded["text"]
        self.trace.append(
            dict(
                stage=stage,
                prompt=message,
                response=text,
                original_chars=original,
                shown_chars=len(content),
                input_tokens=b.input_tokens - before[0],
                output_tokens=b.output_tokens - before[1],
            )
        )
        return text


def localize(case, backend, variant, budget=16000):
    if variant not in {"agentless_adapted", "rgfl_adapted"}:
        raise ValueError(variant)
    backend.input_tokens = backend.output_tokens = 0
    files, _, _ = index(Path(case["root"]))
    report = case["report"]
    run = Investigation(backend, budget)
    structure = {}
    for path in files:
        node = structure
        for part in path.split("/")[:-1]:
            node = node.setdefault(part, {})
        node[path.split("/")[-1]] = {"classes": []}
    ranking, function_ranking, status = [], [], "complete"
    try:
        response = run.ask(
            "file_selection",
            lambda x: prompts.obtain_relevant_files_prompt.format(
                problem_statement=report, structure=x
            ),
            prompts.show_project_structure(structure),
            2600,
            256,
        )
        ranking = extract_files(response, files)[:5]
        if variant == "rgfl_adapted" and ranking:
            reasoning = {}
            for path in ranking[:3]:
                reasoning[path] = run.ask(
                    "file_reasoning:" + path,
                    lambda x: prompts.file_reasoning_prompt(x, report),
                    files[path],
                    2000,
                    384,
                )
            response = run.ask(
                "file_ranking",
                lambda x: prompts.file_ranking_prompt(x, report),
                json.dumps(reasoning),
                2000,
                256,
            )
            # Preserve unranked original candidates; no gold-dependent fallback.
            ranking = list(dict.fromkeys(extract_files(response, reasoning) + ranking))
        if ranking:
            context = "\n".join(
                f"### {p} ###\n{get_skeleton(files[p], compress_assign=True)}" for p in ranking[:3]
            )
            response = run.ask(
                "element_selection",
                lambda x: (
                    prompts.obtain_relevant_functions_and_vars_from_compressed_files_prompt_more.format(
                        problem_statement=report, file_contents=x
                    )
                ),
                context,
                3500,
                512,
            )
            function_ranking = extract_functions(response, {p: files[p] for p in ranking[:3]})
        if variant == "rgfl_adapted" and function_ranking:
            reasons = {}
            for key in function_ranking[:3]:
                path, name = key.split("::")
                reasons[key] = run.ask(
                    "element_reasoning:" + key,
                    lambda x: prompts.element_reasoning_prompt(x, report),
                    functions(files[path])[name],
                    1200,
                    256,
                )
            response = run.ask(
                "element_ranking",
                lambda x: prompts.element_ranking_prompt(x, report),
                json.dumps(reasons),
                1800,
                256,
            )
            # Match exact known keys in response order; never execute upstream eval().
            ordered = sorted((response.find(k), k) for k in reasons if k in response)
            function_ranking = list(dict.fromkeys([k for _, k in ordered] + function_ranking))
    except BudgetExceeded:
        status = "budget_exhausted"
    return dict(
        instance_id=case["instance_id"],
        repo=case["repo"],
        revision=case["revision"],
        variant=variant,
        ranking=ranking,
        function_ranking=function_ranking,
        input_tokens=backend.input_tokens,
        output_tokens=backend.output_tokens,
        seconds=time.monotonic() - run.started,
        status=status,
        trace=run.trace,
        abstained=not ranking,
        confidence=None,
    )
