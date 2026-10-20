#!/bin/bash
set -euo pipefail
runtime=/home/babaei/morph-ufv/runtime
export SINGULARITY_CACHEDIR=/tmp/morph-build-$SLURM_JOB_ID/cache
export SINGULARITY_TMPDIR=/tmp/morph-build-$SLURM_JOB_ID/tmp
mkdir -p "$runtime" "$SINGULARITY_CACHEDIR" "$SINGULARITY_TMPDIR"
trap 'rm -rf /tmp/morph-build-$SLURM_JOB_ID' EXIT
if [ ! -s "$runtime/pytorch.sif" ]; then
    singularity pull "$runtime/pytorch.sif" docker://pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime
fi
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" /opt/conda/bin/python -m venv --system-site-packages /tmp/morph-build-$SLURM_JOB_ID/venv
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" /tmp/morph-build-$SLURM_JOB_ID/venv/bin/python -m pip install --no-cache-dir 'transformers>=4.55,<5' accelerate datasets huggingface_hub matplotlib libcst==1.8.6 sentencepiece
singularity exec --nv "$runtime/pytorch.sif" /opt/conda/bin/python --version
tar -cf "$runtime/packages.tar.tmp" -C /tmp/morph-build-$SLURM_JOB_ID/venv/lib/python3.11/site-packages .
mv "$runtime/packages.tar.tmp" "$runtime/packages.tar"
sha256sum "$runtime/pytorch.sif" "$runtime/packages.tar" > "$runtime/SHA256SUMS"
