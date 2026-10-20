"""Watch a UFV run once/minute and retrieve terminal results over SSH."""
import argparse
import json
import re
import shlex
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from study_tracker import DOCUMENT, update_document

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--deployment', default='/home/babaei/projects/MORPH-FL-full-v12-20261020')
parser.add_argument('--run-id', default='ufv-full-v12-20261020-01')
parser.add_argument('--destination', type=Path)
parser.add_argument('--tracker-document', type=Path, default=DOCUMENT)
args = parser.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_.-]+', args.run_id):
    parser.error('Invalid run identifier')
LOCAL = Path(__file__).resolve().parents[2]
DEST = args.destination or LOCAL / 'hpc/logs/ufv-full-v12-20261020'
DEST.mkdir(parents=True, exist_ok=True)
REMOTE = args.deployment
RUN = args.run_id
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', '-o',
           'ControlPath=' + str(Path.home() / '.ssh/controlmasters/%r@%h:%p')]
HOST = 'babaei@slurm.soc.ufv.ca'
SCRIPT = f'root_path = {REMOTE!r}\nrun = {RUN!r}\n' + r'''
import json, subprocess
from pathlib import Path
root = Path(root_path) / 'hpc/logs' / run
jobs = root / 'jobs.tsv'
ids = [line.split('\t')[0] for line in jobs.read_text().splitlines()] if jobs.exists() else []
active = subprocess.run(['squeue', '-h', '-u', 'babaei', '-o', '%F|%T'], capture_output=True, text=True, timeout=20)
lines = [line for line in active.stdout.splitlines() if line.split('|')[0] in set(ids)]
active_ids = {line.split('|')[0] for line in lines}
collected = root / 'results'
artifacts = {str(p.relative_to(collected)): p.stat().st_size for p in collected.rglob('*') if p.is_file()} if collected.exists() else {}
report = collected / 'raw/analysis/completeness.json'
complete = json.loads(report.read_text()) if report.exists() else None
done = bool(ids) and not (set(ids) & active_ids) and active.returncode == 0
state = dict(run=run, done=done, scientific_completeness=complete, active='\n'.join(lines), jobs=ids, remote_results=str(collected), artifacts=artifacts)
state['tracker'] = inspect_run(root_path, run)
print(json.dumps(state))
'''
SCRIPT = Path(__file__).with_name('tracker_snapshot.py').read_text() + '\n' + SCRIPT


def copy_results():
    target = DEST / RUN
    target.mkdir(parents=True, exist_ok=True)
    source = REMOTE + '/hpc/logs/' + RUN
    command = ['ssh', *OPTIONS, HOST,
               'tar -cf - --exclude=graphs.tar.gz --exclude=evidence_archives.tar.gz -C '
               + shlex.quote(source) + ' .']
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
            archive.extractall(target, filter='data')
        if process.wait() != 0:
            raise RuntimeError('Remote result transfer failed')


# Preserve the once/minute scheduler limit across watcher restarts.
status_path = DEST / 'status.json'
if status_path.exists():
    previous = json.loads(status_path.read_text()).get('checked_utc')
    if previous:
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(previous.replace('Z', '+00:00'))).total_seconds()
        time.sleep(max(0, 60 - elapsed))
while True:
    try:
        process = subprocess.run(['ssh', *OPTIONS, HOST, 'python3 -'], input=SCRIPT,
                                 text=True, capture_output=True, timeout=50, check=True)
        state = json.loads(process.stdout)
        state['checked_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        status_path.write_text(json.dumps(state, indent=2) + '\n')
        (DEST / 'study-progress.json').write_text(json.dumps(state, indent=2) + '\n')
        update_document(state, args.tracker_document)
        progress = state.get('tracker', {}).get('progress', {})
        print(json.dumps(dict(run=state['run'], done=state['done'], checked_utc=state['checked_utc'],
                              study_progress_records=sum(v.get('completed', 0) for k,v in progress.items()
                                                         if not k.startswith('preflight__')))), flush=True)
        if state['done']:
            copy_results()
            state['collected_locally'] = str((DEST / RUN).resolve())
            status_path.write_text(json.dumps(state, indent=2) + '\n')
            (DEST / 'study-progress.json').write_text(json.dumps(state, indent=2) + '\n')
            update_document(state, args.tracker_document)
            break
    except Exception as error:
        print(str(error), flush=True)
    time.sleep(60)
