#!/usr/bin/env python3
"""Losslessly deduplicate static model payloads after a completed inference cell.

Inference prompts and results are unchanged. Behavior remains in each prediction;
the revision/symbol/relation graph is stored once per content hash on scratch.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import uuid
from pathlib import Path


def restore_model(record: dict, predictions: Path) -> dict:
    model = record["model"]
    if "structure_artifact" not in model:
        return model
    path = (predictions.parent / model["structure_artifact"]).resolve()
    with gzip.open(path, "rb") as stream:
        data = stream.read()
    if hashlib.sha256(data).hexdigest() != model["structure_sha256"]:
        raise ValueError("Stored model failed integrity verification")
    structure = json.loads(data)
    if "behavior" in model:
        structure["behavior"] = model["behavior"]
    return structure


def compact(predictions: Path, store: Path) -> dict:
    store.mkdir(parents=True, exist_ok=True)
    temporary = predictions.with_name(predictions.name + "." + uuid.uuid4().hex + ".tmp")
    records = written = 0
    before = predictions.stat().st_size
    try:
        with predictions.open() as source, temporary.open("w") as target:
            for line in source:
                if not line.strip():
                    continue
                row = json.loads(line)
                model = row.get("model", {})
                if "structure_artifact" in model:
                    restore_model(row, predictions)
                elif "relations" in model and "symbols" in model:
                    structure = {key: value for key, value in model.items() if key != "behavior"}
                    raw = json.dumps(structure, sort_keys=True, separators=(",", ":")).encode()
                    digest = hashlib.sha256(raw).hexdigest()
                    artifact = store / (digest + ".json.gz")
                    if not artifact.exists():
                        staging = store / ("." + digest + "." + uuid.uuid4().hex + ".tmp")
                        with staging.open("wb") as stream:
                            with gzip.GzipFile(
                                filename="", fileobj=stream, mode="wb", mtime=0
                            ) as compressed:
                                compressed.write(raw)
                        os.replace(staging, artifact)
                        written += 1
                    with gzip.open(artifact, "rb") as stream:
                        if hashlib.sha256(stream.read()).hexdigest() != digest:
                            raise ValueError("Content-addressed graph is corrupt")
                    row["model"] = dict(
                        structure_artifact=os.path.relpath(artifact, predictions.parent),
                        structure_sha256=digest,
                        revision=model.get("revision"),
                        symbol_count=len(model["symbols"]),
                        relation_count=len(model["relations"]),
                    )
                    if "behavior" in model:
                        row["model"]["behavior"] = model["behavior"]
                target.write(json.dumps(row) + "\n")
                records += 1
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, predictions)
    finally:
        temporary.unlink(missing_ok=True)
    return dict(
        records=records,
        new_graphs=written,
        before_bytes=before,
        predictions_after_bytes=predictions.stat().st_size,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compact(args.input, args.store)))


if __name__ == "__main__":
    main()
