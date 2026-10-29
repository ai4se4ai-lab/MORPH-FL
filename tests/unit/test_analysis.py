import unittest

from morph_fl.analysis import paired_bootstrap


class AnalysisTests(unittest.TestCase):
    def test_pairs_and_seed_average(self):
        rows = [
            dict(repo="r", instance_id="x", variant=v, top1=s)
            for v, s in [("morph", 1), ("morph", 0), ("bm25", 0)]
        ]
        r = paired_bootstrap(rows, right="bm25", samples=100)
        self.assertEqual(r["delta"], 0.5)
        self.assertEqual(r["paired_cases"], 1)
        self.assertEqual(r["ci95"], [0.5, 0.5])

    def test_no_unpaired_comparison(self):
        with self.assertRaises(ValueError):
            paired_bootstrap([dict(repo="r", instance_id="x", variant="morph", top1=1)])
