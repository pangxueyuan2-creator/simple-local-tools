# simple-local-tools

A few small local scripts I actually use day to day.  
No frameworks, no configuration files, no "platform". Just plain files you can read and change.

---

### `clean-name.py`

Rename a bunch of files by removing common junk (spaces, Chinese punctuation, trailing numbers, etc.).

```bash
python clean-name.py /path/to/folder
```

### `find-big.py`

List the biggest files under a directory (quick and dirty).

```bash
python find-big.py /path/to/folder --top 20
```

### `git-summary.py`

Print a short summary of recent commits in the current repo (author + date + message).

```bash
python git-summary.py
python git-summary.py --days 7
```

---

These are intentionally tiny. If something is useful, copy it and modify it for yourself.
