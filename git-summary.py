#!/usr/bin/env python3
"""Print a short summary of recent commits."""

import subprocess
import sys
from datetime import datetime, timedelta

def main():
    days = 14
    if "--days" in sys.argv:
        i = sys.argv.index("--days")
        days = int(sys.argv[i + 1])

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        out = subprocess.check_output(
            ["git", "log", f"--since={since}", "--pretty=format:%h %ad %an %s", "--date=short"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("Not a git repo or no commits")
        sys.exit(1)

    if not out.strip():
        print(f"No commits in the last {days} days")
        return

    print(out)

if __name__ == "__main__":
    main()
