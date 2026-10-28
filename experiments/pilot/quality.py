"""Summarize DeepSeek output diagnostics without changing experiment outputs."""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from .snapshot import completed_rows
except ImportError:
    from snapshot import completed_rows


def inspect(results, output):
    groups = defaultdict(lambda: dict(records=0, with_hypotheses=0, events=Counter(),
                                     errors=Counter(), stop_reasons=Counter()))
    for path in sorted((results / 'predictions').glob('main__m1__*.jsonl')):
        for row in completed_rows(path, path.stat().st_size):
            group = groups[row['variant']]
            group['records'] += 1
            group['with_hypotheses'] += bool(row.get('hypotheses'))
            group['stop_reasons'][str(row.get('stop_reason'))] += 1
            for event in row.get('audit', []):
                group['events'][str(event.get('type'))] += 1
                if event.get('type') in {'invalid_response', 'invalid_hypothesis'}:
                    group['errors'][str(event.get('error'))[:400]] += 1
    output.write_text(json.dumps(dict(checked_utc=datetime.now(timezone.utc).isoformat(),
                                     note='Live partial records; per-workflow counts may differ.',
                                     variants=dict(groups)), indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    inspect(args.results, args.out)
