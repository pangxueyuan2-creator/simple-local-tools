#!/usr/bin/env python3
"""Print a short summary of recent commits."""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days",
        type=positive_int,
        default=14,
        help="number of days of commit history to include (default: 14)",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    since = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    try:
        out = subprocess.check_output(
            [
                "git",
                "log",
                f"--since={since}",
                "--pretty=format:%h %ad %an %s",
                "--date=short",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("git is not installed or not available on PATH")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Not a git repo or no commits")
        sys.exit(1)

    if not out.strip():
        print(f"No commits in the last {args.days} days")
        return

    print(out)


if __name__ == "__main__":
    main()
