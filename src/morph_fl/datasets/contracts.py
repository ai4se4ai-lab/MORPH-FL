"""Public benchmark case validation; evaluator labels are never agent inputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublicCase:
    instance_id: str
    repo: str
    revision: str
    root: str
    report: str
    initial_clue: str | None = None
    language: str = "python"

    def validate(self) -> None:
        if self.language != "python":
            raise ValueError(
                "Built-in localization supports Python; a language analyzer is required for this case"
            )
        if not self.instance_id or not self.revision or not self.report:
            raise ValueError("A case needs an ID, source revision, and report")
        if not Path(self.root).is_dir():
            raise ValueError("Case source snapshot is missing")

    @classmethod
    def from_row(cls, row: dict) -> PublicCase:
        forbidden = {
            "patch",
            "test_patch",
            "hints_text",
            "gold",
            "solution",
            "labels",
            "fix_commit",
        }
        if forbidden.intersection(row):
            raise ValueError("Evaluator-only information is present in a public case")
        case = cls(**{k: row[k] for k in cls.__dataclass_fields__ if k in row})
        case.validate()
        return case
