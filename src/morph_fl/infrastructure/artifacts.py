"""Content-addressed artifacts and hash-linked append-only audit events."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class ArtifactStore:
    def __init__(self, directory: Path):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(data).hexdigest()
        path = self.directory / digest
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError("Artifact hash mismatch")
        else:
            temporary = self.directory / f".{digest}.{os.getpid()}"
            temporary.write_bytes(data)
            os.replace(temporary, path)
        return str(path), digest

    @staticmethod
    def verify(path: str, digest: str) -> bool:
        return (
            Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
        )


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.previous = "0" * 64
        if path.exists():
            for line in path.read_text().splitlines():
                row = json.loads(line)
                digest = row.pop("digest")
                if row["previous"] != self.previous or self._digest(row) != digest:
                    raise ValueError("Audit chain is corrupt")
                self.previous = digest

    @staticmethod
    def _digest(row: dict) -> str:
        return hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()

    def append(self, event: dict) -> None:
        row = dict(previous=self.previous, event=event)
        row["digest"] = self._digest(row)
        with self.path.open("a") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.previous = row["digest"]
