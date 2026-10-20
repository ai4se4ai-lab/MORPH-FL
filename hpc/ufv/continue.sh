#!/bin/bash
# Run on the login host after smoke: compute-node Slurm clients lack config access.
set -euo pipefail
if [ -n "${SLURM_JOB_ID:-}" ]; then
    echo 'Run this submission command on slurm.soc.ufv.ca outside a compute allocation.' >&2
    exit 2
fi
cd /home/babaei/projects/MORPH-FL-ufv-20261020
exec python3 hpc/scripts/continue_full.py --smoke-run ufv-smoke-20261020-01
