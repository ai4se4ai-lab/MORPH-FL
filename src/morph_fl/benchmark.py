"""Compatibility facade for dataset preparation and metrics."""

from .datasets.swebench import prepare
from .evaluation.metrics import metrics

__all__ = ["prepare", "metrics"]
