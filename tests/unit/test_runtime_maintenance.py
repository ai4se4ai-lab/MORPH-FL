import json
import tempfile
import unittest
from pathlib import Path
from hpc.ufv.runtime_maintenance import digest, verify_sources


class RuntimeMaintenanceTests(unittest.TestCase):
    def test_exact_recorded_repair_accepted_unrecorded_change_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'experiments/full').mkdir(parents=True)
            source = root/'source.py'
            source.write_text('original')
            original = digest(source)
            spec = dict(source_files={'source.py': original})
            protocol = root/'experiments/full/protocol.json'
            protocol.write_text(json.dumps(spec))
            self.assertIsNone(verify_sources(root, spec))
            source.write_text('repaired')
            with self.assertRaisesRegex(ValueError, 'Frozen source differs'):
                verify_sources(root, spec)
            repair = dict(protocol_sha256=digest(protocol), files={'source.py': dict(original_sha256=original, sha256=digest(source))})
            manifest = root/'experiments/full/runtime_maintenance.json'
            manifest.write_text(json.dumps(repair))
            self.assertEqual(verify_sources(root, spec), repair)
            source.write_text('unrecorded')
            with self.assertRaisesRegex(ValueError, 'Maintenance source differs'):
                verify_sources(root, spec)
            repair['files']['source.py']['original_sha256'] = 'wrong'
            manifest.write_text(json.dumps(repair))
            with self.assertRaisesRegex(ValueError, 'Maintenance original identity differs'):
                verify_sources(root, spec)

    def test_interrupted_recovery_streams_and_preserves_partial_tail(self):
        from unittest.mock import patch
        from morph_fl.application import repair_interrupted_tail
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'predictions.jsonl'
            path.write_bytes(b'{"complete": true}\n{"partial":')
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('whole-file read forbidden')):
                repair_interrupted_tail(path)
            self.assertEqual(path.read_bytes(), b'{"complete": true}\n')
            tails = list(Path(tmp).glob('*.tail-*.bin'))
            self.assertEqual(len(tails), 1)
            self.assertEqual(tails[0].read_bytes(), b'{"partial":')
