"""Backend contract shared by local inference and deterministic test fixtures."""

from typing import Any, Protocol


class ModelBackend(Protocol):
    input_tokens: int
    output_tokens: int

    def ask(
        self, messages: list[dict[str, str]], remaining: int, max_new: int = 1536
    ) -> tuple[dict[str, Any], str]: ...
