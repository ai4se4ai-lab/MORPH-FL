import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments.pilot import manage
from experiments.pilot.snapshot import completed_rows


class PilotTests(unittest.TestCase):
    def test_live_snapshot_ignores_incomplete_tail_and_later_appends(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'predictions.jsonl'
            path.write_bytes(b'{"id": 1}\n{"id":')
            limit = path.stat().st_size
            with path.open('ab') as stream:
                stream.write(b' 2}\n')
            self.assertEqual(list(completed_rows(path, limit)), [{'id': 1}])
            self.assertEqual(list(completed_rows(path, path.stat().st_size)),
                             [{'id': 1}, {'id': 2}])

    def test_selection_is_order_independent_balanced_and_excludes_prior_cases(self):
        cases = [dict(instance_id=f'{repo}-{i}', repo=repo)
                 for repo in ['a', 'b', 'c'] for i in range(30)]
        selected = manage.select(cases, {'a-0'})
        self.assertEqual(selected, manage.select(list(reversed(cases)), {'a-0'}))
        self.assertEqual(len(set(selected)), 50)
        self.assertNotIn('a-0', selected)
        counts = [sum(i.startswith(r + '-') for i in selected) for r in ['a', 'b', 'c']]
        self.assertLessEqual(max(counts) - min(counts), 1)

    def test_subset_preserves_original_shards_and_full_settings(self):
        from experiments import full
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'experiments/full').mkdir(parents=True)
            protocol = root / 'experiments/full/protocol.json'
            protocol.write_text('{}')
            (root / 'data').mkdir()
            cases = [dict(instance_id=str(i)) for i in range(100)]
            data = root / 'data/cases.jsonl'
            data.write_text(''.join(json.dumps(c) + '\n' for c in cases))
            manage.write_json(root / 'pilot.json', dict(
                selected_ids=['1', '33', '66'], models=[0, 1], variants=manage.VARIANTS,
                wrapper_sha256=manage.digest(manage.__file__), cases_sha256=manage.digest(data),
                protocol_sha256=manage.digest(protocol)))
            def check(args):
                selected = fake.selected_cases(cases, 'main', 0)[args.shard::args.shards]
                self.assertEqual([c['instance_id'] for c in selected], ['1', '33'])
                self.assertEqual((args.seed, args.shards, args.smoke), (1, 32, 0))
                self.assertEqual(fake.jobs_for('main', 0),
                                 [(v, 32000, None) for v in manage.VARIANTS])
            fake = SimpleNamespace(ROOT=root, run=check, jobs_for=lambda *a:
                                   [(v, 32000, None) for v in manage.VARIANTS + ['rgfl_adapted']])
            with patch.object(full, 'suite', fake, create=True):
                manage.run(SimpleNamespace(results=str(root), model=0, shard=1))

    def test_report_excludes_unpaired_cases(self):
        records = []
        for variant in manage.VARIANTS:
            records.append(dict(model_id='q', seed=1, instance_id='paired', repo='r',
                                variant=variant, eligible=True, top1=int(variant == 'morph'),
                                top5=1, function_top1=None, tokens=100,
                                end_to_end_seconds=2, resets=0))
        records.append(dict(records[0], instance_id='unpaired'))
        with tempfile.TemporaryDirectory() as temporary:
            manage.report(records, Path(temporary), 'test')
            summary = json.loads((Path(temporary) / 'summary.json').read_text())
            self.assertTrue(all(r['paired_issues'] == 1 for r in summary))
            self.assertEqual(summary[0]['top1'], 1)
            self.assertEqual(summary[1]['top1'], 0)


if __name__ == '__main__':
    unittest.main()
