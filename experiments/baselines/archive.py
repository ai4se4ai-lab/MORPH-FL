"""Archive exact measured code and public-source provenance without datasets/weights."""

import hashlib
import json
import tarfile
from pathlib import Path

out = Path("experiments/baselines/source-versions")
out.mkdir(parents=True, exist_ok=True)
protocol = json.loads(Path("experiments/baselines/protocol.json").read_text())
h = hashlib.sha256()
for p in sorted(Path("src").rglob("*.py")):
    h.update(str(p.relative_to("src")).encode())
    h.update(p.read_bytes())
if h.hexdigest() != protocol["source_sha256"]:
    raise ValueError("Measured source changed")
archive = out / ("baselines-" + h.hexdigest()[:12] + ".tar.gz")
with tarfile.open(archive, "w:gz") as tar:
    for p in sorted(Path("src").rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and "egg-info" not in str(p):
            tar.add(p)
(out / "manifest.json").write_text(
    json.dumps(
        dict(
            source_sha256=h.hexdigest(),
            archive=str(archive),
            archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            upstream=json.loads(Path("src/morph_fl/baselines/vendor/manifest.json").read_text()),
        ),
        indent=2,
    )
    + "\n"
)
