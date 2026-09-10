#!/usr/bin/env python3
"""Rename files by cleaning common junk from their names."""

import argparse
import re
from pathlib import Path


def clean(name: str) -> str:
    # remove common noise
    name = re.sub(r'[\s\u3000]+', '-', name)          # spaces → -
    name = re.sub(r'[（）()【】\[\]{}]', '', name)     # brackets
    name = re.sub(r'[，。！？、；：]', '', name)       # Chinese punctuation
    name = re.sub(r'-+', '-', name)                   # collapse -
    name = name.strip('-_. ')
    return name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="folder whose files should be renamed")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show planned renames without changing any files",
    )
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error(f"not a directory: {args.folder}")
    return args


def main() -> None:
    args = parse_args()

    for f in args.folder.iterdir():
        if not f.is_file():
            continue

        # Dotfiles are often configuration or metadata files. Renaming them can
        # silently change application behavior, so leave them untouched.
        if f.name.startswith('.'):
            continue

        cleaned_stem = clean(f.stem)
        if not cleaned_stem:
            print(f"skip (empty after cleaning): {f.name}")
            continue

        new_name = cleaned_stem + f.suffix
        if new_name != f.name:
            target = f.with_name(new_name)
            if target.exists():
                print(f"skip (exists): {new_name}")
            elif args.dry_run:
                print(f"would rename: {f.name}  →  {new_name}")
            else:
                print(f"{f.name}  →  {new_name}")
                f.rename(target)


if __name__ == "__main__":
    main()
