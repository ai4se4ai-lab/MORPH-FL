"""GPU-stage preparation of full pinned datasets using packed Python snapshots.

Only public reports and pre-fix Python source enter inference. Gold patches are
used solely to create separate proxy labels; no post-fix tests are exposed.
Packed snapshots avoid exhausting Nibi's shared-filesystem inode quota.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

from morph_fl.datasets.labels import patch_labels

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def extract_python(archive, destination):
    destination = Path(destination).resolve()
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf:
            target = (destination / member.name).resolve()
            if (
                not target.is_relative_to(destination)
                or not member.isfile()
                or not member.name.endswith(".py")
            ):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def prepare(out, smoke=False):
    from datasets import load_dataset

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
    rows = {}
    memberships = {}
    for spec in pins["datasets"]:
        name = spec["id"].split("/")[-1]
        records = list(load_dataset(spec["id"], revision=spec["revision"], split="test"))
        expected = 300 if name.endswith("Lite") else 500
        if len(records) != expected:
            raise ValueError(f"Pinned dataset size differs: {name} {len(records)} != {expected}")
        # Same tiny source subset in both membership manifests makes smoke compositional.
        if smoke:
            records = sorted(records, key=lambda r: r["instance_id"])[:2]
        memberships[name] = [r["instance_id"] for r in records]
        for r in records:
            iid = r["instance_id"]
            if iid in rows and any(
                rows[iid][k] != r[k] for k in ["repo", "base_commit", "problem_statement", "patch"]
            ):
                raise ValueError("Overlapping benchmark instance has inconsistent content")
            rows[iid] = r
    archives = out / "archives"
    archives.mkdir(exist_ok=True)
    cache = Path(tempfile.mkdtemp(prefix="morph-git-"))
    public = []
    labels = []
    try:
        for number, (iid, row) in enumerate(sorted(rows.items()), 1):
            archive = archives / (iid + ".tar.gz")
            receipt = archives / (iid + ".json")
            if not archive.exists() or not receipt.exists():
                repo = cache / row["repo"].replace("/", "__")
                if not repo.exists():
                    subprocess.run(
                        ["git", "init", "--bare", str(repo)], check=True, stdout=subprocess.DEVNULL
                    )
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "fetch",
                        "--depth=1",
                        "https://github.com/" + row["repo"] + ".git",
                        row["base_commit"],
                    ],
                    check=True,
                )
                # Stream the pre-fix Git archive, retaining regular Python files only.
                process = subprocess.Popen(
                    ["git", "-C", str(repo), "archive", row["base_commit"]], stdout=subprocess.PIPE
                )
                temporary = archive.with_suffix(".partial")
                try:
                    with (
                        tarfile.open(fileobj=process.stdout, mode="r|") as source,
                        tarfile.open(temporary, "w:gz") as dest,
                    ):
                        for member in source:
                            if member.isfile() and member.name.endswith(".py"):
                                dest.addfile(member, source.extractfile(member))
                    if process.wait() != 0:
                        raise RuntimeError("git archive failed")
                    temporary.replace(archive)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                receipt.write_text(
                    json.dumps(dict(revision=row["base_commit"], sha256=digest(archive))) + "\n"
                )
            state = json.loads(receipt.read_text())
            if state["revision"] != row["base_commit"] or state["sha256"] != digest(archive):
                raise ValueError("Cached source archive differs")
            public.append(
                dict(
                    instance_id=iid,
                    repo=row["repo"],
                    revision=row["base_commit"],
                    archive=str(archive.resolve()),
                    archive_sha256=state["sha256"],
                    report=row["problem_statement"],
                )
            )
            label_cache = archives / (iid + ".label.json")
            if label_cache.exists():
                label = json.loads(label_cache.read_text())
            else:
                with tempfile.TemporaryDirectory(prefix="morph-label-") as tmp:
                    extract_python(archive, tmp)
                    label = dict(
                        instance_id=iid,
                        revision=row["base_commit"],
                        **patch_labels(row["patch"], Path(tmp)),
                    )
                label_cache.write_text(json.dumps(label) + "\n")
            labels.append(label)
            print(json.dumps(dict(prepared=number, total=len(rows), instance_id=iid)), flush=True)
    finally:
        shutil.rmtree(cache)
    for name, records in [("cases", public), ("labels", labels)]:
        (out / (name + ".jsonl")).write_text("".join(json.dumps(r) + "\n" for r in records))
    (out / "membership.json").write_text(json.dumps(memberships, indent=2) + "\n")
    manifest = dict(
        datasets=pins["datasets"],
        benchmark_sizes={k: len(v) for k, v in memberships.items()},
        unique_cases=len(public),
        overlap=len(set.intersection(*(set(v) for v in memberships.values()))),
        source_scope="pre-fix regular Python files; no git history",
        labels="unreviewed patch-change proxy",
        smoke=smoke,
    )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--smoke", type=int, default=0)
    a = p.parse_args()
    prepare(a.out, bool(a.smoke))
