import json
import tempfile
import unittest
from pathlib import Path

from morph_fl.benchmark import metrics
from morph_fl.engine import localize
from morph_fl.models import Hypothesis, snapshot, verify_quote


class FakeModel:
    """Deterministic protocol fixture; never used for benchmark inference."""

    input_tokens = 0
    output_tokens = 0

    def __init__(self):
        self.contexts = []

    def ask(self, messages, remaining):
        self.contexts.append(messages)
        self.input_tokens += 100
        self.output_tokens += 50
        response = dict(
            expected="discount persisted",
            observed="subtotal persisted",
            hypotheses=[
                dict(
                    path="order.py",
                    mechanism="wrong persisted value",
                    prediction="subtotal appears in save call",
                    probe=dict(path="order.py", line=2, quote="save(subtotal)"),
                )
            ],
        )
        return response, json.dumps(response)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "order.py").write_text("def persist(subtotal):\n    save(subtotal)\n")
        (self.root / "pricing.py").write_text("def discount(total):\n    return total * .9\n")
        (self.root / "tests").mkdir()
        (self.root / "tests/test_gold.py").write_text("gold_secret=True")

    def tearDown(self):
        self.temp.cleanup()

    def test_verification_is_exact_and_versioned(self):
        e = verify_quote(self.root, "abc", dict(path="order.py", line=2, quote="save(subtotal)"))
        self.assertEqual(e.revision, "abc")
        self.assertEqual(e.kind, "static_source")
        self.assertIsNone(
            verify_quote(self.root, "abc", dict(path="order.py", line=1, quote="save(subtotal)"))
        )

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            verify_quote(self.root, "abc", dict(path="../outside.py", line=1, quote="secret"))

    def test_symlink_escape_rejected(self):
        (self.root / "link.py").symlink_to("/etc/passwd")
        with self.assertRaises(ValueError):
            verify_quote(self.root, "abc", dict(path="link.py", line=1, quote="root"))

    def test_reset_preserves_evidence_cost_and_discards_dialogue(self):
        b = FakeModel()
        result = localize(self.root, "persist subtotal discount", "abc", b, rounds=7)
        self.assertGreater(result["resets"], 0)
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["input_tokens"], 700)
        lengths = [len(m) for m in b.contexts]
        self.assertTrue(all(length == 2 for length in lengths))
        self.assertTrue(any(a.get("type") == "reset" for a in result["audit"]))
        self.assertEqual(result["ranking"][0], "order.py")
        self.assertIsNone(result["confidence"])

    def test_no_forgetting_keeps_context(self):
        b = FakeModel()
        r = localize(self.root, "persist", "abc", b, "no_forgetting", rounds=7)
        self.assertEqual(r["resets"], 0)
        self.assertEqual([len(m) for m in b.contexts], sorted(len(m) for m in b.contexts))

    def test_snapshot_does_not_promote_hypothesis_to_fact(self):
        h = Hypothesis("h", "order.py", "mechanism", "prediction", {})
        s = snapshot([h], {}, 42)
        self.assertEqual(s["observations"], [])
        self.assertEqual(s["remaining_tokens"], 42)

    def test_gold_tests_not_visible(self):
        b = FakeModel()
        localize(self.root, "persist", "abc", b, rounds=1)
        self.assertNotIn("gold_secret", json.dumps(b.contexts))

    def test_metrics_multi_file_and_duplicates(self):
        m = metrics(["x", "a", "a", "b"], ["a", "b"])
        self.assertEqual(m["mrr"], 0.5)
        self.assertEqual(m["recall10"], 1)
        self.assertEqual(m["top1"], 0)

    def test_empty_gold_not_scored_as_failure(self):
        self.assertFalse(metrics(["a"], [])["eligible"])
        self.assertIsNone(metrics(["a"], [])["mrr"])

    def test_no_llm_silent_fallback(self):
        with self.assertRaises(ValueError):
            localize(self.root, "bug", "abc", variant="morph")

    def test_bm25_runs_without_backend(self):
        r = localize(self.root, "persist subtotal", "abc", variant="bm25")
        self.assertEqual(r["ranking"][0], "order.py")
        self.assertTrue(r["abstained"])


if __name__ == "__main__":
    unittest.main()
