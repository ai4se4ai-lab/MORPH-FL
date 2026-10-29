"""Read-only compact prediction export; execute on an allocated compute node."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root, out = map(Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
files = [(p, p.stat().st_size) for p in sorted((root / 'predictions').glob('*.jsonl'))
         if p.name.startswith(('main__', 'retrieval__', 'ablations__'))]
manifest = {'started_utc': datetime.now(timezone.utc).isoformat(), 'source': str(root), 'files': []}
keys = ['instance_id', 'repo', 'revision', 'track', 'model_id', 'model_revision', 'seed',
        'variant', 'budget', 'window', 'ranking', 'function_ranking', 'input_tokens',
        'output_tokens', 'seconds', 'end_to_end_seconds', 'resets', 'probe_count', 'abstained']
with (out / 'predictions.jsonl').open('w') as dest:
    for path, limit in files:
        consumed = count = 0
        digest = hashlib.sha256()
        with path.open('rb') as src:
            while consumed < limit:
                line = src.readline(limit - consumed)
                consumed += len(line)
                digest.update(line)
                if not line.endswith(b'\n'):
                    break
                row = json.loads(line)
                dest.write(json.dumps({k: row.get(k) for k in keys}) + '\n')
                count += 1
        manifest['files'].append(dict(file=path.name, captured_bytes=limit, records=count,
                                      captured_sha256=digest.hexdigest()))
        print(path.name, count, flush=True)
for name in ['labels.jsonl', 'membership.json', 'manifest.json']:
    (out / name).write_bytes((root / 'data' / name).read_bytes())
manifest['finished_utc'] = datetime.now(timezone.utc).isoformat()
(out / 'snapshot.json').write_text(json.dumps(manifest, indent=2) + '\n')
