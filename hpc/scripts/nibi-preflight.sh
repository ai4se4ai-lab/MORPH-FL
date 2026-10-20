#!/usr/bin/env bash
# Read-only login-node checks. No installs, downloads, model loading or submissions.
set -euo pipefail
ssh -o BatchMode=yes -o ControlPath="$HOME/.ssh/controlmasters/%r@%h:%p" \
  mbabaei@nibi.alliancecan.ca 'hostname; id -un; sshare -U; diskusage_report; module spider python/3.11 2>&1; cat "/cvmfs/soft.computecanada.ca/custom/docs/en/Nibi.md" 2>/dev/null'
