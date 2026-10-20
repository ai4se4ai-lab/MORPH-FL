"""Policy invariants and legacy equivalence for paper/implementation alignment."""

import math
import unittest

from morph_fl.search.config import configuration
from morph_fl.search.policies import PlateauMonitor, SearchSample


class ResetPolicyTests(unittest.TestCase):
    def stalled(self, **options):
        monitor = PlateauMonitor(window=3, min_rounds=3, **options)
        for _ in range(3):
            monitor.update(SearchSample(0, 0.8, 0.2, 200))
        return monitor

    def test_fraction_uses_original_budget_and_never_resets_it(self):
        monitor = self.stalled(total_budget=10000, min_fraction=0.15)
        self.assertFalse(monitor.should_reset(9000, 300))
        self.assertTrue(monitor.should_reset(8000, 300))
        monitor.reset()
        self.assertEqual(monitor.total_budget, 10000)
        self.assertEqual(len(monitor.history), 0)

    def test_fraction_gate_scales_across_budgets(self):
        for total in [10000, 100000]:
            monitor = self.stalled(total_budget=total, min_fraction=0.15)
            self.assertFalse(monitor.should_reset(int(total * 0.9), 300))
            self.assertTrue(monitor.should_reset(int(total * 0.8), 300))

    def test_progress_and_restart_cost_can_veto_a_reset(self):
        monitor = self.stalled(total_budget=10000, min_fraction=0.15)
        self.assertFalse(monitor.should_reset(8000, 7900))
        monitor.update(SearchSample(1, 0.8, 0.2, 200))
        self.assertFalse(monitor.should_reset(8000, 300))

    def test_default_decisions_match_measured_legacy_rule(self):
        for gain in [0, 1]:
            for repeated in [0.0, 0.5, 1.0]:
                for spread in [0.0, 0.5, 1.0]:
                    monitor = PlateauMonitor()
                    for _ in range(4):
                        monitor.update(SearchSample(gain, repeated, spread, 100))
                    for remaining in [300, 2000]:
                        expected = (
                            remaining > 512 and gain == 0 and (repeated >= 0.5 or spread < 0.5)
                        )
                        self.assertEqual(monitor.should_reset(remaining, 256), expected)

    def test_invalid_or_undefined_thresholds_rejected(self):
        for options in [
            dict(window=0),
            dict(min_fraction=0.15),
            dict(repetition=1.1),
            dict(gain_rate=math.nan),
        ]:
            with self.assertRaises(ValueError):
                PlateauMonitor(**options)
        with self.assertRaises(ValueError):
            configuration("morph", reset_diversity=-1)

    def test_diagnostic_is_a_measured_rate_not_entropy(self):
        result = self.stalled().evaluate(2000, 300)
        self.assertEqual(result["evidence_gain_rate"], 0)
        self.assertEqual(result["window_tokens"], 600)
        self.assertAlmostEqual(result["repetition"], 0.8)
        self.assertNotIn("entropy", result)
