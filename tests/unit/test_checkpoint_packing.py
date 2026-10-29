import json
import tempfile
import unittest
from pathlib import Path

from hpc.scripts.compact_models import restore_model
from hpc.ufv.compact_checkpoint import pack_checkpoint


class CheckpointPackingTests(unittest.TestCase):
    def test_restores_all_records_and_preserves_interrupted_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cell.jsonl"
            row = dict(
                instance_id="unit",
                model=dict(
                    revision="v", symbols=[], relations=[], behavior=dict(expected="unit-only")
                ),
            )
            path.write_bytes((json.dumps(row) + "\n" + '{"instance_id":').encode())
            result = pack_checkpoint(path, Path(tmp) / "graphs")
            self.assertTrue(result["verified"])
            self.assertEqual(result["before"], result["after"])
            self.assertEqual(result["after"]["records"], 1)
            self.assertEqual(
                Path(result["repair"]["preserved_tail"]).read_bytes(), b'{"instance_id":'
            )
            packed = json.loads(path.read_text())
            self.assertEqual(restore_model(packed, path), row["model"])

    def test_refuses_completed_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cell.jsonl"
            original = b'{"instance_id":\n'
            path.write_bytes(original)
            with self.assertRaisesRegex(ValueError, "Corrupt completed"):
                pack_checkpoint(path, Path(tmp) / "graphs")
            self.assertEqual(path.read_bytes(), original)
