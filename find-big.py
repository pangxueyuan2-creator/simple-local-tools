#!/usr/bin/env python3
"""List the biggest files under a directory."""

import argparse
import os
from pathlib import Path


def human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=Path("."), type=Path)
    parser.add_argument("--top", type=positive_int, default=20, help="number of files to show")
    args = parser.parse_args()
    if not args.path.is_dir():
        parser.error(f"not a directory: {args.path}")
    return args


def main() -> None:
    args = parse_args()
    files: list[tuple[int, Path]] = []

    for dirpath, _, filenames in os.walk(args.path, followlinks=False):
        for name in filenames:
            path = Path(dirpath) / name
            try:
                if path.is_symlink():
                    continue
                files.append((path.stat().st_size, path))
            except OSError:
                pass

    files.sort(key=lambda item: item[0], reverse=True)
    for size, path in files[: args.top]:
        print(f"{human(size):>10}  {path}")


if __name__ == "__main__":
    main()
