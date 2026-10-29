"""Verified observations outlive agent sessions and cannot be overwritten."""

from dataclasses import asdict

from morph_fl.domain import Evidence
from morph_fl.infrastructure.artifacts import ArtifactStore, AuditLog


class EvidenceLedger:
    def __init__(self, revision: str, audit: AuditLog | None = None):
        self.revision = revision
        self.observations: dict[str, Evidence] = {}
        self.audit = audit

    def add(self, evidence: Evidence) -> bool:
        if evidence.location.revision != self.revision:
            raise ValueError("Evidence source revision differs from the investigation")
        if not evidence.procedure or not evidence.location.digest:
            raise ValueError("Evidence lacks reproducibility/source provenance")
        if not ArtifactStore.verify(evidence.artifact, evidence.artifact_digest):
            raise ValueError("Evidence artifact failed independent integrity verification")
        old = self.observations.get(evidence.id)
        if old is not None:
            old_data, new_data = asdict(old), asdict(evidence)
            old_data.pop("probe_id")
            new_data.pop("probe_id")
            if old_data != new_data:
                raise ValueError("An observation is immutable")
            return False
        self.observations[evidence.id] = evidence
        if self.audit:
            self.audit.append({"type": "observation", "evidence": asdict(evidence)})
        return True
