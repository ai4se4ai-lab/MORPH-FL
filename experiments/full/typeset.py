"""Prepare a pinned portable compiler/cache in the internet-enabled GPU stage.

Final collection compiles offline using that cache; smoke/partial results never
replace the manuscript. All compilation is on allocated compute nodes.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

URL = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-unknown-linux-musl.tar.gz"
SHA = "8533d07f9ccbd7a65824b9e0459041bca34af1eb33daba48f59215593753a3b7"


def typeset(results, template, prepare=False):
    results = Path(results)
    tools = results / "tools"
    tools.mkdir(exist_ok=True)
    compiler = tools / "tectonic"
    if prepare:
        archive = tools / "tectonic.tar.gz"
        if not archive.exists():
            urllib.request.urlretrieve(URL, archive)
        with archive.open("rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() != SHA:
                raise ValueError("Compiler asset digest mismatch")
        with tarfile.open(archive, "r:gz") as tf:
            member = next(m for m in tf if m.name == "tectonic" and m.isfile())
            with tf.extractfile(member) as source, compiler.open("wb") as dest:
                shutil.copyfileobj(source, dest)
        compiler.chmod(0o755)
        target = results / "setup/paper_preflight"
        shutil.copytree(
            template,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                "*.aux", "*.log", "*.out", "*.zip", "*.blg", "__pycache__"
            ),
        )
        subprocess.run(
            [str(compiler), "-X", "compile", str(target / "morph-fl.tex"), "--keep-logs"],
            check=True,
        )
        (tools / "typeset_preflight.json").write_text(
            json.dumps(
                dict(
                    compiler_url=URL,
                    asset_sha256=SHA,
                    pdf=str(target / "morph-fl.pdf"),
                    complete=True,
                )
            )
            + "\n"
        )
        return
    status = json.loads((results / "paper_export.json").read_text())
    if status.get("state") != "tex_exported_for_review":
        (results / "typeset_status.json").write_text(
            json.dumps(dict(state="deferred", reason="No complete non-smoke paper export")) + "\n"
        )
        return
    paper = results / "paper/morph-fl.tex"
    subprocess.run(
        [str(compiler), "-X", "compile", str(paper), "--only-cached", "--keep-logs"], check=True
    )
    with paper.with_suffix(".pdf").open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    (results / "typeset_status.json").write_text(
        json.dumps(dict(state="compiled_for_review", pdf_sha256=digest, compiler_asset_sha256=SHA))
        + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--prepare", action="store_true")
    a = p.parse_args()
    typeset(a.results, a.template, a.prepare)
