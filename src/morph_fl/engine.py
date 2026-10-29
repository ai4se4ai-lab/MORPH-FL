"""Stable application facade for the model-driven localization controller."""

from pathlib import Path

from .search.config import RESET_FIELDS, VARIANTS, configuration
from .search.controller import LocalizationController


def localize(
    root,
    report,
    revision,
    backend=None,
    variant="morph",
    budget=16000,
    rounds=12,
    portfolio=3,
    *,
    artifacts=None,
    sandbox=None,
    initial_clue=None,
    max_probes=48,
    wall_seconds=3600,
    reset_policy=None,
):
    options = dict(
        tokens=budget, portfolio_size=portfolio, max_probes=max_probes, wall_seconds=wall_seconds
    )
    if variant != "rerank":
        options["rounds"] = rounds
    if reset_policy:
        if set(reset_policy) - RESET_FIELDS:
            raise ValueError("Unknown reset policy parameter")
        options.update(reset_policy)
    config = configuration(variant, **options)
    return LocalizationController(config, backend, sandbox).run(
        Path(root), report, revision, Path(artifacts) if artifacts else None, initial_clue
    )


__all__ = ["VARIANTS", "localize"]
