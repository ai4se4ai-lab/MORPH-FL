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
