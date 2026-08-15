#!/usr/bin/env python3
"""List the biggest files under a directory."""

import os
import sys
from pathlib import Path

def human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def main():
    top = 20
    path = "."
    args = sys.argv[1:]
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        args = args[:i] + args[i+2:]
    if args:
        path = args[0]

    root = Path(path)
    files = []
    for dirpath, _, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.is_symlink():
                    continue
                size = p.stat().st_size
                files.append((size, p))
            except OSError:
                pass

    files.sort(reverse=True)
    for size, p in files[:top]:
        print(f"{human(size):>10}  {p}")

if __name__ == "__main__":
    main()
