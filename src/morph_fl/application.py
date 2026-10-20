"""Application services: validated cases, durable records, separate evaluation."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path

from .datasets.contracts import PublicCase
from .engine import localize
from .evaluation.metrics import metrics, set_metrics
from .investigation import SandboxConfig


def read_rows(path: Path | str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def repair_interrupted_tail(path: Path) -> None:
    """Recover only a truncated final JSON record; reject corruption elsewhere."""
    if not path.exists():
        return
    offset = 0
    last = b""
    with path.open("rb") as source:
        for line in source:
            try:
                json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # A binary readline without a newline is necessarily the final
                # fragment. Completed-line corruption must never be repaired.
                if line.endswith(b"\n"):
                    raise ValueError("Corrupt completed result record") from None
                with path.open("r+b") as stream:
                    stream.truncate(offset)
                    stream.flush()
                    os.fsync(stream.fileno())
                return
            offset += len(line)
            last = line
    if last and not last.endswith(b"\n"):
        with path.open("ab") as stream:
            stream.write(b"\n")
            stream.flush()
            os.fsync(stream.fileno())


def run_cases(
    cases_path: Path,
    out: Path,
    backend,
    *,
    variant="morph",
    seed=1,
    budget=16000,
    rounds=12,
    limit=300,
    sandbox: SandboxConfig | None = None,
    require_inference=False,
    initial_clue: str | None = None,
    max_probes=48,
    wall_seconds=3600,
    reset_policy: dict | None = None,
):
    out.parent.mkdir(parents=True, exist_ok=True)
    repair_interrupted_tail(out)
    settings = dict(
        variant=variant,
        seed=seed,
        budget=budget,
        rounds=rounds,
        max_probes=max_probes,
        wall_seconds=wall_seconds,
        initial_clue=initial_clue,
        sandbox=asdict(sandbox) if sandbox else None,
        backend=getattr(backend, "metadata", None),
        reset_policy=reset_policy,
    )
    signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
    manifest = out.with_suffix(out.suffix + ".config.json")
    if manifest.exists() and json.loads(manifest.read_text())["signature"] != signature:
        raise ValueError("Cannot resume with changed experimental settings")
    manifest.write_text(json.dumps(dict(signature=signature, settings=settings), indent=2) + "\n")
    prior = read_rows(out) if out.exists() else []
    completed = {(r["instance_id"], r["revision"], r["report_digest"]) for r in prior}
    for row in read_rows(cases_path)[:limit]:
        case = PublicCase.from_row(row)
        report_digest = hashlib.sha256(case.report.encode()).hexdigest()
        if (case.instance_id, case.revision, report_digest) in completed:
            continue
        if any(r["instance_id"] == case.instance_id for r in prior):
            raise ValueError("Case revision or report changed during resume")
        if backend:
            backend.input_tokens = backend.output_tokens = 0
            if hasattr(backend, "set_seed"):
                # Per-case seed is stable across order changes and requeues.
                backend.set_seed(
                    int(hashlib.sha256(f"{seed}:{case.instance_id}".encode()).hexdigest()[:8], 16)
                )
        safe_id = hashlib.sha256(case.instance_id.encode()).hexdigest()[:20]
        result = localize(
            Path(case.root),
            case.report,
            case.revision,
            backend,
            variant,
            budget,
            rounds,
            artifacts=out.parent / (out.stem + ".evidence") / safe_id,
            sandbox=sandbox,
            initial_clue=initial_clue or case.initial_clue,
            max_probes=max_probes,
            wall_seconds=wall_seconds,
            reset_policy=reset_policy,
        )
        if require_inference and (not result["output_tokens"] or not result["hypotheses"]):
            raise RuntimeError("Preflight requires real inference and valid structured hypotheses")
        result.update(
            instance_id=case.instance_id,
            repo=case.repo,
            revision=case.revision,
            variant=variant,
            seed=seed,
            budget=budget,
            report_digest=report_digest,
            run_signature=signature,
        )
        with out.open("a") as stream:
            stream.write(json.dumps(result) + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def score_predictions(predictions: Path, labels_path: Path, out: Path) -> None:
    labels = {r["instance_id"]: r for r in read_rows(labels_path)}
    rows = []
    for prediction in read_rows(predictions):
        label = labels[prediction["instance_id"]]
        if prediction.get("revision") != label.get("revision"):
            raise ValueError("Prediction and label source revisions differ")
        row = dict(
            instance_id=prediction["instance_id"],
            repo=prediction["repo"],
            variant=prediction["variant"],
            seed=prediction["seed"],
            label_status=label["status"],
            **metrics(prediction["ranking"], label["files"]),
        )
        row.update(
            {
                key: prediction.get(key)
                for key in (
                    "input_tokens",
                    "output_tokens",
                    "seconds",
                    "resets",
                    "duplicate_probes",
                    "abstained",
                    "probe_count",
                    "hypothesis_switches",
                    "mechanism_diversity",
                )
            }
        )
        row.update(
            {
                f"set_{k}": v
                for k, v in set_metrics(prediction["ranking"][:5], label["files"]).items()
            }
        )
        function = metrics(prediction.get("function_ranking", []), label.get("functions", []))
        row.update({f"function_{k}": v for k, v in function.items()})
        rows.append(row)
    if not rows:
        raise ValueError("No predictions; refusing empty evaluation")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
