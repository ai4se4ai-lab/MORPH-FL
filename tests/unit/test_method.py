"""Executable scientific invariants of metamodel transformations and search."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from morph_fl.agents import InvestigatorSessions
from morph_fl.application import repair_interrupted_tail
from morph_fl.datasets.contracts import PublicCase
from morph_fl.domain import Budget, Prediction
from morph_fl.evaluation.metrics import (
    calibration,
    cost_accuracy_auc,
    selective_accuracy,
    set_metrics,
)
from morph_fl.infrastructure.artifacts import ArtifactStore, AuditLog
from morph_fl.investigation import EvidenceLedger, ProbeExecutor
from morph_fl.program_analysis import analyze_python
from morph_fl.search.config import VARIANTS, configuration
from morph_fl.search.controller import source_window
from morph_fl.search.policies import PlateauMonitor, SearchSample, rank_probes, select_portfolio
from morph_fl.transformations import (
    complaint_to_contract,
    compose_slice,
    evidence_update,
    synthesize,
)


class MethodTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        (self.root / "order.py").write_text(
            "from pricing import discount\ndef persist(total):\n    payable = discount(total)\n    save(total)\n    return payable\n"
        )
        (self.root / "pricing.py").write_text("def discount(total):\n    return total * .9\n")
        self.system = analyze_python(self.root, "revision")
        self.store = ArtifactStore(Path(self.tmp.name) / "artifacts")
        self.executor = ProbeExecutor(self.root, "revision", self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def item(self, **extra):
        return dict(
            path="order.py",
            mechanism="wrong saved total",
            prediction="save uses undiscounted total",
            probe=dict(path="order.py", line=4, quote="save(total)"),
            **extra,
        )

    def test_t1_keeps_ambiguity_and_epistemic_status(self):
        model = complaint_to_contract("broken", {"expected": "90", "observed": "100"})
        self.assertEqual(model.status, "conjectured")
        self.assertTrue(complaint_to_contract("unclear").ambiguities)

    def test_t2_records_calls_data_flow_and_source_versions(self):
        kinds = {r.kind for r in self.system.relations}
        self.assertTrue({"calls", "imports", "reads", "writes", "data_flows_to"} <= kinds)
        resolved = [
            r
            for r in self.system.relations
            if r.kind == "calls" and r.target == "pricing.py::discount"
        ]
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].location.revision, "revision")
        self.assertTrue(any(r.resolution == "unresolved" for r in self.system.relations))

    def test_t3_expands_upstream_and_downstream(self):
        self.assertIn("pricing.py", compose_slice(self.system, ["order.py"]))
        self.assertIn("order.py", compose_slice(self.system, ["pricing.py"]))

    def test_t4_cannot_promote_generated_edges(self):
        h, p = synthesize(
            self.item(causal_chain=[dict(source="a", target="b", status="observed")]), self.system
        )
        self.assertEqual(h.causal_chain[0]["status"], "conjectured")
        self.assertEqual(h.locations[0].symbol, "persist")

    def test_invalid_source_and_prediction_rejected(self):
        item = self.item()
        item["path"] = "../secret.py"
        with self.assertRaises(ValueError):
            synthesize(item, self.system)
        item = self.item()
        item["prediction"] = ""
        with self.assertRaises(ValueError):
            synthesize(item, self.system)

    def test_t5_t6_static_support_and_contradiction_are_scoped(self):
        h, p = synthesize(self.item(), self.system)
        e = self.executor.execute(p)
        a = evidence_update(h, p, e)
        self.assertEqual(a.verdict, "supports")
        self.assertEqual(a.scope, "source_presence_only")
        wrong = replace(p, parameters=dict(path="order.py", line=4, quote="save(payable)"))
        contrary = self.executor.execute(wrong)
        a = evidence_update(h, wrong, contrary)
        self.assertEqual(a.verdict, "contradicts")
        self.assertIn(contrary.id, h.contradictions)

    def test_ast_probe_checks_predicted_structure(self):
        h, p = synthesize(self.item(), self.system)
        p = replace(
            p,
            kind="ast_query",
            parameters=dict(line=4, query=dict(node_type="Call", contains="save(total)")),
            prediction=Prediction("p", "call exists", "ast_matches", True),
        )
        e = self.executor.execute(p)
        a = evidence_update(h, p, e)
        self.assertEqual(a.verdict, "supports")
        self.assertEqual(a.scope, "static_structure_only")

    def test_dynamic_without_sandbox_is_inconclusive(self):
        h, p = synthesize(self.item(), self.system)
        p = replace(p, kind="test", prediction=Prediction("p", "failure", "test_fails", True))
        e = self.executor.execute(p)
        self.assertEqual(evidence_update(h, p, e).verdict, "inconclusive")

    def test_evidence_integrity_and_shared_fact_identity(self):
        h, p = synthesize(self.item(), self.system)
        e = self.executor.execute(p)
        ledger = EvidenceLedger("revision")
        self.assertTrue(ledger.add(e))
        self.assertFalse(ledger.add(replace(e, probe_id="other-agent")))
        self.assertEqual(len(ledger.observations), 1)
        Path(e.artifact).write_text("tampered")
        with self.assertRaises(ValueError):
            EvidenceLedger("revision").add(e)

    def test_revision_mismatch_rejected(self):
        h, p = synthesize(self.item(), self.system)
        e = self.executor.execute(p)
        with self.assertRaises(ValueError):
            EvidenceLedger("other").add(e)

    def test_audit_chain_detects_mutation(self):
        path = Path(self.tmp.name) / "audit.jsonl"
        log = AuditLog(path)
        log.append({"event": "first"})
        log.append({"event": "second"})
        AuditLog(path)
        path.write_text(path.read_text().replace("first", "other"))
        with self.assertRaises(ValueError):
            AuditLog(path)

    def test_t7_discards_dialogue_and_preserves_external_knowledge(self):
        sessions = InvestigatorSessions()
        messages = sessions.messages("structural", {"fact": "x"})
        sessions.record("structural", messages, "speculation")
        sessions.forget()
        fresh = sessions.messages("structural", {"fact": "x"})
        self.assertNotIn("speculation", json.dumps(fresh))
        self.assertIn("fact", json.dumps(fresh))

    def test_budget_never_resets_or_overdraws(self):
        b = Budget(tokens=10)
        b.charge(3, 4)
        self.assertEqual(b.remaining, 3)
        with self.assertRaises(ValueError):
            b.charge(4, 0)
        with self.assertRaises(ValueError):
            b.charge(-1, 0)

    def test_plateau_requires_minimum_budget_and_accounts_for_restart(self):
        monitor = PlateauMonitor(window=2, min_rounds=2, minimum_tokens=100)
        for _ in range(2):
            monitor.update(SearchSample(0, 1, 0, 100))
        self.assertFalse(monitor.should_reset(300, 250))
        self.assertTrue(monitor.should_reset(2000, 250))
        monitor.update(SearchSample(1, 0, 1, 100))
        self.assertFalse(monitor.should_reset(2000, 250))

    def test_portfolio_and_probe_selection(self):
        h, p = synthesize(self.item(), self.system)
        other = replace(
            h,
            id="alternative",
            mechanism="discount calculation error",
            locations=[replace(h.locations[0], path="pricing.py")],
        )
        portfolio = select_portfolio([h, other], 2)
        self.assertEqual({v.path for v in portfolio}, {"order.py", "pricing.py"})
        self.assertEqual(rank_probes([p], [h], {p.id}), [])

    def test_all_ablation_policies_are_real_configurations(self):
        for variant in VARIANTS:
            self.assertEqual(configuration(variant).variant, variant)
        self.assertTrue(configuration("context_only").retain_all_models)
        self.assertTrue(configuration("independent_agents").independent)
        self.assertEqual(len(configuration("one_agent").roles), 1)
        self.assertFalse(configuration("no_mde").model_memory)

    def test_long_file_can_retrieve_beyond_prefix(self):
        source = "\n".join(
            ["# unrelated"] * 100 + ["save discounted subtotal"] + ["# trailing"] * 20
        )
        self.assertIn(
            "101: save discounted subtotal", source_window(source, "discounted subtotal", 10)
        )

    def test_public_case_rejects_gold_leakage(self):
        row = dict(
            instance_id="x",
            repo="a/b",
            revision="v",
            root=str(self.root),
            report="bug",
            patch="solution",
        )
        with self.assertRaises(ValueError):
            PublicCase.from_row(row)

    def test_resume_recovers_only_truncated_tail(self):
        path = Path(self.tmp.name) / "records.jsonl"
        path.write_bytes(b'{"ok":1}\n{"partial":')
        repair_interrupted_tail(path)
        self.assertEqual(path.read_bytes(), b'{"ok":1}\n')
        path.write_bytes(b'bad\n{"ok":1}\n')
        with self.assertRaises(ValueError):
            repair_interrupted_tail(path)

    def test_reliability_metrics(self):
        self.assertEqual(calibration([0, 1], [0, 1]), dict(brier=0, ece=0))
        self.assertEqual(set_metrics(["a"], ["a", "b"])["recall"], 0.5)
        self.assertEqual(selective_accuracy([1, 0], [False, True])["accuracy"], 1)
        self.assertEqual(cost_accuracy_auc([(0, 0), (2, 1)]), 1)


class EpistemicPresentationTests(unittest.TestCase):
    def test_static_support_does_not_close_a_causal_question(self):
        from morph_fl.transformations import fresh_context

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.py").write_text("def total():\n    return 100\n")
            system = analyze_python(root, "v")
            hypothesis, probe = synthesize(
                dict(
                    path="a.py",
                    mechanism="wrong total",
                    prediction="persisted total is wrong",
                    probe=dict(path="a.py", line=2, quote="return 100"),
                ),
                system,
            )
            evidence = ProbeExecutor(root, "v", ArtifactStore(root / "artifacts")).execute(probe)
            evidence_update(hypothesis, probe, evidence)
            context = fresh_context(
                complaint_to_contract("wrong total"),
                [hypothesis],
                {evidence.id: evidence},
                1000,
                "skeptical",
            )
        candidate = context["hypotheses"][0]
        self.assertEqual(candidate["verified_prediction_observations"], [])
        self.assertEqual(candidate["source_observations"], [evidence.id])
        self.assertEqual(candidate["epistemic_status"], "unverified_cause")
        self.assertTrue(context["unresolved"])
