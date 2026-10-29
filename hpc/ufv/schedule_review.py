#!/usr/bin/env python3
"""Queue the recurring experiment review in an existing Codex conversation.

Invoked by a user systemd timer; no separate agent or inference process is started
by this script. See docs/UFV/recurring_review.md for installation and controls.
"""

import argparse
import fcntl
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

MESSAGE = "check full experiment and tell me details of this and fix any issues"
ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--thread", required=True)
    parser.add_argument("--state-dir", type=Path,
                        default=ROOT / "hpc/logs/recurring-review")
    args = parser.parse_args()
    args.state_dir.mkdir(parents=True, exist_ok=True)
    with (args.state_dir / "queue.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another review enqueue is still running; skipping.", flush=True)
            return
        command = [str(args.codex), "queue", "--thread", args.thread,
                   "--message", MESSAGE]
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                    text=True, timeout=60)
            status = dict(returncode=result.returncode, stdout=result.stdout,
                          stderr=result.stderr)
        except subprocess.TimeoutExpired:
            # A timeout may happen after acceptance. Do not immediately retry
            # and risk posting the same request twice.
            status = dict(returncode=124, stderr="Queue command timed out; acceptance unknown.")
        status.update(checked_utc=datetime.now(UTC).isoformat(),
                      thread=args.thread, message=MESSAGE)
        temporary = args.state_dir / "status.tmp"
        temporary.write_text(json.dumps(status, indent=2) + "\n")
        temporary.replace(args.state_dir / "status.json")
        with (args.state_dir / "history.jsonl").open("a") as history:
            history.write(json.dumps(status) + "\n")
        print(json.dumps(status), flush=True)
        raise SystemExit(status["returncode"])


if __name__ == "__main__":
    main()
