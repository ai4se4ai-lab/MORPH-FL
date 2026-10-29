"""The storage optimization must not change any scientific record."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


class StorageTests(unittest.TestCase):
    def test_model_packing_is_lossless_shared_and_resumable(self):
        path = Path(__file__).resolve().parents[2] / "hpc/scripts/compact_models.py"
        spec = importlib.util.spec_from_file_location("compact_models", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            main = root / "main"
            main.mkdir()
            store = root / "models"
            first = main / "one.jsonl"
            second = main / "two.jsonl"
            original = dict(
                ranking=["a.py"],
                model=dict(
                    behavior=dict(expected="one"),
                    revision="v",
                    symbols=[dict(name="fn")],
                    relations=[dict(source="a", target="b")],
                ),
            )
            other = dict(original, model=dict(original["model"], behavior=dict(expected="two")))
            first.write_text(json.dumps(original) + "\n")
            second.write_text(json.dumps(other) + "\n")
            module.compact(first, store)
            module.compact(second, store)
            packed = json.loads(first.read_text())
            packed_other = json.loads(second.read_text())
            self.assertEqual(module.restore_model(packed, first), original["model"])
            self.assertEqual(module.restore_model(packed_other, second), other["model"])
            self.assertEqual(packed["ranking"], original["ranking"])
            self.assertEqual(len(list(store.glob("*.json.gz"))), 1)
            before = first.read_bytes()
            module.compact(first, store)
            self.assertEqual(first.read_bytes(), before)
