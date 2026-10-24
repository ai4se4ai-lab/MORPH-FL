"""Hold extended-study pending work, preserving running tasks, then submit the pilot."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def command(argv):
    result = subprocess.run(argv, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def schedule(base):
    results = base / 'results'
    if (base / 'schedule.json').exists():
        raise ValueError('Pilot already scheduled')
    pending = json.loads((results / 'pending.json').read_text())
    snapshot = command(['squeue', '-h', '-r', '-u', 'babaei', '-o', '%i|%j|%T'])
    (base / 'queue-before.txt').write_text(snapshot + '\n')
    held, running, submissions = [], [], []
    for line in snapshot.splitlines():
        job, name, state = line.split('|')
        if not name.startswith('morph-ufv_'):
            continue
        if state == 'RUNNING':
            running.append(job)
        elif state == 'PENDING':
            # Hold task IDs for the partially running main array, whole arrays otherwise.
            target = job if name == 'morph-ufv_main_m0' else job.split('_')[0]
            if target not in held:
                command(['scontrol', 'hold', target])
                held.append(target)
                (base / 'held-jobs.json').write_text(json.dumps(held, indent=2) + '\n')
    common = ['sbatch', '--parsable', '--account=babaei', '--partition=main',
              '--cpus-per-task=8', '--mem=40G', '--time=12:00:00',
              '--gres=gpu:nvidia_a30:1', '--open-mode=append']
    env = ('ALL,PILOT_ROOT=/home/babaei/projects/MORPH-FL-full-v12-20261020'
           f',PILOT_RESULTS={results},PILOT_CODE={base}/code')
    dependency = running
    for model in [0, 1]:
        shards = [str(p['shard']) for p in pending if p['model'] == model]
        if not shards:
            continue
        argv = common + [f'--job-name=morph-pilot-m{model}',
                         f'--array={",".join(shards)}%2',
                         f'--output={base}/m{model}_%A_%a.out',
                         f'--error={base}/m{model}_%A_%a.err',
                         f'--export={env},PILOT_MODE=run,PILOT_MODEL={model}']
        if dependency:
            argv.append('--dependency=afterany:' + ':'.join(dependency))
        argv.append(str(base / 'code/pilot.sh'))
        job = command(argv).split(';')[0]
        submissions.append(dict(model=model, job=job, command=argv))
        dependency = [job]
        (base / 'submissions.json').write_text(json.dumps(submissions, indent=2) + '\n')
    argv = ['sbatch', '--parsable', '--account=babaei', '--partition=main',
            '--cpus-per-task=2', '--mem=16G', '--time=01:00:00',
            '--job-name=morph-pilot-report', f'--output={base}/report.out',
            f'--error={base}/report.err', f'--export={env},PILOT_MODE=analyze']
    if dependency:
        argv.append('--dependency=afterany:' + ':'.join(dependency))
    argv.append(str(base / 'code/pilot.sh'))
    report = command(argv).split(';')[0]
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), held=held,
                  full_tasks_finishing=running, models=submissions, report_job=report)
    (base / 'schedule.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    args = parser.parse_args()
    schedule(args.base)
