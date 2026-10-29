"""Losslessly pack a stopped cell before resume; never run against a live writer."""

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path

from hpc.scripts.compact_models import compact, restore_model


def fingerprint(path, repair=False):
    """Stream logical records, optionally preserving/removing an interrupted tail."""
    digest = hashlib.sha256()
    count = 0
    repair_info = None
    size = path.stat().st_size
    with path.open("rb") as stream:
        while True:
            offset = stream.tell()
            line = stream.readline()
            if not line:
                break
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                if not repair or line.endswith(b"\n") or stream.tell() != size:
                    raise ValueError("Corrupt completed checkpoint record") from None
                backup = path.with_name(path.name + ".tail-" + uuid.uuid4().hex + ".bin")
                backup.write_bytes(line)
                with path.open("r+b") as target:
                    target.truncate(offset)
                    target.flush()
                    os.fsync(target.fileno())
                repair_info = dict(discarded_bytes=len(line), preserved_tail=str(backup))
                break
            if "model" in row:
                row["model"] = restore_model(row, path)
            digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode())
            digest.update(b"\n")
            count += 1
            if not line.endswith(b"\n"):
                if not repair:
                    raise ValueError("Checkpoint lacks a completed final newline")
                with path.open("ab") as target:
                    target.write(b"\n")
                    target.flush()
                    os.fsync(target.fileno())
                repair_info = dict(added_final_newline=True)
                break
    return dict(records=count, logical_sha256=digest.hexdigest()), repair_info


def pack_checkpoint(predictions, store):
    before_bytes = predictions.stat().st_size
    before, repair = fingerprint(predictions, repair=True)
    print(json.dumps(dict(phase="before", **before, before_bytes=before_bytes)), flush=True)
    packing = compact(predictions, store)
    after, _ = fingerprint(predictions)
    if before != after:
        raise ValueError("Packing changed logical checkpoint records; keep the job held")
    return dict(verified=True, before=before, after=after, repair=repair, packing=packing)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = pack_checkpoint(args.input, args.store)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.receipt.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(args.receipt)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
