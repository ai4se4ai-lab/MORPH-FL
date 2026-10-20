"""Sequential, resumable local pilot with model/source provenance and separate scoring."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
p.add_argument("--phase", choices=["dev", "test"], required=True)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--models", default="qwen2.5-coder:7b")
p.add_argument("--variants", default="bm25,graph,rerank,stateless_summary,no_forgetting,morph")
p.add_argument("--rounds", type=int, default=2)
args = p.parse_args()
sys.path.insert(0, str(args.source.resolve()))
from morph_fl.application import run_cases, score_predictions  # noqa: E402
from morph_fl.inference.ollama import OllamaModel  # noqa: E402

source_hash = hashlib.sha256()
for path in sorted(args.source.rglob("*.py")):
    source_hash.update(str(path.relative_to(args.source)).encode())
    source_hash.update(path.read_bytes())
if (args.out / "manifest.json").exists():
    previous = json.loads((args.out / "manifest.json").read_text())
    if previous["sha256"] != source_hash.hexdigest() or previous["phase"] != args.phase:
        raise ValueError(
            "Refusing to relabel old predictions with a different source version or split"
        )
args.out.mkdir(parents=True, exist_ok=True)
(args.out / "manifest.json").write_text(
    json.dumps(
        dict(
            source=str(args.source.resolve()),
            sha256=source_hash.hexdigest(),
            phase=args.phase,
            models=args.models,
            variants=args.variants,
            tokens=16000,
            rounds=args.rounds,
            seeds=[1],
        ),
        indent=2,
    )
    + "\n"
)
base = Path("artifacts/local/data") / args.phase
for model in args.models.split(","):
    backend = None
    for variant in args.variants.split(","):
        cell = args.out / (model.replace(":", "_") + "__" + variant)
        output = cell / "predictions.jsonl"
        print(
            json.dumps(dict(event="start", model=model, variant=variant, phase=args.phase)),
            flush=True,
        )
        started = time.monotonic()
        if variant not in {"bm25", "graph"} and backend is None:
            backend = OllamaModel(model, 1)
        run_cases(
            base / "cases.jsonl",
            output,
            None if variant in {"bm25", "graph"} else backend,
            variant=variant,
            seed=1,
            budget=16000,
            rounds=args.rounds,
            wall_seconds=300,
        )
        score_predictions(output, base / "labels.jsonl", cell / "scores.csv")
        print(
            json.dumps(
                dict(event="done", model=model, variant=variant, seconds=time.monotonic() - started)
            ),
            flush=True,
        )
