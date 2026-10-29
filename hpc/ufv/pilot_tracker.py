"""Read pilot metadata/reports over SSH; publish a small local status page."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REMOTE = '/home/babaei/morph-ufv/pilots/pilot-20261024'
SCRIPT = r'''
import json,subprocess
from pathlib import Path
base=Path('/home/babaei/morph-ufv/pilots/pilot-20261024')
out={'base':str(base),'files':{}}
for relative in ['schedule.json','results/pilot.json','results/pending.json',
                 'results/analysis/completeness.json','results/interim-analysis/completeness.json']:
 p=base/relative
 if p.exists():out[relative]=json.loads(p.read_text())
for directory in ['existing-analysis','interim-analysis','analysis']:
 for name in ['report.md','scores.csv','summary.json','completeness.json','quality.json',
              'controls.json','final-verification.json']:
  p=base/'results'/directory/name
  if p.exists():out['files'][directory+'/'+name]=p.read_text()
counts={}
reuse=base/'results/reuse.json'
if reuse.exists():
 for row in json.loads(reuse.read_text())['records']:
  if row['file'].startswith('main__'):
   cell=row['file'][:-6];counts[cell]=counts.get(cell,0)+1
for p in (base/'results/progress').glob('main*.jsonl'):
 counts[p.stem]=max(counts.get(p.stem,0),sum(bool(l.strip()) for l in p.open()))
out['completed_primary']=sum(counts.values())
out['completed_by_model']={str(m):sum(n for cell,n in counts.items() if '__m'+str(m)+'__' in cell)
                           for m in [0,1]}
out['successful_cells_by_model']={str(m):len(list((base/'results/receipts').glob('main__m'+str(m)+'__*.json')))
                                 for m in [0,1]}
out['queue']=subprocess.check_output(['squeue','-h','-r','-u','babaei','-o','%i|%j|%T|%R'],universal_newlines=True)
print(json.dumps(out))
'''


def refresh():
    response = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                               'babaei@slurm.soc.ufv.ca', 'python3 -'],
                              input=SCRIPT, text=True, capture_output=True, timeout=90, check=True)
    state = json.loads(response.stdout)
    state['checked_utc'] = datetime.now(timezone.utc).isoformat()
    destination = ROOT / 'experiments/pilot/results'
    destination.mkdir(parents=True, exist_ok=True)
    for relative, content in state.pop('files').items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (destination / 'status.json').write_text(json.dumps(state, indent=2) + '\n')
    pilot = state.get('results/pilot.json', {})
    if pilot:
        (destination / 'pilot.json').write_text(json.dumps(pilot, indent=2) + '\n')
    complete = state.get('results/analysis/completeness.json', {}).get('complete', False)
    model_counts = state.get('completed_by_model', {})
    interim = state.get('results/interim-analysis/completeness.json', {})
    lines = ['# Fast pilot progress', '', f'Updated: {state["checked_utc"]} (UTC).', '',
             '**The extended study is deferred.** Its pending jobs are held; existing full-run '
             'outputs are preserved. Pilot inference follows the two full-study tasks that '
             'were already running when the pilot was scheduled.', '',
             '**Pilot:** 50 issues × Qwen/DeepSeek × one seed × four workflows = 400 primary records. '
             '32k token budget and 16 rounds are unchanged. Previously inspected IDs were excluded '
             'before outcomes were read. Completed matching predictions are reused.', '',
             f'**Progress:** {state["completed_primary"]}/400 primary records '
             f'({"complete, coverage verified" if complete else "coverage not yet complete"}).', '',
             *(['[Completed pilot results and interpretation](pilot_results.md). '
                'The extended study remains deferred pending output-quality diagnosis.', '']
               if complete else []),
             f'**By model:** Qwen {model_counts.get("0", 0)}/200; '
             f'DeepSeek {model_counts.get("1", 0)}/200. Counts show written records; '
             'the final report validates full coverage.', '',
             '[Existing paired comparison](../../experiments/pilot/results/existing-analysis/report.md) '
             'uses complete four-workflow issue sets from a completion-selected snapshot. '
             'Its exploratory estimates do not establish generalization.', '',
             '[Interim pilot comparison](../../experiments/pilot/results/interim-analysis/report.md) '
             'reports a scheduled snapshot of the fixed 50-issue sample, with incomplete coverage '
             f'shown explicitly. Latest snapshot: {interim.get("checked_utc", "pending")}; '
             f'{interim.get("observed", 0)}/400 records.', '',
             '[Output-quality review](pilot_quality_review.md) documents the DeepSeek '
             'empty-hypothesis and invalid-response diagnostics separately from scheduler health.', '',
             '[Pilot report](../../experiments/pilot/results/analysis/report.md) contains the final comparison. '
             'Per-case scores, descriptive repository bootstrap intervals and completeness metadata '
             'are preserved with the reports.', '',
             f'Remote pilot artifacts: `{REMOTE}`.', '',
             '## Scheduler', '', '```text']
    pilot_queue = [line for line in state['queue'].splitlines() if 'morph-pilot' in line]
    lines += pilot_queue or ['No pilot jobs queued or running.']
    lines += ['```', '', '## Resume the extended study', '',
              'The exact held job IDs are recorded remotely in `schedule.json` and `held-jobs.json`. '
              'Release those jobs with `scontrol release <job-id>` when ready. '
              'Pilot outputs remain separate; new pilot-only predictions must be imported and '
              'validated before they can count toward full-study completion.', '']
    (ROOT / 'docs/UFV/pilot_progress.md').write_text('\n'.join(lines))
    print(json.dumps(dict(checked_utc=state['checked_utc'], primary=state['completed_primary'], complete=complete)))


if __name__ == '__main__':
    refresh()
