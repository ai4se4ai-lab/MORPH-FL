import unittest

from morph_fl.baselines.local import extract_files, extract_functions, functions
from morph_fl.baselines.vendor import prompts


class BaselineTests(unittest.TestCase):
    def test_paths_are_validated_and_deduplicated(self):
        self.assertEqual(extract_files("bad.py\n../secret.py\na.py\na.py", {"a.py": ""}), ["a.py"])

    def test_qualified_function_parsing(self):
        files = {"a.py": "class A:\n def f(self):\n  pass\n"}
        self.assertEqual(
            extract_functions("a.py\nfunction: A.f\nfunction: invented", files), ["a.py::A.f"]
        )
        self.assertIn("A.f", functions(files["a.py"]))

    def test_upstream_prompts_accept_only_public_inputs(self):
        self.assertIn(
            "example report", prompts.file_reasoning_prompt("def f(): pass", "example report")
        )
        self.assertIn("a.py", prompts.show_project_structure({"a.py": {"classes": []}}))


class StageBudgetTests(unittest.TestCase):
    def test_budget_exhaustion_never_calls_model(self):
        from types import SimpleNamespace

        from morph_fl.baselines.local import Investigation
        from morph_fl.inference.local import BudgetExceeded

        class Backend:
            input_tokens = 15999
            output_tokens = 0
            tokenizer = SimpleNamespace(encode=lambda *a, **k: SimpleNamespace(ids=[1] * 200))
            render = staticmethod(lambda messages: str(messages))

            def ask(self, *args, **kwargs):
                raise AssertionError("Exhausted budget must not invoke inference")

        with self.assertRaises(BudgetExceeded):
            Investigation(Backend()).ask("test", lambda text: text, "repository", 1000)

    def test_free_text_adapter_keeps_usage_and_removes_schema(self):
        import json
        from unittest.mock import patch

        from morph_fl.baselines.local import TextOllama
        from morph_fl.inference.ollama import OllamaModel

        backend = object.__new__(TextOllama)
        with patch.object(
            OllamaModel,
            "_request",
            return_value={"response": "a.py", "prompt_eval_count": 11, "eval_count": 3},
        ) as request:
            result = backend._request(
                "/api/generate", {"format": {"type": "object"}, "model": "local"}
            )
        self.assertNotIn("format", request.call_args.args[1])
        self.assertEqual(result["prompt_eval_count"], 11)
        self.assertEqual(json.loads(result["response"])["text"], "a.py")
