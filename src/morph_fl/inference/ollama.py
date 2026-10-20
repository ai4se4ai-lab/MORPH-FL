"""Local-only Ollama inference with pinned model digests and token accounting.

Qwen ChatML is rendered explicitly and sent through /api/generate with raw=True.
A matching Hugging Face tokenizer counts that exact prompt before generation;
server-reported usage is checked and charged even if JSON decoding fails.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from .local import BudgetExceeded

TOKENIZERS = {
    "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "qwen3-coder:30b": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
}
TOKENIZER_REVISIONS = {
    "qwen2.5-coder:7b": "c03e6d358207e414f1eca0bb1891e29f1db0e242",
    "qwen3-coder:30b": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
}
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "expected": {"type": "string"},
        "observed": {"type": "string"},
        "trigger": {"type": "string"},
        "invariants": {"type": "array", "items": {"type": "string"}},
        "ambiguities": {"type": "array", "items": {"type": "string"}},
        "hypotheses": {
            "type": "array",
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "mechanism": {"type": "string"},
                    "prediction": {
                        "anyOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "predicate": {
                                        "type": "string",
                                        "enum": [
                                            "source_contains",
                                            "ast_matches",
                                            "exit_code",
                                            "test_fails",
                                            "output_contains",
                                            "counterfactual_changes_outcome",
                                        ],
                                    },
                                    "expected": {
                                        "anyOf": [
                                            {"type": "boolean"},
                                            {"type": "integer"},
                                            {"type": "string"},
                                        ]
                                    },
                                    "assumptions": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["description", "predicate", "expected", "assumptions"],
                            },
                        ]
                    },
                    "probe": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "line": {"type": "integer", "minimum": 1},
                            "kind": {
                                "type": "string",
                                "enum": [
                                    "source_quote",
                                    "ast_query",
                                    "test",
                                    "trace",
                                    "counterfactual",
                                ],
                            },
                            "quote": {"type": "string"},
                            "procedure_id": {"type": "string"},
                            "baseline_procedure_id": {"type": "string"},
                            "test_code": {"type": "string"},
                            "query": {
                                "type": "object",
                                "properties": {
                                    "node_type": {"type": "string"},
                                    "contains": {"type": "string"},
                                },
                            },
                        },
                        "required": ["path", "line", "quote"],
                    },
                },
                "required": ["path", "mechanism", "prediction", "probe"],
            },
        },
    },
    "required": ["expected", "observed", "hypotheses"],
}


class OllamaModel:
    def __init__(
        self,
        model: str,
        seed: int = 1,
        endpoint="http://127.0.0.1:11434",
        tokenizer: str | None = None,
        context: int = 16384,
        timeout: float = 300,
        temperature: float = 0.2,
    ):
        parsed = urlparse(endpoint)
        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.scheme != "http":
            raise ValueError("Ollama experiments require an explicitly local HTTP endpoint")
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.seed = seed
        self.context = context
        self.timeout = timeout
        self.temperature = temperature
        self.input_tokens = self.output_tokens = 0
        self.calls = []
        tags = self._request("/api/tags", None)
        entry = next((m for m in tags["models"] if m["name"] == model), None)
        if not entry or entry.get("remote_host") or ":cloud" in model:
            raise ValueError("Model must be installed locally and cannot route to a cloud service")
        show = self._request("/api/show", dict(model=model))
        native_template = "<|im_start|>" in show.get("template", "")
        parameters = show.get("parameters") or ""
        verified_raw = (
            model in TOKENIZERS
            and show.get("details", {}).get("family", "").startswith("qwen")
            and "<|im_start|>" in parameters
            and "<|im_end|>" in parameters
        )
        if not (native_template or verified_raw):
            raise ValueError("This adapter supports verified Qwen ChatML templates only")
        from tokenizers import Tokenizer

        identifier = tokenizer or TOKENIZERS.get(model)
        if not identifier:
            raise ValueError("A matching tokenizer is required")
        self.tokenizer = (
            Tokenizer.from_file(identifier)
            if Path(identifier).is_file()
            else Tokenizer.from_pretrained(
                identifier, revision=TOKENIZER_REVISIONS.get(model, "main")
            )
        )
        self.metadata = dict(
            backend="ollama",
            model=model,
            digest=entry["digest"],
            quantization=entry["details"].get("quantization_level"),
            tokenizer=identifier,
            tokenizer_revision=TOKENIZER_REVISIONS.get(model),
            tokenizer_sha256=hashlib.sha256(self.tokenizer.to_str().encode()).hexdigest(),
            context=context,
            temperature=temperature,
            structured_outputs=True,
            server=self._request("/api/version", None),
        )

    def _request(self, path, payload):
        request = urllib.request.Request(
            self.endpoint + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.load(response)

    def set_seed(self, seed):
        self.seed = seed

    @staticmethod
    def render(messages):
        if any(message["role"] not in {"system", "user", "assistant"} for message in messages):
            raise ValueError("Unsupported ChatML role")
        return (
            "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages)
            + "<|im_start|>assistant\n"
        )

    def ask(self, messages, remaining, max_new=1536):
        prompt = self.render(messages)
        estimated = len(self.tokenizer.encode(prompt, add_special_tokens=False).ids)
        # Reserve template/BOS accounting slack, and verify actual server counts below.
        maximum = min(max_new, remaining - estimated - 32, self.context - estimated - 32)
        if maximum < 64:
            raise BudgetExceeded()
        answer = self._request(
            "/api/generate",
            dict(
                model=self.model,
                prompt=prompt,
                raw=True,
                stream=False,
                format=RESPONSE_SCHEMA,
                think=False,
                keep_alive="10m",
                options=dict(
                    seed=self.seed,
                    temperature=self.temperature,
                    num_ctx=self.context,
                    num_predict=maximum,
                ),
            ),
        )
        if "prompt_eval_count" not in answer or "eval_count" not in answer:
            raise RuntimeError("Ollama did not return usage; refusing unaccounted inference")
        consumed_in, consumed_out = answer["prompt_eval_count"], answer["eval_count"]
        self.input_tokens += consumed_in
        self.output_tokens += consumed_out
        self.calls.append(
            {
                k: answer.get(k)
                for k in (
                    "prompt_eval_count",
                    "eval_count",
                    "done_reason",
                    "total_duration",
                    "load_duration",
                    "eval_duration",
                )
            }
        )
        if consumed_in + consumed_out > remaining or consumed_in > estimated + 32:
            raise RuntimeError(
                "Ollama/tokenizer budget mismatch; run must not enter matched-budget results"
            )
        text = answer.get("response", "")
        decoded = json.loads(text)
        if not isinstance(decoded, dict):
            raise ValueError("Expected a JSON object")
        return decoded, text
