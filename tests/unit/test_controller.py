"""Behavioral checks of communication ablations and failed-call accounting."""

import json
import tempfile
import unittest
from pathlib import Path

from morph_fl.engine import localize


class RecordingBackend:
    def __init__(self, malformed=False):
        self.input_tokens = self.output_tokens = 0
        self.requests = []
        self.malformed = malformed

    def ask(self, messages, remaining):
        self.input_tokens += 50
        self.output_tokens += 25
        payload = json.loads(messages[-1]["content"])
        self.requests.append(payload)
        if self.malformed:
            raise ValueError("Generated JSON is malformed")
        answer = dict(
            expected="discounted total",
            observed="original total",
            hypotheses=[
                dict(
                    path="a.py",
                    mechanism="wrong persisted value",
                    prediction="original value is returned",
                    probe=dict(path="a.py", line=2, quote="return total"),
                )
            ],
        )
        return answer, json.dumps(answer)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "a.py").write_text("def amount(total):\n    return total\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_independent_agents_do_not_receive_other_findings(self):
        shared = RecordingBackend()
        independent = RecordingBackend()
        localize(self.root, "total", "v", shared, rounds=4)
        localize(self.root, "total", "v", independent, "independent_agents", rounds=4)
        self.assertTrue(shared.requests[1]["hypotheses"])
        self.assertTrue(all(not r["hypotheses"] for r in independent.requests))
        self.assertTrue(all(r["behavior"]["expected"] is None for r in independent.requests))
        self.assertIsNotNone(shared.requests[1]["behavior"]["expected"])

    def test_one_agent_and_no_skeptic_change_actual_invocations(self):
        one = RecordingBackend()
        no_skeptic = RecordingBackend()
        localize(self.root, "total", "v", one, "one_agent", rounds=4)
        localize(self.root, "total", "v", no_skeptic, "no_skeptic", rounds=4)
        self.assertEqual({r["role"] for r in one.requests}, {"structural"})
        self.assertNotIn("skeptical", {r["role"] for r in no_skeptic.requests})

    def test_no_probe_ablation_does_not_create_observations(self):
        backend = RecordingBackend()
        result = localize(self.root, "total", "v", backend, "no_probes", rounds=3)
        self.assertEqual(result["observations"], [])
        self.assertEqual(result["probe_count"], 0)
        self.assertTrue(result["hypotheses"])

    def test_malformed_calls_still_spend_budget(self):
        backend = RecordingBackend(malformed=True)
        result = localize(self.root, "total", "v", backend, rounds=3)
        self.assertEqual(result["input_tokens"], 150)
        self.assertEqual(result["output_tokens"], 75)
        self.assertEqual(result["invalid_probes"], 3)
        self.assertTrue(result["abstained"])

    def test_malformed_generation_is_preserved_as_auditable_artifact(self):
        import hashlib

        from morph_fl.inference.local import InvalidModelResponse

        class MalformedBackend(RecordingBackend):
            def ask(self, messages, remaining):
                self.input_tokens += 50
                self.output_tokens += 25
                raise InvalidModelResponse("Invalid JSON", "Here is prose instead of JSON.")

        result = localize(self.root, "total", "v", MalformedBackend(), rounds=1,
                          artifacts=self.root / "evidence")
        failure = next(e for e in result["audit"] if e["type"] == "invalid_response")
        raw = Path(failure["artifact"]).read_bytes()
        self.assertEqual(raw, b"Here is prose instead of JSON.")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), failure["digest"])
        self.assertEqual(result["input_tokens"], 50)
        self.assertEqual(result["output_tokens"], 25)

    def test_echoed_payload_without_hypotheses_is_invalid(self):
        class EchoBackend(RecordingBackend):
            def ask(self, messages, remaining):
                self.input_tokens += 50
                self.output_tokens += 25
                response = dict(report="echoed report", expected=None)
                return response, json.dumps(response)

        result = localize(self.root, "total", "v", EchoBackend(), rounds=1,
                          artifacts=self.root / "evidence")
        failure = next(e for e in result["audit"] if e["type"] == "invalid_response")
        self.assertEqual(json.loads(Path(failure["artifact"]).read_text()),
                         dict(report="echoed report", expected=None))
        self.assertFalse(any(e["type"] == "agent_response" for e in result["audit"]))
        self.assertEqual(result["invalid_probes"], 1)

    def test_no_mde_uses_plain_evidence_memory(self):
        backend = RecordingBackend()
        localize(self.root, "total", "v", backend, "no_mde", rounds=2)
        self.assertNotIn("hypotheses", backend.requests[1])
        self.assertNotIn("relations", backend.requests[1])
        self.assertIn("return total", backend.requests[1]["summary"])


class ObservationReuseTests(unittest.TestCase):
    def test_different_mechanisms_reuse_one_physical_probe(self):
        class Alternatives(RecordingBackend):
            def ask(self, messages, remaining):
                answer, raw = super().ask(messages, remaining)
                answer["hypotheses"][0]["mechanism"] = f"alternative mechanism {len(self.requests)}"
                return answer, json.dumps(answer)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.py").write_text("def amount(total):\n    return total\n")
            result = localize(root, "total", "v", Alternatives(), rounds=3)
        self.assertEqual(result["probe_count"], 1)
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["duplicate_probes"], 2)
        self.assertEqual(len(result["assessments"]), 3)
