"""Watch this UFV deployment once/minute and copy terminal run artifacts locally."""
import json
import subprocess
import time
import tarfile
from datetime import datetime, timezone
from pathlib import Path

LOCAL = Path(__file__).resolve().parents[2]
DEST = LOCAL / 'hpc/logs/ufv-20261020'
DEST.mkdir(parents=True, exist_ok=True)
REMOTE = '/home/babaei/projects/MORPH-FL-ufv-20261020'
SMOKE = 'ufv-smoke-20261020-01'
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', '-o',
           'ControlPath=' + str(Path.home() / '.ssh/controlmasters/%r@%h:%p')]
HOST = 'babaei@slurm.soc.ufv.ca'
SCRIPT = r'''
import json, subprocess
from pathlib import Path
root = Path('/home/babaei/projects/MORPH-FL-ufv-20261020/hpc/logs')
smoke = 'ufv-smoke-20261020-01'
receipt = root / smoke / 'full_continuation.json'
r = json.loads(receipt.read_text()) if receipt.exists() else {}
run = r.get('full_run', smoke)
accounting = subprocess.run(['sacct', '-n', '-P', '-j', '17822,17832,17833', '--format=JobIDRaw,State,ExitCode'], capture_output=True, text=True)
gate = subprocess.run(['scontrol', 'show', 'job', '17833', '-o'], capture_output=True, text=True, timeout=15)
active = subprocess.run(['squeue', '-h', '-u', 'babaei', '-o', '%A|%T'], capture_output=True, text=True)
collected = root / run / 'results'
artifacts = {str(p.relative_to(collected)): p.stat().st_size for p in collected.rglob('*') if p.is_file()} if collected.exists() else {}
jobs = root / run / 'jobs.tsv'
ids = [line.split('\t')[0] for line in jobs.read_text().splitlines()] if jobs.exists() else []
active_ids = {line.split('|')[0] for line in active.stdout.splitlines()}
done = bool(ids) and not (set(ids) & active_ids) and active.returncode == 0
print(json.dumps(dict(run=run, continuation=r.get('state'), done=done, accounting=accounting.stdout, gate=gate.stdout, active=active.stdout, jobs=ids, remote_results=str(collected), artifacts=artifacts)))
'''

def copy(run):
    target = DEST / run
    target.mkdir(parents=True, exist_ok=True)
    command = ['ssh', *OPTIONS, HOST,
               'tar -cf - --exclude=graphs.tar.gz --exclude=evidence_archives.tar.gz -C '
               + REMOTE + '/hpc/logs/' + run + ' .']
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
            archive.extractall(target, filter='data')
        if process.wait() != 0:
            raise RuntimeError('Remote result transfer failed')

# Preserve the once/minute limit across watcher restarts.
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
        (DEST / 'status.json').write_text(json.dumps(state, indent=2) + '\n')
        print(json.dumps(state), flush=True)
        if state['done']:
            copy(state['run'])
            if state['run'] != SMOKE:
                copy(SMOKE)
                break
            # Leave time for the scheduled continuation to validate and submit.
            if state['continuation'] == 'submission_failed_needs_repair':
                break
            if any('JobState=' + status in state['gate'] for status in ('CANCELLED', 'FAILED', 'TIMEOUT', 'OUT_OF_MEMORY')):
                break
    except Exception as error:
        print(str(error), flush=True)
    time.sleep(60)
