import tempfile
import unittest
from pathlib import Path

from hpc.ufv.recovery_io import inspect_process


class RecoveryIOTests(unittest.TestCase):
    def test_reports_compaction_bytes_for_exact_run_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            results=root/'results'
            predictions=results/'predictions/retrieval__m0__s1__p0.jsonl'
            predictions.parent.mkdir(parents=True)
            predictions.write_bytes(b'x'*100)
            output=predictions.with_suffix('.jsonl.unique.tmp')
            output.write_bytes(b'packed')
            proc=root/'123'
            (proc/'fd').mkdir(parents=True)
            (proc/'fdinfo').mkdir()
            args=['python','-m','experiments.full.suite','run','--results',str(results),'--track','retrieval']
            (proc/'cmdline').write_bytes(('\0'.join(args)+'\0').encode())
            (proc/'status').write_text('VmRSS:\t1024 kB\n')
            (proc/'fd/3').symlink_to(predictions)
            (proc/'fd/4').symlink_to(output)
            (proc/'fdinfo/3').write_text('pos:\t40\n')
            (proc/'fdinfo/4').write_text('pos:\t6\n')
            info=inspect_process(proc,results)
            self.assertEqual(info['phase'],'COMPACTING')
            self.assertEqual(info['fraction'],.4)
            self.assertEqual(info['memory_rss'],'1024 kB')
            self.assertIsNone(inspect_process(proc,root/'other-run'))
            (proc/'fd/4').unlink()
            info=inspect_process(proc,results)
            self.assertEqual(info['phase'],'CHECKPOINT READ / RESUME')
            self.assertNotIn('fraction',info)
