"""Scheduled validation of the AST repair on the exact failing source archive."""
import argparse
import dataclasses
import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import tempfile
from pathlib import Path

from experiments.full.prepare import extract_python
from hpc.ufv.runtime_maintenance import verify_sources
from morph_fl.program_analysis.python import analyze_python


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads((args.deployment/'experiments/full/protocol.json').read_text())
    verify_sources(args.deployment, spec)
    module_spec = importlib.util.spec_from_loader('original_analyzer', SourceFileLoader('original_analyzer', str(args.original)))
    original = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(original)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root/'example.py').write_text('''from os import path
value = 1
class Example:
    def first(self, x):
        local = x + value
        def inner():
            return path.join(str(local), 'a')
        return local
    async def second(self):
        return value
final = value
''')
        before = dataclasses.asdict(original.analyze_python(root, 'unit'))
        after = dataclasses.asdict(analyze_python(root, 'unit'))
        assert before == after, 'Traversal semantics changed on ordinary source'
    with (args.results/'data/cases.jsonl').open() as stream:
        case = next(json.loads(line) for line in stream if json.loads(line)['instance_id'] == 'sympy__sympy-24909')
    with Path(case['archive']).open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == case['archive_sha256']
    with tempfile.TemporaryDirectory() as tmp:
        extract_python(case['archive'], tmp)
        try:
            original.analyze_python(Path(tmp), case['revision'])
        except RecursionError:
            reproduced = True
        else:
            raise AssertionError('Expected original crash was not reproduced')
        system = analyze_python(Path(tmp), case['revision'])
        receipt = dict(complete=True, original_crash_reproduced=reproduced,
                       ordinary_source_exact_equivalence=True, case=case['instance_id'],
                       sources=len(system.sources), symbols=len(system.symbols), relations=len(system.relations),
                       diagnostics=system.diagnostics, archive_sha256=case['archive_sha256'])
    args.receipt.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
