#!/bin/bash
# Host Slurm shell owns signals/requeue; the container owns experiment execution.
set -euo pipefail
export SLURM_TMPDIR="/tmp/morph-${SLURM_JOB_ID}"
mkdir -p "$SLURM_TMPDIR/packages"
runtime_pid=""
cleanup() { rm -rf "$SLURM_TMPDIR"; }
requeue() {
    if [ -n "$runtime_pid" ]; then
        kill -TERM "$runtime_pid" 2>/dev/null || true
        wait "$runtime_pid" || true
    fi
    if [ "${SLURM_RESTART_COUNT:-0}" -ge 2 ]; then
        echo 'Maximum UFV requeues reached' >&2
        exit 99
    fi
    local requeue_id="${SLURM_JOB_ID}"
    if [ -n "${SLURM_ARRAY_JOB_ID:-}" ]; then
        requeue_id="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
    fi
    scontrol requeue "$requeue_id"
    exit 0
}
trap cleanup EXIT
trap requeue USR1
tar -xf /home/babaei/morph-ufv/runtime/packages.tar -C "$SLURM_TMPDIR/packages"
mkdir -p "$SLURM_TMPDIR/tools"
tar -xf /home/babaei/morph-ufv/runtime/git-tools.tar -C "$SLURM_TMPDIR/tools"
export UFV_PACKAGES="$SLURM_TMPDIR/packages"
export GIT_EXEC_PATH="$SLURM_TMPDIR/tools/libexec/git-core"
export GIT_TEMPLATE_DIR="$SLURM_TMPDIR/tools/share/git-core/templates"
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt
export SINGULARITYENV_PREPEND_PATH="$SLURM_TMPDIR/tools/bin:/opt/conda/bin"
singularity exec --nv --bind /home,/tmp /home/babaei/morph-ufv/runtime/pytorch.sif bash "$HPC_DIR/slurm/stage-container.sh" &
runtime_pid=$!
wait "$runtime_pid"
