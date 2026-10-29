"""Publish small exact source snapshots for every attempted development version."""

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

out = Path("experiments/local/source-versions")
out.mkdir(parents=True, exist_ok=True)
protocol = json.loads(Path("experiments/local/protocol.json").read_text())
versions = {
    "before": Path("artifacts/local/revisions/before/src"),
    "compact": Path("artifacts/local/revisions/compact/src"),
    "intermediate": Path("artifacts/local/revisions/final-317396be209d/src"),
    "validated": Path(protocol["held_out_source"]),
}
manifest = {}
for name, source in versions.items():
    buffer = io.BytesIO()
    hasher = hashlib.sha256()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for path in sorted(source.rglob("*")):
            if (
                not path.is_file()
                or (path.suffix != ".py" and path.name != "py.typed")
                or "__pycache__" in path.parts
            ):
                continue
            raw = path.read_bytes()
            relative = path.relative_to(source)
            if path.suffix == ".py":
                hasher.update(str(relative).encode())
                hasher.update(raw)
            info = tarfile.TarInfo("src/" + relative.as_posix())
            info.size = len(raw)
            info.mode = 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(raw))
    target = out / (name + ".tar.gz")
    target.write_bytes(gzip.compress(buffer.getvalue(), mtime=0))
    manifest[name] = dict(
        source_path=str(source),
        source_sha256=hasher.hexdigest(),
        archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        bytes=target.stat().st_size,
    )
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
