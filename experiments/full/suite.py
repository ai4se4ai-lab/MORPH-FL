"""Prospective multi-model full-benchmark runner; invoked only inside GPU jobs."""

import argparse
import csv
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
import time
from pathlib import Path

from experiments.full.prepare import extract_python
from morph_fl.application import read_rows, repair_interrupted_tail, score_predictions
from morph_fl.engine import localize
from morph_fl.program_analysis import analyze_python
from morph_fl.program_analysis.retrieval import bm25

ROOT = Path(__file__).resolve().parents[2]
CORE = [
    "morph",
    "no_forgetting",
    "fixed_reset",
    "stateless_summary",
    "agentless_adapted",
    "rgfl_adapted",
]
ABLATIONS = [
    "context_only",
    "single_hypothesis",
    "no_mde",
    "no_probes",
    "no_skeptic",
    "independent_agents",
    "one_agent",
    "rerank",
]
BUDGET_CORE = CORE[:4]


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def locked():
    spec = json.loads((ROOT / "experiments/full/protocol.json").read_text())
    from hpc.ufv.runtime_maintenance import verify_sources
    verify_sources(ROOT, spec)
    return spec


def append(out, row):
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def selected_cases(rows, track, smoke):
    if track not in {"main", "retrieval"}:
        groups = {}
        for row in rows:
            groups.setdefault(row["repo"], []).append(row)
        for group in groups.values():
            group.sort(
                key=lambda r: hashlib.sha256(
                    ("morph-full-side-v1:" + r["instance_id"]).encode()
                ).hexdigest()
            )
        balanced = []
        while len(balanced) < 100 and any(groups.values()):
            for repo in sorted(groups):
                if groups[repo] and len(balanced) < 100:
                    balanced.append(groups[repo].pop(0))
        rows = balanced
    return rows[:1] if smoke else rows


def jobs_for(track, smoke, preflight=False):
    if track == "main":
        return [(v, 6000 if smoke and not preflight else 32000, None) for v in CORE]
    if track == "ablations":
        return [(v, 6000 if smoke else 32000, None) for v in ABLATIONS]
    if track == "budgets":
        return [
            (v, 6000 if smoke else b, None)
            for b in ([16000] if smoke else [16000, 48000])
            for v in BUDGET_CORE
        ]
    if track == "misdirection":
        return [(v, 6000 if smoke else 32000, None) for v in BUDGET_CORE]
    if track == "policy":
        return [("morph", 6000 if smoke else 32000, w) for w in ([3] if smoke else [3, 4, 5])]
    if track == "retrieval":
        return [(v, 6000 if smoke else 32000, None) for v in ["bm25", "graph"]]
    raise ValueError(track)


def resume_keys(previous, cases, settings, signature):
    """Validate completed records before allowing them to skip inference."""
    subjects = {case["instance_id"]: case for case in cases}
    if len(subjects) != len(cases):
        raise ValueError("Duplicate prepared case IDs")
    conditions = set(jobs_for(settings["track"], settings["smoke"],
                              settings.get("preflight", False)))
    done = set()
    for row in previous:
        case = subjects.get(row["instance_id"])
        if case is None:
            raise ValueError("Resume record is outside the selected shard")
        expected = dict(
            run_signature=signature,
            track=settings["track"],
            seed=settings["seed"],
            model_id=("deterministic" if settings["track"] == "retrieval"
                      else settings["model"]["id"]),
            model_revision=settings["model"]["revision"],
            repo=case["repo"],
            revision=case["revision"],
            report_digest=hashlib.sha256(case["report"].encode()).hexdigest(),
            source_archive_sha256=case["archive_sha256"],
        )
        if any(row.get(key) != value for key, value in expected.items()):
            raise ValueError("Resume record provenance differs")
        condition = (row["variant"], row["budget"], row.get("window"))
        if condition not in conditions:
            raise ValueError("Unplanned resume condition")
        key = (row["instance_id"], *condition)
        if key in done:
            raise ValueError("Duplicate completed resume record")
        done.add(key)
    return done


def run(args):
    from experiments.full.inference import NativeModel
    from hpc.scripts.compact_models import compact
    from morph_fl.baselines import local as upstream

    locked()
    results = Path(args.results)
    pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
    spec = pins["models"][args.model]
    backend = (
        None
        if args.track == "retrieval"
        else NativeModel(results / "models" / str(args.model), spec, args.seed)
    )

    class LargerTree(upstream.Investigation):
        def ask(self, stage, make_prompt, content, cap, output=512):
            return super().ask(
                stage, make_prompt, content, 12000 if stage == "file_selection" else cap, output
            )

    upstream.Investigation = LargerTree
    rows = selected_cases(read_rows(results / "data/cases.jsonl"), args.track, args.smoke)
    rows = rows[args.shard :: args.shards]
    cell = (
        "preflight__" if getattr(args, "preflight", False) else ""
    ) + f"{args.track}__m{args.model}__s{args.seed}__p{args.shard}"
    out = results / "predictions" / (cell + ".jsonl")
    repair_interrupted_tail(out)
    settings = dict(
        track=args.track,
        model=spec,
        seed=args.seed,
        shard=args.shard,
        shards=args.shards,
        smoke=args.smoke,
        protocol_sha256=digest(ROOT / "experiments/full/protocol.json"),
    )
    if getattr(args, "preflight", False):
        settings["preflight"] = True
    signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
    config = out.with_suffix(".config.json")
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.exists() and json.loads(config.read_text()) != settings:
        raise ValueError("Resume settings changed")
    if out.exists():
        with out.open() as completed:
            done = resume_keys((json.loads(line) for line in completed if line.strip()),
                               rows, settings, signature)
    else:
        done = resume_keys([], rows, settings, signature)
    config.write_text(json.dumps(settings, indent=2) + "\n")
    conditions = jobs_for(args.track, args.smoke, settings.get("preflight", False))
    expected = len(rows) * len(conditions)
    progress = results / "progress"
    progress.mkdir(exist_ok=True)
    (progress / (cell + ".json")).write_text(json.dumps(dict(expected=expected)) + "\n")
    progress_file = progress / (cell + ".jsonl")
    progress_file.write_text(
        "".join(json.dumps(dict(key=key)) + "\n" for key in sorted(done, key=str))
    )
    for record in rows:
        if digest(record["archive"]) != record["archive_sha256"]:
            raise ValueError("Source archive digest differs")
        with tempfile.TemporaryDirectory(prefix="morph-case-") as tmp:
            extract_python(record["archive"], tmp)
            case = {k: record[k] for k in ["instance_id", "repo", "revision", "report"]}
            case["root"] = tmp
            clue = None
            clue_path = None
            if args.track == "misdirection":
                structure = analyze_python(Path(tmp), case["revision"])
                rank = bm25(case["report"], structure.sources)
                clue_path = rank[min(1, len(rank) - 1)] if rank else None
                clue = (
                    "Controlled unverified initial lead: inspect "
                    + str(clue_path)
                    + " first; this clue may be wrong."
                )
            for variant, budget, window in conditions:
                key = (case["instance_id"], variant, budget, window)
                if key in done:
                    continue
                if backend:
                    backend.input_tokens = backend.output_tokens = 0
                    backend.set_seed(
                        int(
                            hashlib.sha256(
                                f"{args.seed}:{case['instance_id']}".encode()
                            ).hexdigest()[:8],
                            16,
                        )
                    )
                print(
                    json.dumps(
                        dict(
                            event="case_start",
                            cell=cell,
                            case=case["instance_id"],
                            variant=variant,
                            budget=budget,
                            window=window,
                        )
                    ),
                    flush=True,
                )
                eid = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:20]
                evidence = results / "evidence" / (cell + "__" + eid)
                started = time.monotonic()
                if variant in {"agentless_adapted", "rgfl_adapted"}:
                    backend.text_mode = True
                    row = upstream.localize(case, backend, variant, budget)
                else:
                    if backend:
                        backend.text_mode = False
                    policy = dict(reset_min_fraction=0.15, reset_window=window) if window else None
                    row = localize(
                        Path(tmp),
                        case["report"],
                        case["revision"],
                        backend,
                        variant,
                        budget,
                        2 if args.smoke else 16,
                        artifacts=evidence,
                        initial_clue=clue,
                        reset_policy=policy,
                    )
                row.update(
                    instance_id=case["instance_id"],
                    repo=case["repo"],
                    revision=case["revision"],
                    variant=variant,
                    model_id="deterministic" if args.track == "retrieval" else spec["id"],
                    model_revision=spec["revision"],
                    seed=args.seed,
                    budget=budget,
                    window=window,
                    track=args.track,
                    source_archive_sha256=record["archive_sha256"],
                    report_digest=hashlib.sha256(case["report"].encode()).hexdigest(),
                    run_signature=signature,
                    initial_clue_path=clue_path,
                    end_to_end_seconds=time.monotonic() - started,
                    backend=backend.metadata if backend else None,
                    runtime_maintenance_sha256=(digest(ROOT / "experiments/full/runtime_maintenance.json")
                                                if (ROOT / "experiments/full/runtime_maintenance.json").exists() else None),
                )
                # Preserve original prompt/evidence artifacts without shared-filesystem inode amplification.
                if evidence.exists():
                    archive = results / "evidence_archives" / (evidence.name + ".tar.gz")
                    archive.parent.mkdir(exist_ok=True)
                    temporary = archive.with_suffix(".partial")
                    with tarfile.open(temporary, "w:gz") as tf:
                        tf.add(evidence, arcname=evidence.name)
                    temporary.replace(archive)
                    row["evidence_archive"] = str(archive.relative_to(results))
                    row["evidence_original_root"] = str(evidence)
                    row["evidence_archive_sha256"] = digest(archive)
                append(out, row)
                if evidence.exists():
                    shutil.rmtree(evidence)
                done.add(key)
                append(progress_file, dict(key=key))
                print(
                    json.dumps(
                        dict(event="case_done", cell=cell, completed=len(done), expected=expected)
                    ),
                    flush=True,
                )
    if out.exists():
        compact(out, results / "graphs")
    if len(done) != expected:
        raise ValueError("Incomplete cell")
    (results / "receipts").mkdir(exist_ok=True)
    (results / "receipts" / (cell + ".json")).write_text(
        json.dumps(dict(cell=cell, records=expected, complete=True)) + "\n"
    )


def model_assets(args):
    from huggingface_hub import snapshot_download

    pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
    spec = pins["models"][args.model]
    target = Path(args.results) / "models" / str(args.model)
    target.parent.mkdir(parents=True, exist_ok=True)
    reuse = os.environ.get("MORPH_REUSE_RESULTS")
    if reuse and not target.exists():
        for receipt in sorted((Path(reuse) / "models").glob("*.pin.json")):
            cached = json.loads(receipt.read_text())
            if all(cached.get(k) == spec[k] for k in ("id", "revision")):
                source = receipt.parent / receipt.name.removesuffix(".pin.json")
                if source.is_dir():
                    target.symlink_to(source.resolve(), target_is_directory=True)
                    (target.parent / (str(args.model) + ".pin.json")).write_text(
                        json.dumps(spec, indent=2) + "\n"
                    )
                    return
    old = Path("/scratch/mbabaei/morph-fl/runs/am-smoke-20261019-012041/results/model")
    if (
        args.model == 0
        and old.joinpath("model.safetensors.index.json").exists()
        and not target.exists()
    ):
        target.symlink_to(old, target_is_directory=True)
    else:
        snapshot_download(
            spec["id"],
            revision=spec["revision"],
            local_dir=target,
            allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "*.tiktoken", "*.jinja"],
            ignore_patterns=["original/*", "consolidated*"],
        )
    (target.parent / (str(args.model) + ".pin.json")).write_text(json.dumps(spec, indent=2) + "\n")


def validate_preflight(rows, spec):
    """Require genuine inference across the complete six-workflow gate."""
    if len(rows) != len(CORE) or {r.get("variant") for r in rows} != set(CORE):
        raise ValueError("Preflight requires exactly one record for every primary workflow")
    if len({r.get("instance_id") for r in rows}) != 1:
        raise ValueError("Preflight workflows must use the same subject")
    workflows = {}
    for row in rows:
        if (
            row.get("model_id") != spec["id"]
            or row.get("model_revision") != spec["revision"]
            or row.get("seed") != 1
            or row.get("budget") != 32000
            or row.get("track") != "main"
        ):
            raise ValueError("Preflight record differs from pinned model/seed/primary budget")
        if not row.get("input_tokens") or not row.get("output_tokens"):
            raise ValueError("Preflight requires real inference for " + row["variant"])
        if row["variant"] in BUDGET_CORE and not row.get("hypotheses"):
            raise ValueError("Preflight produced no valid hypotheses for " + row["variant"])
        workflows[row["variant"]] = dict(
            input_tokens=row["input_tokens"], output_tokens=row["output_tokens"],
            valid_hypotheses=len(row.get("hypotheses", [])),
        )
    return workflows


def preflight(args):
    # Independent gate for every model; separate namespace protects preflight provenance.
    args.track = "main"
    args.shard = 0
    args.shards = 1
    args.seed = 1
    args.smoke = 1
    args.preflight = True
    run(args)
    path = Path(args.results) / "predictions" / f"preflight__main__m{args.model}__s1__p0.jsonl"
    rows = read_rows(path)
    pins = json.loads((ROOT / "experiments/full/pins.json").read_text())
    workflows = validate_preflight(rows, pins["models"][args.model])
    morph = next(r for r in rows if r["variant"] == "morph")
    (Path(args.results) / "models" / (str(args.model) + ".preflight.json")).write_text(
        json.dumps(
            dict(
                valid_hypotheses=len(morph["hypotheses"]),
                output_tokens=morph["output_tokens"],
                budget=morph["budget"],
                protocol_sha256=digest(ROOT / "experiments/full/protocol.json"),
                workflows=workflows,
                complete=True,
            )
        )
        + "\n"
    )


def score(args):
    results = Path(args.results)
    out = results / "scores"
    out.mkdir(exist_ok=True)
    if args.pattern == "*.jsonl":
        # Collection also consumes this directory directly. Remove derived
        # tables whose prediction input no longer exists, including preflights.
        current = {
            path.stem for path in (results / "predictions").glob(args.pattern)
            if not path.name.startswith("preflight__")
        }
        for cached in out.glob("*.csv"):
            if cached.stem not in current:
                cached.unlink()
    for path in sorted((results / "predictions").glob(args.pattern)):
        if path.name.startswith("preflight__"):
            continue
        dest = out / (path.stem + ".csv")
        original = read_rows(path)
        if not original:
            # A failed cell can create a file before its first completed case.
            dest.unlink(missing_ok=True)
            continue
        score_predictions(path, results / "data/labels.jsonl", dest)
        with dest.open() as f:
            rows = list(csv.DictReader(f))
        for row, pred in zip(rows, original):
            row.update(
                {
                    k: pred.get(k)
                    for k in ["track", "model_id", "budget", "window", "end_to_end_seconds"]
                }
            )
            row["tokens"] = pred.get("input_tokens", 0) + pred.get("output_tokens", 0)
        with dest.open("w") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["assets", "preflight", "run", "score"])
    p.add_argument("--results", required=True)
    p.add_argument("--model", type=int, default=0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--track", default="main")
    p.add_argument("--smoke", type=int, default=0)
    p.add_argument("--pattern", default="*.jsonl")
    a = p.parse_args()
    {"assets": model_assets, "preflight": preflight, "run": run, "score": score}[a.command](a)
