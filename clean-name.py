#!/usr/bin/env python3
"""Rename files by cleaning common junk from their names."""

import os
import re
import sys
from pathlib import Path

def clean(name: str) -> str:
    # remove common noise
    name = re.sub(r'[\s\u3000]+', '-', name)          # spaces → -
    name = re.sub(r'[（）()【】\[\]{}]', '', name)     # brackets
    name = re.sub(r'[，。！？、；：]', '', name)       # Chinese punctuation
    name = re.sub(r'-+', '-', name)                   # collapse -
    name = name.strip('-_. ')
    return name

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean-name.py <folder>")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.is_dir():
        print("Not a directory")
        sys.exit(1)

    for f in folder.iterdir():
        if f.is_file():
            new_name = clean(f.stem) + f.suffix
            if new_name != f.name:
                target = f.with_name(new_name)
                if not target.exists():
                    print(f"{f.name}  →  {new_name}")
                    f.rename(target)
                else:
                    print(f"skip (exists): {new_name}")

if __name__ == "__main__":
    main()
