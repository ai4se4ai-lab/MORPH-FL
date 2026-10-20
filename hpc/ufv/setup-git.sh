#!/bin/bash
set -euo pipefail
runtime=/home/babaei/morph-ufv/runtime
build=/tmp/morph-git-$SLURM_JOB_ID
mkdir -p "$build"
trap 'rm -rf "$build"' EXIT
export CONDA_PKGS_DIRS="$build/cache"
singularity exec --bind /home,/tmp "$runtime/pytorch.sif" /opt/conda/bin/conda create --yes --override-channels --channel conda-forge --prefix "$build/tools" git
# Preserve the toolchain as one archive. The stage wrapper supplies Git
# helper/template locations after extraction at its per-job local path.
mkdir -p "$build/relocated"
cp -a "$build/tools/." "$build/relocated/"
tar -cf "$runtime/git-tools.tar" -C "$build/relocated" .
