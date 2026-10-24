#!/bin/bash
# Submit on UFV; use the frozen full deployment's runtime and inference code.
set -euo pipefail
: "${PILOT_ROOT:?}" "${PILOT_RESULTS:?}" "${PILOT_CODE:?}" "${SLURM_JOB_ID:?}"
runtime=/home/babaei/morph-ufv/runtime
pilot_tmp=$(mktemp -d "/tmp/morph-pilot-${SLURM_JOB_ID}-XXXXXX")
trap 'rm -rf "$pilot_tmp"' EXIT
mkdir -p "$pilot_tmp/packages"
tar -xf "$runtime/packages.tar" -C "$pilot_tmp/packages"
export SINGULARITYENV_PYTHONPATH="$PILOT_ROOT:$PILOT_ROOT/src:$pilot_tmp/packages"
export SINGULARITYENV_HF_HOME=/home/babaei/morph-ufv/cache/huggingface
export SINGULARITYENV_HF_HUB_OFFLINE=1
export SINGULARITYENV_HF_DATASETS_OFFLINE=1
export SINGULARITYENV_TOKENIZERS_PARALLELISM=false
export SINGULARITYENV_MORPH_MULTI_GPU=1
cd "$PILOT_ROOT"
mode="${PILOT_MODE:-run}"
entry=manage.py
nv=()
args=("$mode" --results "$PILOT_RESULTS")
if [[ "$mode" == run ]]; then
    nv=(--nv)
    args+=(--model "${PILOT_MODEL:?}" --shard "${SLURM_ARRAY_TASK_ID:?}")
elif [[ "$mode" == prepare ]]; then
    args+=(--source "${PILOT_SOURCE:?}")
elif [[ "$mode" == snapshot ]]; then
    entry=snapshot.py
    args=(--results "$PILOT_RESULTS")
fi
singularity exec "${nv[@]}" --bind /home,/tmp "$runtime/pytorch.sif" \
    /opt/conda/bin/python -u "$PILOT_CODE/$entry" "${args[@]}"
