import hashlib
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Observation:
    id: str
    path: str
    line: int
    quote: str
    revision: str
    digest: str
    kind: str = "static_source"


@dataclass
class Hypothesis:
    id: str
    path: str
    mechanism: str
    prediction: str
    probe: dict
    support: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    score: float = 0.0


def verify_quote(root, revision, probe):
    """An independent exact-source check verifies presence, never causal truth."""
    path = (root / probe["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Probe escapes repository or targets missing file")
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    line = int(probe["line"])
    quote = probe["quote"]
    if line < 1 or line > len(lines) or not quote.strip() or quote not in lines[line - 1]:
        return None
    digest = hashlib.sha256(text.encode()).hexdigest()
    oid = hashlib.sha256(f"{revision}:{probe['path']}:{line}:{quote}".encode()).hexdigest()[:20]
    return Observation(oid, probe["path"], line, quote, revision, digest)


def snapshot(hypotheses, evidence, budget, size=3):
    selected, seen = [], set()
    for h in sorted(hypotheses, key=lambda h: h.score, reverse=True):
        key = (h.path, h.mechanism)
        if key not in seen:
            selected.append(asdict(h))
            seen.add(key)
        if len(selected) >= size:
            break
    return dict(
        hypotheses=selected,
        observations=[asdict(e) for e in evidence.values()],
        remaining_tokens=budget,
        epistemic_status="static observations; causal claims unverified",
    )
