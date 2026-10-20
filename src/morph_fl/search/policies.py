from __future__ import annotations

import math
import re
from collections import deque
from dataclasses import dataclass

from morph_fl.domain import FaultHypothesis, Probe


def mechanism_terms(hypothesis: FaultHypothesis) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", hypothesis.mechanism.lower()))


def distance(left: FaultHypothesis, right: FaultHypothesis) -> float:
    a, b = mechanism_terms(left), mechanism_terms(right)
    semantic = 1 - len(a & b) / max(1, len(a | b))
    return 0.6 * semantic + 0.4 * (left.path != right.path)


def select_portfolio(hypotheses: list[FaultHypothesis], size: int) -> list[FaultHypothesis]:
    if size < 1:
        raise ValueError("Portfolio size must be positive")
    remaining = sorted(hypotheses, key=lambda h: (-h.score, h.id))
    selected = []
    while remaining and len(selected) < size:

        def utility(h):
            diversity = min((distance(h, old) for old in selected), default=1)
            return h.score + diversity

        best = max(remaining, key=utility)
        selected.append(best)
        remaining.remove(best)
    return selected


def rank_probes(
    probes: list[Probe], hypotheses: list[FaultHypothesis], seen: set[str]
) -> list[Probe]:
    """Conservative information-utility heuristic, not calibrated expected entropy."""
    by_id = {h.id: h for h in hypotheses}

    def utility(probe):
        hypothesis = by_id[probe.hypothesis_id]
        diversity = sum(distance(hypothesis, h) for h in hypotheses if h.id != hypothesis.id)
        discrimination = max(1, len(set(probe.alternatives))) + diversity
        return probe.reliability * discrimination / max(0.001, probe.estimated_cost)

    return sorted((p for p in probes if p.id not in seen), key=lambda p: (-utility(p), p.id))


@dataclass(frozen=True)
class SearchSample:
    gained: int
    duplicate_ratio: float
    diversity: float
    tokens: int


class PlateauMonitor:
    """Explicit rolling-window policy; defaults reproduce the measured v1 rule.

    Normalized exploration is optional and must receive the original total budget.
    Thresholds are design parameters, not empirically calibrated probabilities.
    """

    def __init__(
        self,
        window=3,
        min_rounds=4,
        minimum_tokens=256,
        *,
        total_budget=None,
        min_fraction=0.0,
        gain_rate=0.0,
        repetition=0.5,
        diversity_threshold=0.5,
    ):
        if min(window, min_rounds, minimum_tokens) < 1:
            raise ValueError("Plateau window, rounds and reserve must be positive")
        if any(
            not math.isfinite(v) or not 0 <= v <= 1
            for v in (min_fraction, repetition, diversity_threshold)
        ):
            raise ValueError("Normalized plateau thresholds must be in [0, 1]")
        if not math.isfinite(gain_rate) or gain_rate < 0:
            raise ValueError("Evidence gain threshold must be finite and nonnegative")
        if total_budget is not None and total_budget <= 0:
            raise ValueError("Total budget must be positive")
        if min_fraction and total_budget is None:
            raise ValueError("Normalized exploration requires the original total budget")
        self.history: deque[SearchSample] = deque(maxlen=window)
        self.rounds = 0
        self.minimum_tokens, self.min_rounds = minimum_tokens, min_rounds
        self.total_budget, self.min_fraction = total_budget, min_fraction
        self.gain_rate, self.repetition = gain_rate, repetition
        self.diversity_threshold = diversity_threshold

    def update(self, sample: SearchSample) -> None:
        if (
            sample.gained < 0
            or sample.tokens < 0
            or any(
                not math.isfinite(v) or not 0 <= v <= 1
                for v in (sample.duplicate_ratio, sample.diversity)
            )
        ):
            raise ValueError("Invalid plateau observation")
        self.history.append(sample)
        self.rounds += 1

    def evaluate(self, remaining: int, estimated_restart_cost: int) -> dict:
        if remaining < 0 or estimated_restart_cost < 0:
            raise ValueError("Remaining budget and restart cost must be nonnegative")
        if self.total_budget is not None and remaining > self.total_budget:
            raise ValueError("Remaining budget exceeds the original budget")
        n = len(self.history)
        gain = sum(s.gained for s in self.history)
        repeated = sum(s.duplicate_ratio for s in self.history) / max(1, n)
        spread = sum(s.diversity for s in self.history) / max(1, n)
        cost = sum(s.tokens for s in self.history)
        fraction = (1 - remaining / self.total_budget) if self.total_budget else None
        warm = (
            self.rounds >= self.min_rounds
            and n == self.history.maxlen
            and (fraction is None or fraction >= self.min_fraction)
        )
        affordable = remaining > estimated_restart_cost + self.minimum_tokens
        decision = (
            warm
            and affordable
            and cost >= self.minimum_tokens
            and gain / max(1, n) <= self.gain_rate
            and (repeated >= self.repetition or spread < self.diversity_threshold)
        )
        return dict(
            should_reset=decision,
            window=n,
            evidence_gain=gain,
            evidence_gain_rate=gain / max(1, n),
            repetition=repeated,
            diversity=spread,
            window_tokens=cost,
            tokens_per_new_observation=cost / max(1, gain),
            consumed_fraction=fraction,
            exploration_ready=warm,
            restart_affordable=affordable,
            estimated_restart_cost=estimated_restart_cost,
        )

    def should_reset(self, remaining: int, estimated_restart_cost: int) -> bool:
        return self.evaluate(remaining, estimated_restart_cost)["should_reset"]

    def reset(self) -> None:
        self.history.clear()


def diversity(hypotheses: list[FaultHypothesis]) -> float:
    pairs = [distance(a, b) for i, a in enumerate(hypotheses) for b in hypotheses[i + 1 :]]
    return sum(pairs) / len(pairs) if pairs else 0.0
