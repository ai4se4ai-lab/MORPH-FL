"""Experiment conditions are explicit, immutable policy configurations."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SearchConfig:
    variant: str = "morph"
    rounds: int = 12
    tokens: int = 16000
    max_probes: int = 48
    wall_seconds: float = 3600
    portfolio_size: int = 3
    candidate_count: int = 20
    files_per_round: int = 4
    source_lines: int = 40
    forgetting: str = "adaptive"
    fixed_interval: int = 3
    reset_window: int = 3
    reset_min_rounds: int = 4
    reset_min_tokens: int = 256
    reset_min_fraction: float = 0.0
    reset_gain_rate: float = 0.0
    reset_repetition: float = 0.5
    reset_diversity: float = 0.5
    roles: tuple[str, ...] = ("behavioral", "skeptical", "structural", "dynamic")
    probes: bool = True
    model_memory: bool = True
    share_evidence: bool = True
    retain_all_models: bool = False
    independent: bool = False

    def __post_init__(self):
        if (
            min(
                self.rounds,
                self.tokens,
                self.max_probes,
                self.portfolio_size,
                self.candidate_count,
                self.files_per_round,
                self.source_lines,
            )
            < 1
            or self.wall_seconds <= 0
        ):
            raise ValueError("Search sizes and budgets must be positive")
        from .policies import PlateauMonitor

        PlateauMonitor(
            self.reset_window,
            self.reset_min_rounds,
            self.reset_min_tokens,
            total_budget=self.tokens,
            min_fraction=self.reset_min_fraction,
            gain_rate=self.reset_gain_rate,
            repetition=self.reset_repetition,
            diversity_threshold=self.reset_diversity,
        )
        if (
            self.forgetting not in {"adaptive", "fixed", "none", "stateless"}
            or self.fixed_interval < 1
            or not self.roles
        ):
            raise ValueError("Invalid search policy")


VARIANTS = (
    "morph",
    "no_forgetting",
    "fixed_reset",
    "context_only",
    "single_hypothesis",
    "no_mde",
    "no_probes",
    "no_skeptic",
    "independent_agents",
    "one_agent",
    "stateless_summary",
    "rerank",
    "bm25",
    "graph",
)


def configuration(variant: str, **overrides) -> SearchConfig:
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant: {variant}")
    changes = {
        "no_forgetting": dict(forgetting="none"),
        "fixed_reset": dict(forgetting="fixed"),
        "context_only": dict(retain_all_models=True),
        "single_hypothesis": dict(portfolio_size=1),
        "no_mde": dict(model_memory=False),
        "no_probes": dict(probes=False),
        "no_skeptic": dict(roles=("behavioral", "structural", "dynamic")),
        "independent_agents": dict(independent=True, share_evidence=False),
        "one_agent": dict(roles=("structural",)),
        "stateless_summary": dict(forgetting="stateless", model_memory=False),
        "rerank": dict(rounds=1, forgetting="none"),
    }.get(variant, {})
    return replace(SearchConfig(), **(changes | dict(variant=variant) | overrides))


RESET_FIELDS = frozenset(
    {
        "reset_window",
        "reset_min_rounds",
        "reset_min_tokens",
        "reset_min_fraction",
        "reset_gain_rate",
        "reset_repetition",
        "reset_diversity",
    }
)
