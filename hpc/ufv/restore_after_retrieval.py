"""Idempotently restore this run's stopped graph only after retrieval is verified.

Invoked on the Slurm login host by the temporary comp370 recovery cron entry.
No inference or analysis executes on the login host.
"""
import argparse
import fcntl
import importlib.util
import json
import subprocess
import time
from pathlib import Path


def restore(deployment, run, work='/home/babaei/morph-ufv'):
    root = Path(deployment)
    logs = root/'hpc/logs'/run
    repair = logs/'maintenance/ast-recovery-20261020'
    record_path = repair/'restored_graph.json'
    with (repair/'restore.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(record_path.read_text()) if record_path.exists() else dict(jobs={}, commands=[])
        if state.get('complete'):
            return state
        def save():
            temporary = record_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(state, indent=2)+'\n')
            temporary.replace(record_path)
        results = Path(work)/'runs'/run/'results'
        receipt_path = results/'receipts/retrieval__m0__s1__p0.json'
        if not receipt_path.exists():
            return dict(complete=False, reason='Waiting for verified retrieval receipt')
        receipt = json.loads(receipt_path.read_text())
        manifest = json.loads((results/'data/manifest.json').read_text())
        expected = manifest['unique_cases'] * 2
        if receipt.get('complete') is not True or receipt.get('records') != expected:
            raise ValueError('Retrieval receipt does not establish exact full coverage')
        validation = json.loads((repair/'validation.json').read_text())
        if not validation.get('complete'):
            raise ValueError('AST validation incomplete')
        for index in range(5):
            gate = json.loads((results/f'models/{index}.preflight.json').read_text())
            if not (gate.get('complete') and gate.get('valid_hypotheses', 0)>0 and gate.get('output_tokens', 0)>0 and gate.get('budget')==32000):
                raise ValueError('Invalid inference gate: '+str(index))
        module_spec = importlib.util.spec_from_file_location('repair_submit', root/'hpc/slurm/submit.py')
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        config = json.loads((logs/'config/experiments.resolved.json').read_text())
        cluster = module.H.source_env(logs/'config/cluster.env')
        selected = [s for s in config['stages'] if s['name']=='collect' or any(s['name'].startswith(t+'_m') for t in ('main','ablations','budgets','misdirection','policy'))]
        for stage in selected:
            if stage['name'] in state['jobs']:
                continue
            deps = [d.get('type','afterok')+':'+state['jobs'][d['stage']]
                    for d in stage.get('depends', []) if d['stage'] in state['jobs']]
            command = module.sbatch_cmd(stage, config, cluster, run, deps, None)
            process = subprocess.run(command, capture_output=True, text=True)
            state['commands'].append(dict(command=command, rc=process.returncode, stdout=process.stdout, stderr=process.stderr))
            if process.returncode:
                save()
                events_path = repair/'events.json'
                events = json.loads(events_path.read_text()) if events_path.exists() else []
                event = dict(kind='maintenance', stage=stage['name'], rc=str(process.returncode),
                             detail='Recovery sbatch failed: '+process.stderr,
                             command=' '.join(command), log=str(record_path), resolved=False)
                if event not in events:
                    events.append(event)
                    events_path.write_text(json.dumps(events,indent=2)+'\n')
                raise RuntimeError('sbatch failed: '+process.stderr)
            job = process.stdout.strip().split(';')[0]
            state['jobs'][stage['name']] = job
            save()
            with (logs/'jobs.tsv').open('a') as stream:
                stream.write(f"{job}\t{stage['name']}\t{len(stage['cells'])}\t{','.join(deps)}\t{time.strftime('%F %T')}\n")
        state.update(complete=True, retrieval_records=expected,
                     restored_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        save()
        events_path = repair/'events.json'
        events = json.loads(events_path.read_text())
        for event in events:
            event['resolved'] = True
        events.append(dict(kind='maintenance', stage='main_dependency_recovery', job='17937-17941,17974-17978',
                           rc='DEPENDENCY_CANCELLED', detail='Superseded primary arrays canceled following retrieval failures; complete replacement graph submitted after verified retrieval. '+json.dumps(state['jobs'],sort_keys=True),
                           log=str(logs/'jobs.tsv'), ledger=str(record_path), resolved=True))
        events_path.write_text(json.dumps(events,indent=2)+'\n')
        return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    print(json.dumps(restore(args.deployment,args.run_id)))
