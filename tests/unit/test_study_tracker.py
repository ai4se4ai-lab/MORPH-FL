import json
import tempfile
import unittest
from pathlib import Path

from hpc.ufv.study_tracker import render_document
from hpc.ufv.tracker_snapshot import inspect_run


class StudyTrackerTests(unittest.TestCase):
    def state(self):
        return dict(run='example', checked_utc='2026-10-20T13:00:00Z', done=False,
                    tracker=dict(data=dict(unique_cases=1), stages=[dict(name='retrieval', cells=1, expected_steps=1, successful_steps=1)],
                                 progress={'retrieval__m0__s1__p0.jsonl':dict(completed=2, conditions={})}))

    def test_full_record_count_requires_receipt(self):
        state = self.state()
        text = render_document(state)
        line = next(line for line in text.splitlines() if '| BM25 + graph, once per unique issue |' in line)
        self.assertIn('awaiting verified receipts', line)
        self.assertNotIn('COMPLETE (receipts verified)', line)
        state['tracker']['receipts'] = {'retrieval__m0__s1__p0':dict(records=2, complete=True)}
        text = render_document(state)
        self.assertIn('COMPLETE (receipts verified)', text)

    def test_scheduler_finished_is_not_scientific_success(self):
        state = self.state()
        state.update(done=True, scientific_completeness=dict(complete=False))
        text = render_document(state)
        self.assertIn('INCOMPLETE (coverage report)', text)
        self.assertIn('REQUIRES HUMAN REVIEW', text)
        self.assertNotIn('Scientific completeness: **verified complete**', text)

    def test_running_array_members_take_precedence_over_pending_members(self):
        state = self.state()
        state['tracker']['progress'] = {}
        state['tracker']['stages'][0]['jobs'] = ['123']
        state['active'] = '123|RUNNING\n123|PENDING'
        text = render_document(state)
        line = next(line for line in text.splitlines() if '| BM25 + graph, once per unique issue |' in line)
        self.assertIn('| RUNNING |', line)

    def test_incremental_progress_ignores_partial_line_and_recounts_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / 'repo'
            logs = repo / 'hpc/logs/example'
            logs.mkdir(parents=True)
            work = Path(tmp) / 'work'
            (logs / 'run_manifest.json').write_text(json.dumps(dict(cluster_env=dict(WORK=str(work)))))
            progress = work / 'runs/example/results/progress'
            progress.mkdir(parents=True)
            path = progress / 'retrieval__m0__s1__p0.jsonl'
            first = json.dumps(dict(key=['case1', 'bm25', 32000, None]))+'\n'
            second = json.dumps(dict(key=['case1', 'graph', 32000, None]))+'\n'
            path.write_text(first+second[:10])
            one = inspect_run(repo, 'example')['progress'][path.name]
            self.assertEqual(one['completed'], 1)
            with path.open('a') as out:
                out.write(second[10:])
            two = inspect_run(repo, 'example')['progress'][path.name]
            self.assertEqual(two['completed'], 2)
            self.assertEqual(sum(two['conditions'].values()), 2)
            path.write_text(first)
            reset = inspect_run(repo, 'example')['progress'][path.name]
            self.assertEqual(reset['completed'], 1)
