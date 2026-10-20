#!/bin/bash
set -euo pipefail
cd /home/babaei/projects/MORPH-FL-ufv-20261020
exec python3 hpc/scripts/continue_full.py --smoke-run ufv-smoke-20261020-01
