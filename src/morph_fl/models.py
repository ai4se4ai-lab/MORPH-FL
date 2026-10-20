"""Legacy source-quote API. New metamodels live in morph_fl.domain."""

from .domain.legacy import Hypothesis, Observation, snapshot, verify_quote

__all__ = ["Hypothesis", "Observation", "snapshot", "verify_quote"]
