"""Read bounded live prediction snapshots and publish an explicitly partial report."""
import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

try:
    from .manage import VARIANTS, brief, digest, report, rows, write_json
except ImportError:
    from manage import VARIANTS, brief, digest, report, rows, write_json


def completed_rows(path, limit):
    with path.open('rb') as stream:
        while stream.tell() < limit:
            line = stream.readline(limit - stream.tell())
            if not line.endswith(b'\n'):
                return
            if line.strip():
                yield json.loads(line)


def snapshot(results):
    from experiments.full import suite
    suite.locked()
    manifest = json.loads((results / 'pilot.json').read_text())
    if digest(Path(__file__).with_name('manage.py')) != manifest['wrapper_sha256']:
        raise ValueError('Frozen pilot wrapper changed')
    if digest(results / 'data/cases.jsonl') != manifest['cases_sha256']:
        raise ValueError('Prepared subjects changed')
    if digest(suite.ROOT / 'experiments/full/protocol.json') != manifest['protocol_sha256']:
        raise ValueError('Frozen protocol changed')
    subjects = list(rows(results / 'data/cases.jsonl'))
    labels = {r['instance_id']: r for r in rows(results / 'data/labels.jsonl')}
    selected = set(manifest['selected_ids'])
    pins = json.loads((suite.ROOT / 'experiments/full/pins.json').read_text())['models']
    expected = {(pins[m]['id'], 1, i, v) for m in manifest['models']
                for i in selected for v in VARIANTS}
    records, seen, inputs = [], set(), []
    for path in sorted((results / 'predictions').glob('main*.jsonl')):
        settings = json.loads(path.with_suffix('.config.json').read_text())
        if settings['protocol_sha256'] != manifest['protocol_sha256']:
            raise ValueError('Protocol mismatch')
        # A self-consistent signature proves agreement with the saved config,
        # not that the config belongs to the frozen pilot.
        model = next((m for m in manifest['models']
                      if pins[m]['id'] == settings['model']['id']), None)
        if (model is None or settings['model']['revision'] != pins[model]['revision']
                or settings['track'] != 'main' or settings['seed'] != manifest['seed']
                or settings['shards'] != manifest['shards'] or settings['smoke']
                or settings.get('preflight', False)
                or type(settings['shard']) is not int
                or not 0 <= settings['shard'] < manifest['shards']):
            raise ValueError('Prediction configuration differs from frozen pilot settings')
        cell = f"main__m{model}__s{manifest['seed']}__p{settings['shard']}"
        if path.stem != cell:
            raise ValueError('Prediction filename differs from frozen shard identity')
        signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
        shard_cases = [c for c in subjects[settings['shard']::settings['shards']]
                       if c['instance_id'] in selected]
        limit = path.stat().st_size
        inputs.append(dict(path=str(path), snapshot_bytes=limit))
        def validated():
            for row in completed_rows(path, limit):
                key = (row['model_id'], row['seed'], row['instance_id'], row['variant'])
                if key not in expected or key in seen or row['budget'] != manifest['budget']:
                    raise ValueError('Duplicate or unplanned prediction')
                seen.add(key)
                records.append(brief(row, labels[row['instance_id']]))
                yield row
        suite.resume_keys(validated(), shard_cases, settings, signature)
    destination = results / 'interim-analysis'
    report(records, destination, 'Fast pilot — partial snapshot on fixed subjects')
    write_json(destination / 'completeness.json', dict(
        expected=len(expected), observed=len(seen), missing=len(expected-seen),
        complete=seen == expected, checked_utc=datetime.now(UTC).isoformat(), inputs=inputs))
    with (destination / 'report.md').open('a') as out:
        out.write(f'\nSnapshot coverage: **{len(seen)}/{len(expected)} primary records**. '
                  'Only issues complete for all four workflows enter each model table; '
                  'unfinished issues can change these estimates.\n')
    print(json.dumps(dict(observed=len(seen), expected=len(expected))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    snapshot(parser.parse_args().results)
