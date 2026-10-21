"""Temporary comp370 cron callback for the explicitly requested October 20 repair."""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT/'hpc/logs/ufv-full-v12-20261020'
MARKER = '# MORPH-FL temporary retrieval recovery'
command = ['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','babaei@slurm.soc.ufv.ca',
           'cd /home/babaei/projects/MORPH-FL-full-v12-20261020 && python3 -m hpc.ufv.restore_after_retrieval --deployment /home/babaei/projects/MORPH-FL-full-v12-20261020 --run-id ufv-full-v12-20261020-01']
process = subprocess.run(command,capture_output=True,text=True,timeout=120)
print(datetime.now(timezone.utc).isoformat(),process.returncode,process.stdout,process.stderr,flush=True)
if process.returncode:
    (DEST/'recovery-status.json').write_text(json.dumps(dict(complete=False, error=process.stderr[-4096:]),indent=2)+'\n')
    raise SystemExit(process.returncode)
state = json.loads(process.stdout)
(DEST/'recovery-status.json').write_text(json.dumps(state,indent=2)+'\n')
if not state.get('complete'):
    # Metadata only: no inference, analysis, or scheduler polling on the compute node.
    try:
        probe = subprocess.run(['ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
            '-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/ufv_tracker_ed25519'),
            'babaei@node3.slurm.sc.ufv.ca','python3 -'],
            input=(ROOT/'hpc/ufv/recovery_io.py').read_text(),capture_output=True,text=True,timeout=20)
        if probe.returncode == 0:
            telemetry = json.loads(probe.stdout)
            telemetry['observed_utc'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            telemetry['node'] = 'node3'
            temporary = DEST/'recovery-io.json.tmp'
            temporary.write_text(json.dumps(telemetry,indent=2)+'\n')
            temporary.replace(DEST/'recovery-io.json')
        else:
            print('Recovery telemetry unavailable:',probe.stderr[-1000:],flush=True)
    
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('Optional recovery telemetry unavailable:',str(error),flush=True)
if state.get('complete'):
    old = subprocess.check_output(['crontab','-l'],text=True)
    new = '\n'.join(line for line in old.splitlines() if MARKER not in line)+'\n'
    if new != old:
        subprocess.run(['crontab','-'],input=new,text=True,check=True)
