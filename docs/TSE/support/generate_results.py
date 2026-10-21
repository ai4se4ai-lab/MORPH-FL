#!/usr/bin/env python3
"""Validate an author-reviewed binding manifest; never infer manuscript claims.

Input analysis directory is produced by experiments/full/analyze.py. A separate
JSON manifest maps registered keys to values and identifies source artifacts.
This is deliberately a stub: automatic metric/claim selection is not supported.
"""
import argparse
import json
from pathlib import Path

KEYS = {'effectiveness', 'mechanism', 'efficiency', 'file-top1-delta',
        'file-top1-ci', 'function-mrr-delta', 'recovery-delta', 'retention',
        'tokens', 'probes', 'wall-seconds', 'budget-curves',
        'primary-results', 'ablations'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('analysis', type=Path)
    parser.add_argument('bindings', type=Path)
    parser.add_argument('--output', type=Path, default=Path('generated/results.tex'))
    args = parser.parse_args()
    coverage = json.loads((args.analysis / 'completeness.json').read_text())
    if coverage.get('complete') is not True or coverage.get('smoke') is not False:
        raise SystemExit('Refusing incomplete/smoke/unverified coverage')
    status = json.loads((args.analysis / 'primary_comparisons.json').read_text())
    if status.get('complete') is not True:
        raise SystemExit('Refusing incomplete primary comparisons')
    manifest = json.loads(args.bindings.read_text())
    if manifest.get('human_reviewed') is not True:
        raise SystemExit('Bindings require scientific author review, including claim direction')
    values = manifest.get('values', {})
    missing = sorted(KEYS - values.keys())
    if missing:
        raise SystemExit('Missing registered keys: ' + ', '.join(missing))
    # Fail rather than guess an analysis schema or turn a p-value into a claim.
    raise SystemExit('STUB: implement and audit source-to-key extraction before final mode; no results written')

if __name__ == '__main__':
    main()
