"""Algorithm 4: budgeted investigation with evidence-preserving forgetting."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import tempfile
import time
from dataclasses import asdict
from pathlib import Path

from morph_fl.agents import InvestigatorSessions
from morph_fl.domain import Budget, FaultHypothesis, identity
from morph_fl.inference.local import BudgetExceeded
from morph_fl.infrastructure.artifacts import ArtifactStore, AuditLog
from morph_fl.investigation import EvidenceLedger, ProbeExecutor, SandboxConfig
from morph_fl.program_analysis import analyze_python
from morph_fl.program_analysis.retrieval import bm25, tokens
from morph_fl.transformations import (
    complaint_to_contract,
    compose_slice,
    evidence_update,
    fresh_context,
    synthesize,
)

from .config import SearchConfig
from .policies import PlateauMonitor, SearchSample, diversity, rank_probes, select_portfolio


def source_window(text: str, report: str, width: int, path: str = "") -> str:
    """Prefer issue-time trace locations; otherwise use weighted identifier overlap."""
    lines = text.splitlines()
    stop = {
        "the",
        "and",
        "for",
        "this",
        "that",
        "with",
        "from",
        "return",
        "none",
        "true",
        "false",
        "when",
        "not",
        "but",
        "are",
        "was",
        "have",
        "has",
        "should",
        "would",
        "can",
        "def",
        "self",
    }
    query = set(tokens(report)) - stop
    scored = [
        (sum(1 + min(len(term), 20) / 10 for term in query.intersection(tokens(line))), -i)
        for i, line in enumerate(lines)
    ]
    center = -max(scored, default=(0, 0))[1]
    if path:
        basename = re.escape(Path(path).name)
        traces = re.findall(
            r"File [\"\'][^\"\']*" + basename + r"[\"\'], line (\d+), in ([\w.]+)", report
        )
        requested_line = None
        function = None
        if traces:
            requested_line, function = int(traces[-1][0]) - 1, traces[-1][1]
        elif Path(path).name in report:
            arrows = re.findall(r"-{2,}>\s*(\d+)", report)
            methods = re.findall(basename + r" in ([\w.]+)", report)
            if arrows:
                requested_line = int(arrows[-1]) - 1
            if methods:
                function = methods[-1]
        # Issue-time stack line numbers can drift relative to the benchmark snapshot.
        # Resolve the named function before trusting a raw line offset.
        try:
            tree = ast.parse(text)
            methods = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == function
            ]
        except SyntaxError:
            methods = []
        if methods:
            selected = min(methods, key=lambda node: abs(node.lineno - (requested_line or center)))
            body = selected.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                body = body[1:]
            first = body[0].lineno - 1 if body else selected.lineno - 1
            center = first + width // 2
        elif requested_line is not None and 0 <= requested_line < len(lines):
            center = requested_line
    start = max(0, center - width // 2)
    return "\n".join(
        f"{i + 1}: {line}" for i, line in enumerate(lines[start : start + width], start)
    )[:4500]


class LocalizationController:
    def __init__(self, config: SearchConfig, backend=None, sandbox: SandboxConfig | None = None):
        self.config = config
        self.backend = backend
        self.sandbox = sandbox

    def run(
        self,
        root: Path,
        report: str,
        revision: str,
        artifacts: Path | None = None,
        initial_clue: str | None = None,
    ) -> dict:
        cfg = self.config
        started = time.monotonic()
        directory = artifacts or Path(tempfile.mkdtemp(prefix="morph-evidence-"))
        store = ArtifactStore(directory / "artifacts")
        audit_log = AuditLog(directory / "audit.jsonl")
        ledger = EvidenceLedger(revision, audit_log)
        system = analyze_python(root, revision)
        ranking = bm25(report, system.sources)
        if not ranking:
            raise ValueError("No production Python source files found")
        rank_order = {p: i for i, p in enumerate(ranking)}
        seeds = ranking[: min(5, len(ranking))]
        sliced = compose_slice(system, seeds)
        expanded = set(sliced)
        candidates = list(dict.fromkeys(seeds + [p for p in ranking if p in expanded] + ranking))[
            : cfg.candidate_count
        ]
        if cfg.variant == "graph":
            ranking = sorted(ranking, key=lambda p: (p not in sliced, rank_order[p]))
        behavior = complaint_to_contract(report)
        isolated = cfg.independent or not cfg.share_evidence
        behavior_by_scope = {}
        budget = Budget(cfg.tokens, cfg.max_probes, cfg.wall_seconds)
        sessions = InvestigatorSessions()
        monitor = PlateauMonitor(
            cfg.reset_window,
            cfg.reset_min_rounds,
            cfg.reset_min_tokens,
            total_budget=cfg.tokens,
            min_fraction=cfg.reset_min_fraction,
            gain_rate=cfg.reset_gain_rate,
            repetition=cfg.reset_repetition,
            diversity_threshold=cfg.reset_diversity,
        )
        executor = ProbeExecutor(root, revision, store, self.sandbox)
        pools: dict[str, dict[str, FaultHypothesis]] = {}
        scope_evidence: dict[str, set[str]] = {}
        seen: set[str] = set()
        completed_probes = {}
        assessments, events = [], []
        invalid = duplicate = resets = switches = 0
        previous_leader = None
        stop_reason = "round_limit"

        def event(value):
            events.append(value)
            audit_log.append(value)

        event(
            dict(
                type="start",
                revision=revision,
                config=asdict(cfg),
                initial_clue=initial_clue,
                clue_status="controlled_unverified_misdirection" if initial_clue else None,
            )
        )
        if cfg.variant not in {"bm25", "graph"} and self.backend is None:
            raise ValueError("LLM variant needs a model backend")
        for step in range(0 if cfg.variant in {"bm25", "graph"} else cfg.rounds):
            if (
                budget.remaining < 64
                or budget.probes_used >= budget.probes
                or time.monotonic() - started >= budget.seconds
            ):
                stop_reason = "budget_exhausted"
                break
            role = cfg.roles[step % len(cfg.roles)]
            scope = role if isolated else "shared"
            pool = pools.setdefault(scope, {})
            references = scope_evidence.setdefault(scope, set())
            visible_evidence = {eid: ledger.observations[eid] for eid in references}
            retained = select_portfolio(list(pool.values()), cfg.portfolio_size)
            payload = fresh_context(
                behavior_by_scope.get(scope, behavior),
                retained,
                visible_evidence,
                budget.remaining,
                role,
            )
            if not cfg.model_memory:
                payload = dict(
                    role=role,
                    report=report,
                    summary="\n".join(
                        f"{e.location.path}:{e.location.line}: {json.dumps(e.observation)}"
                        for e in visible_evidence.values()
                    ),
                )
            offset = (step * cfg.files_per_round) % len(candidates)
            if step == 0:
                files = candidates[: cfg.files_per_round]
            else:
                # Revisit a live explanation while reserving slots for new alternatives.
                anchors = [ranking[0]] + [h.path for h in retained[:1]]
                rotating = candidates[offset:] + candidates[:offset]
                files = list(dict.fromkeys(anchors + rotating))[: cfg.files_per_round]
            payload["source"] = {
                p: source_window(system.sources[p], report, cfg.source_lines, p) for p in files
            }
            payload["retrieval_rank"] = {path: rank_order[path] + 1 for path in files}
            payload["source_revision"] = revision
            payload["investigation_rule"] = (
                "Recheck recorded contradictions; issue-time trace lines may drift. Quote actual numbered source, not a report excerpt."
            )
            if cfg.model_memory:
                payload["relations"] = [
                    dict(
                        source=r.source,
                        target=r.target,
                        kind=r.kind,
                        line=r.location.line,
                        resolution=r.resolution,
                        status=r.status,
                    )
                    for r in system.relations
                    if r.source.split("::")[0] in files
                    and r.kind in {"calls", "imports", "data_flows_to"}
                ][:12]
            payload["registered_procedures"] = list(self.sandbox.procedures) if self.sandbox else []
            if initial_clue and step == 0:
                payload["initial_clue"] = dict(
                    text=initial_clue, status="unverified_controlled_clue"
                )
            messages = sessions.messages(role, payload, cfg.forgetting == "stateless")
            request_artifact, request_digest = store.put(
                json.dumps(messages, sort_keys=True).encode()
            )
            event(
                dict(
                    type="agent_request",
                    step=step,
                    role=role,
                    artifact=request_artifact,
                    digest=request_digest,
                )
            )
            before_in, before_out = self.backend.input_tokens, self.backend.output_tokens
            try:
                response, raw = self.backend.ask(messages, budget.remaining)
            except BudgetExceeded:
                stop_reason = "context_or_token_budget"
                break
            except (ValueError, TypeError, KeyError) as exc:
                invalid += 1
                failure = dict(type="invalid_response", step=step, role=role, error=str(exc))
                failed_raw = getattr(exc, "raw", None)
                if isinstance(failed_raw, str):
                    artifact, digest = store.put(failed_raw.encode())
                    failure.update(artifact=artifact, digest=digest)
                event(failure)
                continue
            finally:
                budget.charge(
                    self.backend.input_tokens - before_in, self.backend.output_tokens - before_out
                )
            if not isinstance(response, dict) or not isinstance(
                response.get("hypotheses"), list
            ):
                invalid += 1
                artifact, digest = store.put(raw.encode())
                event(
                    dict(
                        type="invalid_response",
                        step=step,
                        error="Expected object with hypothesis list",
                        role=role,
                        artifact=artifact,
                        digest=digest,
                    )
                )
                continue
            response_artifact, response_digest = store.put(raw.encode())
            event(
                dict(
                    type="agent_response",
                    step=step,
                    role=role,
                    artifact=response_artifact,
                    digest=response_digest,
                    response=response,
                )
            )
            sessions.record(role, messages, raw)
            behavior_by_scope[scope] = complaint_to_contract(report, response)
            if not isolated:
                behavior = behavior_by_scope[scope]
            proposed = []
            for ordinal, item in enumerate(response.get("hypotheses", [])[:4]):
                try:
                    hypothesis, probe = synthesize(item, system)
                    if hypothesis.path not in files:
                        raise ValueError("Hypothesis is outside the visible source window")
                    active = pool.setdefault(hypothesis.id, hypothesis)
                    known_predictions = {prediction.id for prediction in active.predictions}
                    active.predictions.extend(
                        prediction
                        for prediction in hypothesis.predictions
                        if prediction.id not in known_predictions
                    )
                    known_locations = {
                        (location.path, location.line) for location in active.locations
                    }
                    active.locations.extend(
                        location
                        for location in hypothesis.locations
                        if (location.path, location.line) not in known_locations
                    )
                    event(
                        dict(
                            type="hypothesis",
                            step=step,
                            hypothesis=asdict(hypothesis),
                            probe=asdict(probe),
                        )
                    )
                    if not cfg.probes:
                        pool[hypothesis.id].score = max(
                            pool[hypothesis.id].score, 0.01 * (4 - ordinal)
                        )
                    probe.alternatives = [
                        other.id
                        for other in pool.values()
                        if other.id != hypothesis.id
                        and any(
                            prediction.expected != probe.prediction.expected
                            or prediction.predicate != probe.prediction.predicate
                            for prediction in other.predictions
                        )
                    ]
                    proposed.append(probe)
                except (ValueError, TypeError, KeyError, AttributeError) as exc:
                    invalid += 1
                    event(dict(type="invalid_hypothesis", step=step, error=str(exc)))
            duplicate_round = sum(
                identity((p.kind, p.path, p.parameters)) in completed_probes for p in proposed
            )
            duplicate += duplicate_round
            # Independent investigators may repeat a physical observation; only its fact is reused,
            # never another agent's speculative hypothesis or dialogue.
            gained = 0
            if cfg.probes:
                for probe in rank_probes(
                    proposed, list(pool.values()), set() if isolated else seen
                ):
                    if (
                        budget.probes_used >= budget.probes
                        or time.monotonic() - started >= budget.seconds
                    ):
                        break
                    seen.add(probe.id)
                    try:
                        execution_key = identity((probe.kind, probe.path, probe.parameters))
                        observation = completed_probes.get(execution_key)
                        if observation is None:
                            observation = executor.execute(
                                probe, max(0.01, budget.seconds - (time.monotonic() - started))
                            )
                            budget.probes_used += 1
                            expected_digest = hashlib.sha256(
                                system.sources[probe.path].encode()
                            ).hexdigest()
                            if observation.location.digest != expected_digest:
                                raise ValueError("Source changed since model construction")
                            ledger.add(observation)
                            observation = ledger.observations[observation.id]
                            completed_probes[execution_key] = observation
                        novel = observation.id not in references
                        gained += int(novel and not observation.observation.get("blocked"))
                        references.add(observation.id)
                        h = pool[probe.hypothesis_id]
                        if observation.id not in h.support + h.contradictions:
                            assessment = evidence_update(h, probe, observation)
                            assessments.append(asdict(assessment))
                            event(dict(type="assessment", **asdict(assessment)))
                        h.validate(ledger.observations)
                    except (ValueError, TypeError, KeyError, SyntaxError, OSError) as exc:
                        invalid += 1
                        event(dict(type="probe_error", step=step, probe=probe.id, error=str(exc)))
            live = list(pool.values())
            leader = max(live, key=lambda h: h.score).id if live else None
            switches += int(previous_leader is not None and leader != previous_leader)
            previous_leader = leader
            round_tokens = (
                self.backend.input_tokens - before_in + self.backend.output_tokens - before_out
            )
            monitor.update(
                SearchSample(
                    gained, duplicate_round / max(1, len(proposed)), diversity(live), round_tokens
                )
            )
            event(
                dict(
                    type="round",
                    step=step,
                    role=role,
                    gained=gained,
                    diversity=diversity(live),
                    tokens=budget.input_tokens + budget.output_tokens,
                    leader=leader,
                )
            )
            reset = cfg.forgetting == "fixed" and (step + 1) % cfg.fixed_interval == 0
            if cfg.forgetting == "adaptive":
                decision = monitor.evaluate(
                    budget.remaining, max(cfg.reset_min_tokens, round_tokens // 2)
                )
                event(dict(type="reset_decision", step=step, **decision))
                reset |= decision["should_reset"]
            if reset:
                before_refs = set(ledger.observations)
                for key, hypotheses in pools.items():
                    if not cfg.retain_all_models:
                        pools[key] = {
                            h.id: h
                            for h in select_portfolio(list(hypotheses.values()), cfg.portfolio_size)
                        }
                sessions.forget()
                monitor.reset()
                resets += 1
                assert before_refs == set(ledger.observations), (
                    "Forgetting deleted verified evidence"
                )
                event(
                    dict(
                        type="reset",
                        step=step,
                        remaining_tokens=budget.remaining,
                        retained={k: list(p) for k, p in pools.items()},
                        observations=sorted(before_refs),
                    )
                )
            # A conservative stop needs multiple independently registered dynamic procedures.
            leader_h = pool.get(leader)
            if leader_h:
                dynamic = [
                    ledger.observations[e]
                    for e in leader_h.support
                    if ledger.observations[e].kind in {"test", "trace", "counterfactual"}
                ]
                procedures = {e.observation.get("procedure_id") for e in dynamic}
                if len(procedures) >= 2 and not leader_h.contradictions and leader_h.assumptions:
                    stop_reason = "independent_dynamic_support"
                    break
        all_hypotheses = [h for pool in pools.values() for h in pool.values()]
        if all_hypotheses:
            scores = {
                path: max((h.score for h in all_hypotheses if h.path == path), default=-1)
                for path in ranking
            }
            ranking = sorted(ranking, key=lambda path: (-scores[path], rank_order[path]))
        verified_dynamic = [
            a
            for a in assessments
            if a["scope"] == "causal_prediction"
            and a["verdict"] == "supports"
            and ledger.observations[a["evidence_id"]].kind in {"test", "trace", "counterfactual"}
        ]
        abstained = not bool(verified_dynamic)
        event(dict(type="stop", reason=stop_reason, abstained=abstained, budget=asdict(budget)))
        return dict(
            ranking=ranking,
            hypotheses=[asdict(h) for h in all_hypotheses],
            observations=[asdict(e) for e in ledger.observations.values()],
            assessments=assessments,
            model=dict(
                behavior=asdict(behavior),
                revision=revision,
                symbols=[asdict(s) for s in system.symbols],
                relations=[asdict(r) for r in system.relations],
                diagnostics=system.diagnostics,
            ),
            audit=events,
            audit_path=str(audit_log.path),
            abstained=abstained,
            confidence=None,
            uncertainty="Causal localization remains unverified"
            if abstained
            else "Supported under recorded procedure assumptions",
            evidence_kind="dynamic_and_static" if verified_dynamic else "static_only",
            stop_reason=stop_reason,
            resets=resets,
            duplicate_probes=duplicate,
            invalid_probes=invalid,
            hypothesis_switches=switches,
            mechanism_diversity=diversity(all_hypotheses),
            input_tokens=budget.input_tokens,
            output_tokens=budget.output_tokens,
            probe_count=budget.probes_used,
            seconds=time.monotonic() - started,
            function_ranking=list(
                dict.fromkeys(
                    f"{location.path}::{location.symbol}"
                    for h in sorted(all_hypotheses, key=lambda h: -h.score)
                    for location in h.locations
                    if location.symbol
                )
            ),
        )
