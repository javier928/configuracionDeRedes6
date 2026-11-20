#!/usr/bin/env python3
import os
import shlex
import shutil
import subprocess

# Change this code phrase every week
WEEKLY_CODE = "super-black-bird"

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def main() -> int:
    if shutil.which("croc") is None:
        print(f"{RED}Error: 'croc' was not found in PATH.{RESET}")
        return 1

    try:
        raw_input = input(f"{GREEN}Which file or folder do you want to send? {RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return 130

    if not raw_input:
        print(f"{RED}No file entered.{RESET}")
        return 1

    try:
        targets = [os.path.expanduser(p) for p in shlex.split(raw_input)]
    except ValueError:
        targets = [os.path.expanduser(raw_input.strip("\"'"))]

    missing = [p for p in targets if not os.path.exists(p)]
    if missing:
        print(f"{RED}File not found: {', '.join(missing)}{RESET}")
        return 1

    # Enable classic mode before sending (piping WEEKLY_CODE so it doesn't block)
    classic_proc = subprocess.run(
        ["croc", "--classic"],
        input=f"{WEEKLY_CODE}\n",
        text=True,
        check=False,
    )
    if classic_proc.returncode != 0:
        print(f"{RED}Failed to run classic mode (exit code {classic_proc.returncode}).{RESET}")
        return classic_proc.returncode

    cmd = ["croc", "send", "--code", WEEKLY_CODE, *targets]
    print(f"Sending with code: {WEEKLY_CODE}")

    try:
        return subprocess.run(cmd, check=False).returncode
    except KeyboardInterrupt:
        print("\nTransfer cancelled.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())