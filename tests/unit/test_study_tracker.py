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

    def test_active_replacement_is_recovery_until_receipt(self):
        state = self.state()
        stage = state['tracker']['stages'][0]
        stage.update(jobs=['123', '456'], successful_steps=0,
                     failures=[dict(job='123', cell='all', step='run', rc='1')])
        state['active'] = '456|RUNNING'
        text = render_document(state)
        line = next(v for v in text.splitlines() if '| BM25 + graph, once per unique issue |' in v)
        self.assertIn('RECOVERY RUNNING', line)
        self.assertNotIn('ATTENTION: failed step', line)
        self.assertNotIn('COMPLETE', line)
        stage['failures'][0]['job'] = '456'
        self.assertIn('ATTENTION: failed step', render_document(state))
        stage['failures'][0]['job'] = '123'
        state['active'] = ''
        self.assertIn('ATTENTION: failed step', render_document(state))
        stage['failures'] = []
        state['tracker']['receipts'] = {'retrieval__m0__s1__p0':dict(records=2,complete=True)}
        self.assertIn('COMPLETE (receipts verified)', render_document(state))

    def test_compaction_progress_does_not_imply_completion(self):
        state=self.state()
        state['tracker']['stages'][0].update(jobs=['123','456'],failures=[dict(job='123',rc='1')])
        state['active']='456|RUNNING'
        state['recovery_io']=dict(phase='COMPACTING',fraction=.4,observed_utc='2026-10-20T18:03:00Z')
        text=render_document(state)
        self.assertIn('checkpoint compaction 40.0%',text)
        self.assertNotIn('COMPLETE (receipts verified)',text)

    def test_model_row_running_before_first_record(self):
        state=self.state()
        state['tracker']['models']=[dict(id='unit-model')]
        state['tracker']['stages'].append(dict(name='main_m0',jobs=['456'],cells=96,expected_steps=96,successful_steps=0))
        state['active']='456|RUNNING'
        text=render_document(state)
        line=next(v for v in text.splitlines() if 'unit-model — three seeds / 32 shards' in v)
        self.assertIn('| RUNNING |',line)

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


class TrackerHistoryTests(unittest.TestCase):
    def test_cadence_restart_deltas_and_persistent_failure(self):
        from hpc.ufv.tracker_history import refresh
        with tempfile.TemporaryDirectory() as tmp:
            output, history = Path(tmp)/'progress.md', Path(tmp)/'history.json'
            state = StudyTrackerTests().state()
            event = dict(kind='step', stage='retrieval', cell='0', step='run', job='123',
                         rc='1', command='python run.py', log='/remote/run.log', tail='bad | input', resolved=False)
            state['tracker']['failure_events'] = [event]
            self.assertTrue(refresh(state, output, history, now='2026-10-20T13:00:00Z'))
            self.assertFalse(refresh(state, output, history, now='2026-10-20T13:29:59Z'))
            event['resolved'] = True
            event['tail'] = 'successful retry'
            state['tracker']['progress']['retrieval__m0__s1__p0.jsonl']['completed'] = 3
            self.assertTrue(refresh(state, output, history, now='2026-10-20T13:30:00Z'))
            data = json.loads(history.read_text())
            self.assertEqual(len(data['refreshes']), 2)
            self.assertEqual(len(data['failures']), 1)
            self.assertIn('RESOLVED', next(iter(data['failures'].values()))['status'])
            self.assertIn('2 → 3 (+1)', output.read_text())
            self.assertIn('/remote/run.log', output.read_text())
            self.assertEqual(output.read_text().rfind('## '), output.read_text().index('## Refresh change log'))
            self.assertTrue(refresh(state, output, history, now='2026-10-20T14:00:00Z'))
            self.assertIn('3 → 3 (+0)', output.read_text())

    def test_monitor_failure_is_recorded_between_publications(self):
        from hpc.ufv.tracker_history import refresh
        with tempfile.TemporaryDirectory() as tmp:
            output, history = Path(tmp)/'progress.md', Path(tmp)/'history.json'
            state = StudyTrackerTests().state()
            refresh(state, output, history, now='2026-10-20T13:00:00Z')
            refresh(state, output, history, now='2026-10-20T13:01:00Z', monitor_error='SSH | disconnected')
            self.assertEqual(len(json.loads(history.read_text())['failures']), 1)
            refresh(state, output, history, now='2026-10-20T13:30:00Z')
            self.assertIn('SSH &#124; disconnected', output.read_text())
            self.assertIn('RESOLVED (successful subsequent poll)', output.read_text())

    def test_snapshot_retains_failed_attempt_after_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)/'repo'
            logs = repo/'hpc/logs/example'
            logs.mkdir(parents=True)
            work = Path(tmp)/'work'
            (logs/'run_manifest.json').write_text(json.dumps(dict(cluster_env=dict(WORK=str(work)))))
            (logs/'steps.tsv').write_text('time\tjob\tstage\tcell\tstep\trc\tcommand\n'
                                         'earlier\t1\tretrieval\t0\trun\t1\tpython run.py\n'
                                         'later\t2\tretrieval\t0\trun\t0\tpython run.py\n')
            log = logs/'steps/retrieval/0/run.log'
            log.parent.mkdir(parents=True)
            log.write_text('Traceback: example failure')
            events = inspect_run(repo, 'example')['failure_events']
            self.assertEqual(len(events), 1)
            self.assertTrue(events[0]['resolved'])
            self.assertEqual(events[0]['job'], '1')
            self.assertEqual(events[0]['log'], str(log))
            self.assertIn('Traceback', events[0]['tail'])

    def test_cron_publication_records_trigger_and_cadence(self):
        from hpc.ufv.tracker_history import refresh
        with tempfile.TemporaryDirectory() as tmp:
            output, history = Path(tmp)/'progress.md', Path(tmp)/'history.json'
            state = StudyTrackerTests().state()
            state['monitor_mode'] = 'cron'
            self.assertTrue(refresh(state, output, history, force=True, now='2026-10-20T14:00:00Z'))
            self.assertIn('Cron 30-minute refresh', output.read_text())
            self.assertIn('Cron on comp370 checks and refreshes it every 30 minutes', output.read_text())
