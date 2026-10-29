"""Protocol tests use a fake local server; real DGXSpark runs are separate."""

import json
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from morph_fl.inference.local import BudgetExceeded
from morph_fl.inference.ollama import OllamaModel


class FakeTokenizer:
    @staticmethod
    def from_pretrained(name, **kwargs):
        return FakeTokenizer()

    def to_str(self):
        return "fixture-tokenizer"

    def encode(self, prompt, add_special_tokens=False):
        return SimpleNamespace(ids=[1] * 20)


class FakeOllama(OllamaModel):
    remote = False
    bad_json = False

    def _request(self, path, payload):
        if path == "/api/tags":
            entry = dict(
                name="qwen2.5-coder:7b", digest="pinned", details=dict(quantization_level="Q4_K_M")
            )
            if self.remote:
                entry["remote_host"] = "https://ollama.com"
            return dict(models=[entry])
        if path == "/api/show":
            return dict(template="<|im_start|>", capabilities=["completion"])
        if path == "/api/version":
            return dict(version="fixture")
        if path == "/api/generate":
            self.last_request = payload
            return dict(
                prompt_eval_count=20,
                eval_count=5,
                response="bad" if self.bad_json else '{"hypotheses":[]}',
                done_reason="stop",
            )
        raise AssertionError(path)


class OllamaTests(unittest.TestCase):
    def model(self):
        with patch.dict(sys.modules, {"tokenizers": SimpleNamespace(Tokenizer=FakeTokenizer)}):
            return FakeOllama("qwen2.5-coder:7b")

    def test_only_local_endpoint_and_model_allowed(self):
        with self.assertRaises(ValueError):
            FakeOllama("qwen2.5-coder:7b", endpoint="https://cloud.example")
        with patch.object(FakeOllama, "remote", True):
            with self.assertRaises(ValueError):
                self.model()

    def test_budget_usage_and_raw_schema_request(self):
        model = self.model()
        result, _ = model.ask([dict(role="user", content="report")], 200)
        self.assertEqual(model.input_tokens, 20)
        self.assertEqual(model.output_tokens, 5)
        self.assertTrue(model.last_request["raw"])
        self.assertFalse(model.last_request["stream"])
        self.assertIsInstance(model.last_request["format"], dict)
        self.assertEqual(result, {"hypotheses": []})

    def test_unaffordable_prompt_does_not_generate(self):
        model = self.model()
        with self.assertRaises(BudgetExceeded):
            model.ask([dict(role="user", content="report")], 50)
        self.assertEqual(model.input_tokens, 0)

    def test_malformed_output_is_still_charged(self):
        model = self.model()
        model.bad_json = True
        with self.assertRaises(json.JSONDecodeError):
            model.ask([dict(role="user", content="report")], 200)
        self.assertEqual(model.input_tokens + model.output_tokens, 25)

    def test_trace_location_outweighs_unrelated_docstring(self):
        from morph_fl.search.controller import source_window

        text = "\n".join(
            ["# error total subtotal"] * 100
            + ["def persist(total):", "    save(total)"]
            + ["# tail"] * 30
        )
        report = 'total error subtotal\n File "/pkg/order.py", line 102, in persist'
        excerpt = source_window(text, report, 10, "pkg/order.py")
        self.assertIn("102:     save(total)", excerpt)


class DriftTests(unittest.TestCase):
    def test_trace_function_is_resolved_when_old_line_numbers_drift(self):
        from morph_fl.search.controller import source_window

        source = "\n".join(
            ["# metadata"] * 100
            + ["def persist(total):", '    """Store a total."""', "    save(total)"]
            + ["# tail"] * 50
        )
        report = 'File "/pkg/order.py", line 20, in persist\n save(total)'
        excerpt = source_window(source, report, 10, "order.py")
        self.assertIn("103:     save(total)", excerpt)
        self.assertNotIn("20: # metadata", excerpt)


class RawTemplateTests(unittest.TestCase):
    def test_known_qwen_raw_template_requires_both_chatml_stop_markers(self):
        class RawQwen(FakeOllama):
            def _request(self, path, payload):
                if path == "/api/show":
                    return dict(
                        template="{{ .Prompt }}",
                        parameters='stop "<|im_start|>"\nstop "<|im_end|>"',
                        details=dict(family="qwen3moe"),
                    )
                return super()._request(path, payload)

        with patch.dict(sys.modules, {"tokenizers": SimpleNamespace(Tokenizer=FakeTokenizer)}):
            model = RawQwen("qwen2.5-coder:7b")
        self.assertEqual(model.metadata["digest"], "pinned")
