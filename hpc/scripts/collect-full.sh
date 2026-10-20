#!/usr/bin/env bash
# Local result transfer/promotion. No monitoring loop and no credentials in source.
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo 'Usage: bash hpc/scripts/collect-full.sh REMOTE_DEPLOYMENT RUN_ID [--update-paper]' >&2
  exit 2
fi
study_deployment="$1"
study_run="$2"
if [[ ! "$study_deployment" =~ ^/project/[A-Za-z0-9_/-]+/MORPH-FL-full-v[0-9]+$ ]] || [[ ! "$study_run" =~ ^am(-smoke)?-[0-9]{8}-[0-9]{6}$ ]]; then
  echo 'Unexpected deployment/run identifier' >&2
  exit 2
fi
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
transfer_dir="$repo_dir/artifacts/full/$study_run"
study_ssh_socket="${MORPH_SSH_SOCKET:-$HOME/.ssh/controlmasters/mbabaei@nibi.alliancecan.ca:22}"
mkdir -p "$transfer_dir" "$repo_dir/experiments/full/results/$study_run"
rsync -az -e "ssh -o BatchMode=yes -S $study_ssh_socket" \
  "mbabaei@nibi.alliancecan.ca:$study_deployment/hpc/logs/$study_run/" "$transfer_dir/logs/"
# Compact scientific outputs, not model weights or large source snapshots.
rsync -az -e "ssh -o BatchMode=yes -S $study_ssh_socket" \
  --include='/analysis/***' --include='/data/' --include='/data/manifest.json' --include='/data/membership.json' \
  --exclude='*' "mbabaei@nibi.alliancecan.ca:/scratch/mbabaei/morph-fl/runs/$study_run/results/" "$transfer_dir/"
if [[ -d "$transfer_dir/analysis" ]]; then
  rsync -a "$transfer_dir/analysis/" "$repo_dir/experiments/full/results/$study_run/"
fi
if [[ "${3:-}" == '--update-paper' ]]; then
  if [[ -x "$repo_dir/artifacts/baselines-venv/bin/python" ]]; then
    study_python="$repo_dir/artifacts/baselines-venv/bin/python"
  else
    study_python="${PYTHON:-python3}"
  fi
  PYTHONPATH="$repo_dir/src:$repo_dir" "$study_python" "$repo_dir/experiments/full/paper_update.py" \
    --results "$transfer_dir" --paper "$repo_dir/docs/TSE"
  tectonic -X compile "$repo_dir/docs/TSE/morph-fl.tex" --keep-logs --keep-intermediates
fi
