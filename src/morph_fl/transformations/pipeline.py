"""Typed transformations; executable observations never inherit LLM certainty."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Any

from morph_fl.domain import (
    Assessment,
    BehavioralModel,
    Evidence,
    FaultHypothesis,
    Prediction,
    Probe,
    SourceLocation,
    SystemModel,
    Verdict,
    identity,
)


def complaint_to_contract(report: str, extraction: dict | None = None) -> BehavioralModel:
    data = extraction or {}
    model = BehavioralModel(report)
    for key in ("trigger", "expected", "observed"):
        if isinstance(data.get(key), str):
            setattr(model, key, data[key])
    model.invariants = [s for s in data.get("invariants", []) if isinstance(s, str)]
    model.ambiguities = [s for s in data.get("ambiguities", []) if isinstance(s, str)]
    if not model.expected or not model.observed:
        model.ambiguities.append(
            "Expected/observed behavior has not been independently established"
        )
    return model


def compose_slice(system: SystemModel, seeds: list[str], hops: int = 2) -> list[str]:
    """Bidirectional dependency neighborhood; conservatively retains upstream causes."""
    selected = set(seeds)
    for _ in range(hops):
        expanded = set(selected)
        for relation in system.relations:
            if relation.resolution == "unresolved":
                continue
            source, target = relation.source.split("::")[0], relation.target.split("::")[0]
            if source in selected or target in selected:
                expanded.update((source, target))
        selected = expanded
    return list(dict.fromkeys(seeds + sorted(selected.intersection(system.sources) - set(seeds))))


def synthesize(item: dict[str, Any], system: SystemModel) -> tuple[FaultHypothesis, Probe]:
    path, mechanism = item["path"], item["mechanism"]
    if path not in system.sources or not isinstance(mechanism, str) or not mechanism.strip():
        raise ValueError("Invalid hypothesis source or mechanism")
    parameters = item["probe"]
    if not isinstance(parameters, dict) or parameters.get("path", path) != path:
        raise ValueError("Probe must map to the hypothesis source")
    line = int(parameters.get("line", 1))
    if not 1 <= line <= len(system.sources[path].splitlines()):
        raise ValueError("Source line is out of range")
    digest = sha256(system.sources[path].encode()).hexdigest()
    containing = [s for s in system.symbols if s.path == path and s.line <= line <= s.end_line]
    symbol = min(containing, key=lambda s: s.end_line - s.line).symbol if containing else ""
    location = SourceLocation(path, line, line, system.revision, digest, symbol)
    hid = identity((path, mechanism.casefold(), parameters.get("kind", "source_quote")))
    prediction_data = item.get("prediction", "")
    if isinstance(prediction_data, dict):
        prediction = Prediction(
            identity((hid, prediction_data)),
            str(prediction_data.get("description", "")),
            prediction_data.get("predicate", "source_contains"),
            prediction_data.get("expected", True),
            list(prediction_data.get("assumptions", [])),
        )
    else:
        prediction = Prediction(identity((hid, prediction_data)), str(prediction_data))
    if not prediction.description:
        raise ValueError("A hypothesis must predict an observation")
    chain = item.get("causal_chain", [])
    # Synthesis is conjectural even when a model labels itself "confirmed".
    chain = [dict(edge, status="conjectured") for edge in chain if isinstance(edge, dict)]
    hypothesis = FaultHypothesis(
        hid, [location], mechanism, [prediction], chain, assumptions=list(prediction.assumptions)
    )
    probe = hypothesis_to_probe(hypothesis, parameters)
    hypothesis.validate({})
    return hypothesis, probe


def hypothesis_to_probe(hypothesis: FaultHypothesis, parameters: dict) -> Probe:
    kind = parameters.get("kind", "source_quote")
    if kind not in {"source_quote", "ast_query", "test", "trace", "counterfactual"}:
        raise ValueError("Unsupported investigation kind")
    params = dict(parameters)
    return Probe(
        identity((hypothesis.id, kind, params)),
        hypothesis.id,
        kind,
        hypothesis.path,
        hypothesis.predictions[0],
        params,
        estimated_cost=30 if kind in {"test", "trace", "counterfactual"} else 1,
        reliability=0.9 if kind == "source_quote" else 0.7,
    )


def evidence_update(hypothesis: FaultHypothesis, probe: Probe, evidence: Evidence) -> Assessment:
    predicate = probe.prediction.predicate
    value = evidence.observation
    scope = "causal_prediction"
    if predicate == "source_contains":
        actual = value.get("matched")
        scope = "source_presence_only"
    elif predicate in {"exit_code", "test_fails"} and evidence.kind in {
        "test",
        "trace",
        "counterfactual",
    }:
        actual = (
            value.get("returncode") if predicate == "exit_code" else value.get("returncode") != 0
        )
    elif predicate == "output_contains" and evidence.kind in {"test", "trace", "counterfactual"}:
        needle = probe.parameters.get("needle")
        actual = needle in value.get("stdout", "") if isinstance(needle, str) and needle else None
    elif predicate == "counterfactual_changes_outcome" and evidence.kind == "counterfactual":
        baseline = value.get("baseline", {})
        actual = (baseline.get("returncode") != value.get("returncode")) if baseline else None
    elif predicate == "ast_matches" and evidence.kind == "ast_query":
        scope = "static_structure_only"
        actual = value.get("matched")
    else:
        actual = None
    if actual is None or value.get("timed_out") or value.get("blocked"):
        verdict = Verdict.INCONCLUSIVE
    else:
        verdict = Verdict.SUPPORTS if actual == probe.prediction.expected else Verdict.CONTRADICTS
    refs = hypothesis.support if verdict == Verdict.SUPPORTS else hypothesis.contradictions
    if verdict != Verdict.INCONCLUSIVE and evidence.id not in refs:
        refs.append(evidence.id)
    weight = 0.25 if scope == "source_presence_only" else (1 if evidence.kind == "ast_query" else 2)
    hypothesis.score += (
        0
        if verdict == Verdict.INCONCLUSIVE
        else weight * (1 if verdict == Verdict.SUPPORTS else -1)
    )
    return Assessment(
        hypothesis.id,
        evidence.id,
        verdict.value,
        scope,
        "Observed predicate under recorded assumptions; source presence alone does not establish cause",
    )


def fresh_context(
    behavior: BehavioralModel,
    hypotheses: list[FaultHypothesis],
    evidence: dict[str, Evidence],
    remaining: int,
    role: str,
) -> dict:
    views = []
    unresolved = []
    dynamic_kinds = {"test", "trace", "counterfactual"}
    for hypothesis in hypotheses:
        hypothesis.validate(evidence)
        runtime = [ref for ref in hypothesis.support if evidence[ref].kind in dynamic_kinds]
        static = [ref for ref in hypothesis.support if evidence[ref].kind not in dynamic_kinds]
        if not runtime:
            unresolved.extend(prediction.description for prediction in hypothesis.predictions)
        views.append(
            dict(
                id=hypothesis.id,
                candidate_locations=[
                    dict(
                        path=location.path,
                        line=location.line,
                        symbol=location.symbol,
                        revision=location.revision,
                    )
                    for location in hypothesis.locations
                ],
                unverified_mechanism=hypothesis.mechanism,
                predictions=[asdict(prediction) for prediction in hypothesis.predictions],
                source_observations=static,
                verified_prediction_observations=runtime,
                contradiction_observations=hypothesis.contradictions,
                epistemic_status="unverified_cause"
                if not runtime
                else "prediction_observed_under_assumptions",
                causal_chain=hypothesis.causal_chain,
            )
        )
    return dict(
        role=role,
        behavior=asdict(behavior),
        hypotheses=views,
        observations=[asdict(observation) for observation in evidence.values()],
        remaining_tokens=remaining,
        unresolved=unresolved,
        epistemic_status="Static source observations do not confirm a fault mechanism; unresolved causal predictions remain open",
    )
