#!/usr/bin/env bash
# Run interactively in your own terminal. Password/MFA stay outside chat.
set -euo pipefail
install -d -m 700 "$HOME/.ssh/controlmasters"
exec ssh -o ControlMaster=yes -o ControlPersist=8h \
  -o ControlPath="$HOME/.ssh/controlmasters/%r@%h:%p" \
  mbabaei@nibi.alliancecan.ca
