"""Subset orchestration around the frozen full runner; never modify full-run outputs."""
import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

VARIANTS = ['morph', 'no_forgetting', 'fixed_reset', 'stateless_summary']


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def select(cases, excluded, count=50):
    groups = defaultdict(list)
    for case in cases:
        if case['instance_id'] not in excluded:
            groups[case['repo']].append(case['instance_id'])
    for group in groups.values():
        group.sort(key=lambda x: hashlib.sha256(('morph-pilot-v1:' + x).encode()).hexdigest())
    selected = []
    while len(selected) < count and any(groups.values()):
        for repo in sorted(groups):
            if groups[repo] and len(selected) < count:
                selected.append(groups[repo].pop(0))
    if len(selected) != count:
        raise ValueError('Insufficient eligible subjects')
    return selected


def brief(row, label):
    from morph_fl.evaluation.metrics import metrics
    if row['revision'] != label['revision']:
        raise ValueError('Label revision mismatch')
    result = {k: row.get(k) for k in [
        'instance_id', 'repo', 'seed', 'variant', 'model_id', 'budget',
        'input_tokens', 'output_tokens', 'end_to_end_seconds', 'resets', 'abstained']}
    result.update(metrics(row['ranking'], label['files']))
    result.update({'function_' + k: v for k, v in
                   metrics(row.get('function_ranking', []), label.get('functions', [])).items()})
    result['has_hypotheses'] = bool(row.get('hypotheses'))
    result['tokens'] = (row.get('input_tokens') or 0) + (row.get('output_tokens') or 0)
    return result


def report(records, output, title):
    output.mkdir(parents=True, exist_ok=True)
    if records:
        with (output / 'scores.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    lines = [f'# {title}', '', 'Exploratory localization against unreviewed patch-change proxies. '
             'Completed-case cost excludes interrupted attempts. No full-study completion claim.', '']
    summary = []
    for model in sorted({r['model_id'] for r in records}):
        grouped = defaultdict(dict)
        for row in records:
            if row['model_id'] == model and row['seed'] == 1 and row['variant'] in VARIANTS:
                if row['variant'] in grouped[row['instance_id']]:
                    raise ValueError('Duplicate model/case/workflow')
                grouped[row['instance_id']][row['variant']] = row
        paired = [g for g in grouped.values() if set(g) == set(VARIANTS)
                  and all(r['eligible'] for r in g.values())]
        lines += [f'## {model}', '', f'{len(paired)} issues have all four workflows and eligible file labels.', '',
                  '| Workflow | File Top1 | File Top5 | Function Top1 | Mean tokens | Mean seconds | Mean resets |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for variant in VARIANTS:
            rs = [g[variant] for g in paired]
            def mean(key):
                vals = [r[key] for r in rs if r.get(key) is not None]
                return sum(vals) / len(vals) if vals else None
            item = dict(model=model, variant=variant, paired_issues=len(rs),
                        **{k: mean(k) for k in ['top1', 'top5', 'function_top1', 'tokens',
                                               'end_to_end_seconds', 'resets']})
            summary.append(item)
            def fmt(key, percent=False):
                v = item[key]
                return 'NA' if v is None else (f'{100*v:.1f}%' if percent else f'{v:.1f}')
            lines.append(f'| {variant} | {fmt("top1", True)} | {fmt("top5", True)} | '
                         f'{fmt("function_top1", True)} | {fmt("tokens")} | '
                         f'{fmt("end_to_end_seconds")} | {fmt("resets")} |')
        lines += ['', 'Paired MORPH minus comparator File Top1 differences; descriptive 95% '
                  'repository-cluster bootstrap intervals (2,000 draws):', '']
        for comparator in VARIANTS[1:]:
            clusters = defaultdict(list)
            for g in paired:
                clusters[g['morph']['repo']].append(g['morph']['top1'] - g[comparator]['top1'])
            if not clusters:
                continue
            values = list(clusters.values())
            delta = sum(map(sum, values)) / sum(map(len, values))
            rng = random.Random(20261024)
            samples = []
            for _ in range(2000):
                sample = [rng.choice(values) for _ in values]
                samples.append(sum(map(sum, sample)) / sum(map(len, sample)))
            samples.sort()
            lines.append(f'- {comparator}: {delta*100:+.1f} percentage points '
                         f'[{samples[49]*100:+.1f}, {samples[1949]*100:+.1f}]; '
                         f'{len(values)} repositories.')
        lines += ['']
    write_json(output / 'summary.json', summary)
    (output / 'report.md').write_text('\n'.join(lines) + '\n')


def prepare(args):
    from experiments.full import suite
    suite.locked()
    source, target = Path(args.source), Path(args.results)
    target.mkdir(parents=True, exist_ok=True)
    if (target / 'pilot.json').exists():
        raise ValueError('Pilot already prepared; refusing overwrite')
    cases = list(rows(source / 'data/cases.jsonl'))
    excluded = json.loads((suite.ROOT / 'experiments/full/prior_cases.json').read_text())['previously_inspected']
    ids = select(cases, set(excluded))
    manifest = dict(study='morph-pilot-v1', selected_ids=ids, excluded_prior_ids=excluded,
                    models=[0, 1], seed=1, variants=VARIANTS, budget=32000, rounds=16,
                    shards=32, source=str(source), frozen_root=str(suite.ROOT),
                    protocol_sha256=digest(suite.ROOT / 'experiments/full/protocol.json'),
                    wrapper_sha256=digest(__file__),
                    cases_sha256=digest(source / 'data/cases.jsonl'),
                    created_utc=datetime.now(timezone.utc).isoformat(),
                    note='Selected by repository/hash before reading outcomes; existing full-run '
                         'predictions may be reused. This is exploratory, not untouched confirmation data.')
    # Freeze selection before opening any predictions or labels.
    write_json(target / 'pilot.json', manifest)
    for name in ['data', 'models']:
        (target / name).symlink_to(source / name, target_is_directory=True)
    for name in ['predictions', 'receipts', 'graphs', 'progress']:
        (target / name).mkdir()
    labels = {r['instance_id']: r for r in rows(source / 'data/labels.jsonl')}
    pins = json.loads((suite.ROOT / 'experiments/full/pins.json').read_text())['models']
    model_ids = {pins[i]['id'] for i in manifest['models']}
    by_id = {c['instance_id']: c for c in cases}
    records, reuse, inputs = [], [], []
    # Only seed 1, primary study, plus inexpensive deterministic controls.
    files = sorted((source / 'predictions').glob('main__m[01]__s1__p*.jsonl'))
    files += sorted((source / 'predictions').glob('retrieval__*.jsonl'))
    for path in files:
        limit = path.stat().st_size
        print(json.dumps(dict(event='snapshot', file=str(path), bytes=limit)), flush=True)
        inputs.append(dict(path=str(path), snapshot_bytes=limit))
        settings = json.loads(path.with_suffix('.config.json').read_text())
        signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
        snapshot_hash = hashlib.sha256()
        with path.open('rb') as f:
            while f.tell() < limit:
                line = f.readline(limit - f.tell())
                snapshot_hash.update(line)
                if not line.endswith(b'\n'):
                    break  # A live writer's incomplete final record is not a result.
                if not line.strip():
                    continue
                row = json.loads(line)
                case = by_id[row['instance_id']]
                if row['run_signature'] != signature or settings['protocol_sha256'] != manifest['protocol_sha256']:
                    raise ValueError('Source signature mismatch')
                if row['source_archive_sha256'] != case['archive_sha256'] or row['revision'] != case['revision']:
                    raise ValueError('Source provenance mismatch')
                if row['report_digest'] != hashlib.sha256(case['report'].encode()).hexdigest():
                    raise ValueError('Report provenance mismatch')
                if row['track'] == 'main' and (row['model_id'] not in model_ids or row['seed'] != 1
                        or row['model_revision'] != settings['model']['revision'] or row['budget'] != 32000):
                    raise ValueError('Unexpected primary settings')
                if row['track'] == 'main' and row['variant'] in VARIANTS:
                    records.append(brief(row, labels[row['instance_id']]))
                if row['instance_id'] not in ids or (row['track'] == 'main' and row['variant'] not in VARIANTS):
                    continue
                # Preserve original signatures and trace ownership; external artifacts remain at source.
                model = row.get('model', {})
                if 'structure_artifact' in model:
                    model['structure_artifact'] = str((path.parent / model['structure_artifact']).resolve())
                if row.get('evidence_archive'):
                    row['evidence_archive'] = str((source / row['evidence_archive']).resolve())
                dest = target / 'predictions' / path.name
                with dest.open('a') as out:
                    out.write(json.dumps(row) + '\n')
                dest.with_suffix('.config.json').write_text(json.dumps(settings, indent=2) + '\n')
                reuse.append(dict(file=path.name, instance_id=row['instance_id'], variant=row['variant']))
        inputs[-1]['snapshot_sha256'] = snapshot_hash.hexdigest()
    write_json(target / 'reuse.json', dict(inputs=inputs, records=reuse))
    report(records, target / 'existing-analysis', 'Existing completed Qwen comparisons — exploratory snapshot')
    planned = []
    for model in manifest['models']:
        for shard in range(32):
            subjects = {c['instance_id'] for c in cases[shard::32]} & set(ids)
            path = target / 'predictions' / f'main__m{model}__s1__p{shard}.jsonl'
            actual = {(r['instance_id'], r['variant']) for r in rows(path)} if path.exists() else set()
            expected = {(i, v) for i in subjects for v in VARIANTS}
            if not actual <= expected:
                raise ValueError('Imported prediction outside original shard')
            if expected - actual:
                planned.append(dict(model=model, shard=shard, missing=len(expected-actual)))
    write_json(target / 'pending.json', planned)
    print(json.dumps(dict(event='prepared', reused=len(reuse), pending_cells=len(planned))), flush=True)


def run(args):
    from experiments.full import suite
    target = Path(args.results)
    manifest = json.loads((target / 'pilot.json').read_text())
    if digest(__file__) != manifest['wrapper_sha256'] or digest(target / 'data/cases.jsonl') != manifest['cases_sha256']:
        raise ValueError('Pilot inputs changed')
    if digest(suite.ROOT / 'experiments/full/protocol.json') != manifest['protocol_sha256']:
        raise ValueError('Frozen protocol changed')
    if args.model not in manifest['models']:
        raise ValueError('Unplanned model')
    ids = set(manifest['selected_ids'])
    class Subjects(list):
        def __getitem__(self, key):
            value = super().__getitem__(key)
            return [r for r in value if r['instance_id'] in ids] if isinstance(key, slice) else value
    # Slice the ORIGINAL case order first, preserving full-run shard/signature identity.
    suite.selected_cases = lambda cases, track, smoke: Subjects(cases)
    original_jobs = suite.jobs_for
    suite.jobs_for = lambda track, smoke, preflight=False: [
        job for job in original_jobs(track, smoke, preflight) if job[0] in manifest['variants']]
    suite.run(SimpleNamespace(results=str(target), model=args.model, seed=1, shard=args.shard,
                              shards=32, smoke=0, track='main'))


def analyze(args):
    target = Path(args.results)
    manifest = json.loads((target / 'pilot.json').read_text())
    labels = {r['instance_id']: r for r in rows(target / 'data/labels.jsonl')}
    records, seen = [], set()
    for path in sorted((target / 'predictions').glob('main*.jsonl')):
        for row in rows(path):
            key = (row['model_id'], row['seed'], row['instance_id'], row['variant'])
            if key in seen or row['instance_id'] not in manifest['selected_ids']:
                raise ValueError('Duplicate or unplanned prediction')
            seen.add(key)
            records.append(brief(row, labels[row['instance_id']]))
    report(records, target / 'analysis', '50-issue two-model pilot')
    from experiments.full import suite
    pins = json.loads((suite.ROOT / 'experiments/full/pins.json').read_text())['models']
    expected = {(pins[m]['id'], 1, i, v) for m in manifest['models']
                for i in manifest['selected_ids'] for v in VARIANTS}
    if seen - expected:
        raise ValueError('Unplanned pilot settings')
    write_json(target / 'analysis/completeness.json', dict(expected=len(expected), observed=len(seen),
                                                        missing=len(expected-seen), complete=seen == expected))
    if seen != expected:
        raise SystemExit('Pilot incomplete; partial descriptive report preserved')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'analyze'])
    parser.add_argument('--source')
    parser.add_argument('--results', required=True)
    parser.add_argument('--model', type=int, default=0)
    parser.add_argument('--shard', type=int, default=0)
    args = parser.parse_args()
    globals()[args.command](args)
