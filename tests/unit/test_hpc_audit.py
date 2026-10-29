"""Scheduler terminal states must not be hidden by interrupted step markers."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class AuditTests(unittest.TestCase):
    def assemble(self, state, ledger):
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location(
            "morph_hpc_audit", root / "hpc/scripts/audit.py"
        )
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            (base / "config").mkdir()
            (base / "config/experiments.resolved.json").write_text(
                json.dumps(
                    dict(stages=[dict(name="setup", cells=[{}], steps=[dict(name="preflight")])])
                )
            )
            marker = base / "steps/setup/all/preflight.running"
            marker.parent.mkdir(parents=True)
            marker.write_text('{"start":1}')
            with (
                patch.object(audit.H, "log_root", return_value=base),
                patch.object(audit.H, "cluster", return_value={}),
                patch.object(audit.H, "results_dir", return_value=base),
                patch.object(
                    audit.H,
                    "read_tsv",
                    side_effect=lambda p: [["1", "setup", "1", ""]] if p.name == "jobs.tsv" else [],
                ),
                patch.object(audit.H, "latest_steps", return_value=ledger),
                patch.object(audit.H, "context", return_value={"CELL": "all"}),
                patch.object(audit, "slurm", return_value={"1": {"state": state}}),
            ):
                return audit.assemble("test")["rows"][0]

    def test_completed_job_with_unfinished_preflight_is_partial(self):
        row = self.assemble("COMPLETED", {})
        self.assertEqual(row["state"], "PARTIAL")
        self.assertIsNone(row["current"])

    def test_terminal_failure_is_not_running(self):
        self.assertEqual(self.assemble("TIMEOUT", {})["state"], "TIMEOUT")

    def test_completed_ledger_wins_over_stale_marker(self):
        row = self.assemble(
            "COMPLETED", {("setup", "all", "preflight"): {"rc": "0", "seconds": "3"}}
        )
        self.assertEqual(row["state"], "OK")
        self.assertEqual(row["steps_ok"], 1)

    def test_live_marker_remains_running(self):
        self.assertEqual(self.assemble("RUNNING", {})["state"], "RUNNING")
