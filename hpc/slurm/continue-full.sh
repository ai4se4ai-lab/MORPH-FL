#!/usr/bin/env bash
# One-shot afterok gate; no polling, downloads, or model work on login nodes.
set -euo pipefail
: "${STUDY_ROOT:?missing source deployment}"
: "${SMOKE_RUN:?missing smoke identifier}"
[[ -n "${CUDA_VISIBLE_DEVICES:-}" ]] || { echo 'No allocated GPU visible' >&2; exit 5; }
nvidia-smi -L >/dev/null
module purge
module load StdEnv/2023 python/3.11.5
cd "$STUDY_ROOT"
exec python3 hpc/scripts/continue_full.py --smoke-run "$SMOKE_RUN"
