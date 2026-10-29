"""Lightweight remote metadata reader; no inference or analysis on the login host."""
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path


def inspect_run(root_path, run):
    errors = []

    def read(path, default=None):
        try:
            return json.loads(path.read_text()) if path.exists() else default
        except (OSError, ValueError) as error:
            errors.append(f'{path}: {error}')
            return default

    repo = Path(root_path)
    logs = repo / 'hpc/logs' / run
    manifest = read(logs / 'run_manifest.json', {})
    work = Path(manifest.get('cluster_env', {}).get('WORK', '/home/babaei/morph-ufv'))
    results = work / 'runs' / run / 'results'
    config = read(logs / 'config/experiments.resolved.json', {})
    pins = read(repo / 'experiments/full/pins.json', {})
    protocol = read(repo / 'experiments/full/protocol.json', {})
    cache_dir = work / 'monitor-cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / (run + '-tracker.json')
    previous = read(cache_path, {})
    files = {}
    for path in sorted((results / 'progress').glob('*.jsonl')):
        stat = path.stat()
        old = previous.get(path.name, {})
        valid = old.get('inode') == stat.st_ino and old.get('offset', 0) <= stat.st_size
        offset = old.get('offset', 0) if valid else 0
        counts = Counter(old.get('conditions', {}) if valid else {})
        count = old.get('completed', 0) if valid else 0
        with path.open('rb') as source:
            source.seek(offset)
            appended = source.read()
        boundary = appended.rfind(b'\n') + 1
        for line in appended[:boundary].splitlines():
            if not line.strip():
                continue
            try:
                key = json.loads(line)['key']
                counts[str(key[1]) + '@' + str(key[2]) + '@' + str(key[3])] += 1
                count += 1
            except (ValueError, KeyError, IndexError) as error:
                errors.append(f'{path.name}: invalid progress record: {error}')
        expected = read(path.with_suffix('.json'), {}).get('expected')
        files[path.name] = dict(inode=stat.st_ino, offset=offset + boundary,
                               completed=count, conditions=dict(counts), expected=expected)
    temporary = cache_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(files))
    temporary.replace(cache_path)
    latest = {}
    attempts = []
    ledger = logs / 'steps.tsv'
    if ledger.exists():
        for row in csv.DictReader(io.StringIO(ledger.read_text()), delimiter='\t'):
            latest[(row['stage'], row['cell'], row['step'])] = row
            attempts.append(row)
    failure_events = []
    for attempt in attempts:
        if attempt.get('rc') == '0':
            continue
        event = dict(attempt, kind='step')
        key = (attempt['stage'], attempt['cell'], attempt['step'])
        event['resolved'] = latest[key].get('rc') == '0'
        path = logs / 'steps' / attempt['stage'] / attempt['cell'] / (attempt['step'] + '.log')
        event['log'] = str(path)
        event['ledger'] = str(ledger)
        if path.resolve().is_relative_to(logs.resolve()) and path.exists():
            with path.open('rb') as source:
                source.seek(max(0, path.stat().st_size - 4096))
                event['tail'] = source.read(4096).decode('utf-8', errors='replace')
        failure_events.append(event)
    # Runtime repairs and validation attempts live outside the original frozen graph.
    for event_path in sorted((logs / 'maintenance').glob('*/events.json')):
        failure_events.extend(read(event_path, []))
    finished = logs / 'jobs_finished.tsv'
    if finished.exists():
        for line in finished.read_text().splitlines():
            fields = line.split('\t')
            if len(fields) >= 7 and fields[5].startswith('FAILED'):
                timestamp, job, stage, cell, restart, outcome, host = fields[:7]
                if any(e.get('job') == job and e.get('kind') == 'step' for e in failure_events):
                    continue
                later_success = any(r.get('stage') == stage and r.get('cell') == cell and r.get('rc') == '0' for r in latest.values())
                failure_events.append(dict(kind='job', time=timestamp, job=job, stage=stage,
                    cell=cell, restart=restart, rc=outcome, detail='Host: ' + host,
                    log=str(logs / 'slurm'), ledger=str(finished), resolved=later_success))
    stages = []
    jobs_by_stage = {}
    job_file = logs / 'jobs.tsv'
    if job_file.exists():
        for line in job_file.read_text().splitlines():
            fields = line.split('\t')
            if len(fields) >= 2:
                jobs_by_stage.setdefault(fields[1], []).append(fields[0])
    for stage in config.get('stages', []):
        rows = [v for k, v in latest.items() if k[0] == stage['name']]
        expected_steps = len(stage.get('cells', [{}])) * len(stage.get('steps', []))
        stages.append(dict(name=stage['name'], jobs=jobs_by_stage.get(stage['name'], []), cells=len(stage.get('cells', [{}])),
                           expected_steps=expected_steps,
                           successful_steps=sum(r['rc'] == '0' for r in rows),
                           failures=[{k:r.get(k) for k in ('cell','step','rc','note','job','time')} for r in rows if r['rc'] != '0']))
    summary_path = results / 'analysis/summary.csv'
    summary = []
    if summary_path.exists():
        with summary_path.open() as source:
            summary = list(csv.DictReader(source))
    analysis_overviews = {}
    paired = read(results / 'analysis/paired.json')
    if paired is not None:
        analysis_overviews['paired.json'] = f'{len(paired)} paired metric comparisons stored; intervals and directions remain in the detailed file.'
    comparisons = read(results / 'analysis/primary_comparisons.json')
    if comparisons is not None:
        tests = comparisons.get('comparisons', [])
        significant = sum(v.get('confirmatory', False) and v.get('holm_p') is not None and v['holm_p'] < .05 for v in tests)
        analysis_overviews['primary_comparisons.json'] = f'{len(tests)} comparisons; {significant} confirmatory Holm-adjusted p-values below .05. Consult effect directions and uncertainty; this is not a causal claim.'
    retention = read(results / 'analysis/reset_retention.json')
    if retention is not None:
        analysis_overviews['reset_retention.json'] = f'{len(retention)} reset-retention event records stored; retention does not establish recovery.'
    for name in ('budget_points.csv', 'recovery_summary.csv'):
        path = results / 'analysis' / name
        if path.exists():
            with path.open() as source:
                records = list(csv.DictReader(source))
            analysis_overviews[name] = f'{len(records)} measured summary rows stored; consult matching subjects and eligible denominators.'
    receipts = {p.stem: read(p, {}) for p in sorted((results / 'receipts').glob('*.json'))}
    preflights = {p.stem.split('.')[0]: read(p, {}) for p in sorted((results / 'models').glob('*.preflight.json'))}
    downloaded = {p.stem.split('.')[0]: read(p, {}) for p in sorted((results / 'models').glob('*.pin.json'))}
    return dict(run=run, deployment=str(repo), results=str(results), log_root=str(logs),
                models=pins.get('models', []), protocol=protocol,
                data=read(results / 'data/manifest.json', {}), stages=stages,
                progress=files, receipts=receipts, preflights=preflights, downloaded=downloaded,
                completeness=read(results / 'analysis/completeness.json'), summary_rows=summary,
                analysis_overviews=analysis_overviews,
                analysis_files=[p.name for p in sorted((results / 'analysis').glob('*')) if p.is_file()],
                errors=errors, failure_events=failure_events,
                runtime_maintenance=read(repo / 'experiments/full/runtime_maintenance.json'),
                maintenance_validation=read(logs / 'maintenance/ast-recovery-20261020/validation.json'),
                maintenance_recovery=read(logs / 'maintenance/ast-recovery-20261020/restored_graph.json') or read(logs / 'maintenance/ast-recovery-20261020/retrieval-retry.json'))
