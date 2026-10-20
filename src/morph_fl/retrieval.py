"""Compatibility imports; analysis lives in program_analysis/."""

from .program_analysis.retrieval import bm25, index, tokens

__all__ = ["bm25", "index", "tokens"]
