"""Reuse the identical pinned benchmark preparation without recomputing snapshots."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--source', required=True, type=Path)
p.add_argument('--out', required=True, type=Path)
a = p.parse_args()
source = a.source.resolve()
manifest = json.loads((source / 'manifest.json').read_text())
pins = json.loads((Path(__file__).resolve().parents[2] / 'experiments/full/pins.json').read_text())
if manifest['datasets'] != pins['datasets'] or manifest.get('smoke'):
    raise ValueError('Prepared datasets differ from the full frozen benchmark pins')
if sorted(manifest['benchmark_sizes'].values()) != [300, 500]:
    raise ValueError('Expected complete Lite/Verified preparation')
for name in ('cases.jsonl', 'labels.jsonl', 'membership.json'):
    if not (source / name).is_file():
        raise ValueError('Missing prepared input: ' + name)
membership = json.loads((source / 'membership.json').read_text())
expected_sizes = {'SWE-bench_Lite': 300, 'SWE-bench_Verified': 500}
if set(membership) != set(expected_sizes):
    raise ValueError('Unexpected benchmark membership names')
for name, size in expected_sizes.items():
    ids = membership[name]
    if len(ids) != size or len(set(ids)) != size:
        raise ValueError('Incomplete or duplicate benchmark membership: ' + name)
if manifest['benchmark_sizes'] != expected_sizes:
    raise ValueError('Manifest benchmark sizes differ from membership')
union = set().union(*(set(ids) for ids in membership.values()))
overlap = len(set.intersection(*(set(ids) for ids in membership.values())))
if manifest.get('unique_cases') != len(union) or manifest.get('overlap') != overlap:
    raise ValueError('Manifest union/overlap differs from membership')
case_revisions = {}
for name in ('cases.jsonl', 'labels.jsonl'):
    rows = [json.loads(line) for line in (source / name).read_text().splitlines() if line.strip()]
    ids = [row['instance_id'] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != union:
        raise ValueError('Prepared input coverage differs from membership: ' + name)
    for row in rows:
        if name == 'cases.jsonl':
            case_revisions[row['instance_id']] = row['revision']
            if not Path(row['archive']).is_file():
                raise ValueError('Missing source archive: ' + row['instance_id'])
        elif row['revision'] != case_revisions[row['instance_id']]:
            raise ValueError('Label revision differs from source: ' + row['instance_id'])
a.out.parent.mkdir(parents=True, exist_ok=True)
if a.out.is_symlink():
    if a.out.resolve() != source:
        raise ValueError('Existing dataset link differs')
elif a.out.exists():
    raise ValueError('Refusing to overwrite existing dataset directory')
else:
    a.out.symlink_to(source, target_is_directory=True)
(a.out.parent / 'data_reuse.json').write_text(json.dumps(dict(source=str(source), manifest=manifest), indent=2)+'\n')
print(json.dumps(manifest, indent=2))
