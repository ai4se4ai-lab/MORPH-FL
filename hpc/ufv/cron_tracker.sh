#!/usr/bin/env bash
# Invoke via cron every 30 minutes. The enclosing flock prevents overlapping checks.
set -euo pipefail
TRACKER_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
TRACKER_DEST="$TRACKER_ROOT/hpc/logs/ufv-full-v12-20261020"
mkdir -p "$TRACKER_DEST"
exec /usr/bin/flock -n "$TRACKER_DEST/cron-tracker.lock" \
    /usr/bin/python3 "$TRACKER_ROOT/hpc/ufv/watch_collect.py" \
    --once --destination "$TRACKER_DEST" >> "$TRACKER_DEST/monitor.log" 2>&1
