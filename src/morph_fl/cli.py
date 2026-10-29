"""Command-line interface; orchestration and algorithms live in their packages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .application import run_cases, score_predictions
from .search.config import VARIANTS


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="MORPH-FL: evidence-preserving fault localization")
    sub = root.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser(
        "prepare", help="Prepare pinned SWE-bench Lite snapshots and separate labels"
    )
    prepare.add_argument("--out", type=Path, required=True)
    prepare.add_argument("--limit", type=int, default=300)
    prepare.add_argument("--revision", required=True)
    download = sub.add_parser("download-model")
    download.add_argument("--model", required=True)
    download.add_argument("--revision", required=True)
    download.add_argument("--out", required=True)
    run = sub.add_parser("run", help="Localize public cases; never reads evaluator labels")
    run.add_argument("--cases", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--variant", choices=VARIANTS, default="morph")
    run.add_argument("--model")
    run.add_argument("--backend", choices=("transformers", "ollama"), default="transformers")
    run.add_argument("--ollama-endpoint", default="http://127.0.0.1:11434")
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--budget", type=int, default=16000)
    run.add_argument("--rounds", type=int, default=12)
    run.add_argument("--limit", type=int, default=300)
    run.add_argument("--max-probes", type=int, default=48)
    run.add_argument("--wall-seconds", type=float, default=3600)
    run.add_argument("--require-inference", action="store_true")
    run.add_argument(
        "--reset-policy", type=Path, help="JSON reset parameters; recorded in run settings"
    )
    run.add_argument(
        "--sandbox",
        type=Path,
        help="JSON: pinned Apptainer image and registered procedure argv lists",
    )
    run.add_argument(
        "--initial-clue", help="Explicitly disclosed controlled misdirection experiment"
    )
    score = sub.add_parser("score")
    score.add_argument("--predictions", type=Path, required=True)
    score.add_argument("--labels", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    external = sub.add_parser("import-agentless")
    external.add_argument("--input", type=Path, required=True)
    external.add_argument("--cases", type=Path, required=True)
    external.add_argument("--out", type=Path, required=True)
    analysis = sub.add_parser("analyze")
    analysis.add_argument("--results", type=Path, required=True)
    analysis.add_argument("--out", type=Path, required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "prepare":
        from .datasets.swebench import prepare

        prepare(args.out, args.limit, args.revision)
    elif args.command == "download-model":
        from huggingface_hub import snapshot_download

        snapshot_download(args.model, revision=args.revision, local_dir=args.out)
    elif args.command == "run":
        from .inference import LocalModel
        from .investigation import SandboxConfig

        if args.variant not in {"bm25", "graph"} and not args.model:
            raise SystemExit("--model is required for inference variants")
        if args.variant in {"bm25", "graph"}:
            backend = None
        elif args.backend == "ollama":
            from .inference.ollama import OllamaModel

            backend = OllamaModel(args.model, args.seed, endpoint=args.ollama_endpoint)
        else:
            backend = LocalModel(args.model, args.seed)
        sandbox = SandboxConfig(**json.loads(args.sandbox.read_text())) if args.sandbox else None
        run_cases(
            args.cases,
            args.out,
            backend,
            variant=args.variant,
            seed=args.seed,
            budget=args.budget,
            rounds=args.rounds,
            limit=args.limit,
            sandbox=sandbox,
            require_inference=args.require_inference,
            initial_clue=args.initial_clue,
            max_probes=args.max_probes,
            wall_seconds=args.wall_seconds,
            reset_policy=json.loads(args.reset_policy.read_text()) if args.reset_policy else None,
        )
    elif args.command == "score":
        score_predictions(args.predictions, args.labels, args.out)
    elif args.command == "analyze":
        from .evaluation.statistics import analyze

        analyze(args.results, args.out)
    elif args.command == "import-agentless":
        from .evaluation.external import import_agentless

        import_agentless(args.input, args.cases, args.out)


if __name__ == "__main__":
    main()
