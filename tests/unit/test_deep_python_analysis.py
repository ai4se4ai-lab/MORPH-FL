"""Regression tests for deeply nested expressions in full benchmark sources."""
import tempfile
import unittest
from pathlib import Path

from morph_fl.program_analysis.python import analyze_python


class DeepPythonAnalysisTests(unittest.TestCase):
    def test_deep_binary_expression_preserves_symbols_and_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'deep.py').write_text('def compute(x):\n    result = ' + ' + '.join(['x'] * 1500) + '\n    return result\n')
            system = analyze_python(root, 'revision')
            self.assertEqual([v.symbol for v in system.symbols], ['compute'])
            reads = [r for r in system.relations if r.kind == 'reads']
            self.assertEqual(len(reads), 1501)
            self.assertTrue(all(r.source == 'deep.py::compute' for r in reads))

    def test_nested_scope_restored_after_each_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'nested.py').write_text('''top = 1
class Outer:
    async def first(self):
        value = top
        def inner():
            return value
        return value
    def second(self):
        return top
end = top
''')
            system = analyze_python(root, 'revision')
            self.assertEqual([v.symbol for v in system.symbols], ['Outer', 'Outer.first', 'Outer.first.inner', 'Outer.second'])
            reads = [(r.source, r.target) for r in system.relations if r.kind == 'reads']
            self.assertIn(('nested.py::first', 'nested.py::first:value@4'), reads)
            self.assertIn(('nested.py', 'nested.py:top@1'), reads)
            self.assertIn(('nested.py::second', 'nested.py::second:top'), reads)
