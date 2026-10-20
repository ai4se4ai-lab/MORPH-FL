#!/bin/bash
# Isolated diagnostic gate; submit with sbatch and explicit REVIEW_* variables.
set -euo pipefail
root="${REVIEW_ROOT:?Set REVIEW_ROOT to the frozen deployment}"
results="${REVIEW_RESULTS:?Set REVIEW_RESULTS to isolated results}"
model="${REVIEW_MODEL:?Set REVIEW_MODEL to the pinned model index}"
: "${SLURM_JOB_ID:?Run this script in a Slurm GPU allocation}"
runtime=/home/babaei/morph-ufv/runtime
review_tmp=$(mktemp -d "/tmp/morph-review-${SLURM_JOB_ID}-XXXXXX")
trap 'rm -rf "$review_tmp"' EXIT
mkdir -p "$review_tmp/packages"
tar -xf "$runtime/packages.tar" -C "$review_tmp/packages"
export SINGULARITYENV_PYTHONPATH="$root:$root/src:$review_tmp/packages"
export SINGULARITYENV_HF_HOME=/home/babaei/morph-ufv/cache/huggingface
export SINGULARITYENV_HF_HUB_OFFLINE=1
export SINGULARITYENV_HF_DATASETS_OFFLINE=1
export SINGULARITYENV_TOKENIZERS_PARALLELISM=false
export SINGULARITYENV_MORPH_MULTI_GPU=1
cd "$root"
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" \
    /opt/conda/bin/python -m experiments.full.suite preflight \
    --results "$results" --model "$model"
