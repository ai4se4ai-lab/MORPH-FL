"""Verify the completed pilot and collect retrieval/output-quality diagnostics."""
import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

try:
    from .manage import brief, rows, write_json
    from .quality import inspect
    from .snapshot import snapshot
except ImportError:
    from manage import brief, rows, write_json
    from quality import inspect
    from snapshot import snapshot


def verify_receipts(results):
    """Account for imported and receipted keys without counting resumed keys twice."""
    predictions = {}
    for path in sorted((results / 'predictions').glob('main*.jsonl')):
        keys = [(row['instance_id'], row['variant']) for row in rows(path)]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate primary prediction')
        predictions[path.stem] = set(keys)
    imported = set()
    reuse = json.loads((results / 'reuse.json').read_text())
    for row in reuse['records']:
        if not row['file'].startswith('main__'):
            continue
        cell = Path(row['file']).stem
        key = (row['instance_id'], row['variant'])
        identity = (cell, *key)
        if identity in imported or key not in predictions.get(cell, set()):
            raise ValueError('Duplicate or missing imported prediction')
        imported.add(identity)
    covered = set(imported)
    receipts = list((results / 'receipts').glob('main*.json'))
    for path in receipts:
        receipt = json.loads(path.read_text())
        keys = predictions.get(path.stem)
        if (receipt.get('cell') != path.stem or receipt.get('complete') is not True
                or keys is None or receipt.get('records') != len(keys)):
            raise ValueError('Receipt disagrees with its prediction cell')
        covered.update((path.stem, *key) for key in keys)
    actual = {(cell, *key) for cell, keys in predictions.items() for key in keys}
    if covered != actual:
        raise ValueError('Primary predictions lack import provenance or a completion receipt')
    return dict(imported_primary_records=len(imported), successful_new_cells=len(receipts),
                new_receipt_records=len(actual - imported))


def finalize(results):
    from experiments.full import suite
    snapshot(results)
    verified = json.loads((results / 'interim-analysis/completeness.json').read_text())
    final = json.loads((results / 'analysis/completeness.json').read_text())
    if not verified['complete'] or not final['complete']:
        raise ValueError('Pilot incomplete')
    inspect(results, results / 'analysis/quality.json')
    quality = json.loads((results / 'analysis/quality.json').read_text())
    if any(g['records'] != 50 for g in quality['variants'].values()) or len(quality['variants']) != 4:
        raise ValueError('Quality diagnostics lack complete coverage')
    quality['note'] = 'Complete DeepSeek pilot: same 50 issues per workflow.'
    write_json(results / 'analysis/quality.json', quality)
    manifest = json.loads((results / 'pilot.json').read_text())
    labels = {r['instance_id']: r for r in rows(results / 'data/labels.jsonl')}
    cases = [r for r in rows(results / 'data/cases.jsonl') if r['instance_id'] in manifest['selected_ids']]
    controls, keys = [], set()
    for path in sorted((results / 'predictions').glob('retrieval*.jsonl')):
        settings = json.loads(path.with_suffix('.config.json').read_text())
        signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
        if settings['protocol_sha256'] != manifest['protocol_sha256']:
            raise ValueError('Retrieval protocol differs')
        original = list(rows(path))
        suite.resume_keys(original, cases, settings, signature)
        for row in original:
            key = (row['instance_id'], row['variant'])
            if key in keys:
                raise ValueError('Duplicate retrieval control')
            keys.add(key)
            controls.append(brief(row, labels[row['instance_id']]))
    expected = {(i, v) for i in manifest['selected_ids'] for v in ['bm25', 'graph']}
    if keys != expected:
        raise ValueError('Retrieval controls incomplete')
    summary = []
    for variant in ['bm25', 'graph']:
        eligible = [r for r in controls if r['variant'] == variant and r['eligible']]
        summary.append(dict(variant=variant, issues=len(eligible),
                            **{k: sum(r[k] for r in eligible)/len(eligible) for k in ['top1', 'top5', 'top10', 'mrr']}))
    write_json(results / 'analysis/controls.json', dict(summary=summary, scores=controls))
    accounting = verify_receipts(results)
    if accounting['imported_primary_records'] + accounting['new_receipt_records'] != verified['observed']:
        raise ValueError('Receipts and imported records disagree')
    write_json(results / 'analysis/final-verification.json', dict(
        checked_utc=datetime.now(UTC).isoformat(), complete=True,
        verified_primary_records=verified['observed'], verified_control_records=len(keys),
        **accounting,
        protocol_sha256=manifest['protocol_sha256']))
    print(json.dumps(dict(complete=True, primary=400, retrieval=len(keys))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    finalize(parser.parse_args().results)
