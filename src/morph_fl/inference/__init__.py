"""Inference adapters; optional GPU dependencies load only when needed."""

from .local import BudgetExceeded, LocalModel

__all__ = ["BudgetExceeded", "LocalModel"]
