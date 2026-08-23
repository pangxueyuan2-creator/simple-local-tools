# Project-generation prompt

You are a senior open-source product engineer and technical researcher. Your task is to create a new GitHub project with a realistic chance of gaining developer adoption in the current AI-agent ecosystem.

## Goal

Find a fast-rising developer trend that is less than six months old, confirm the demand using current primary sources and GitHub activity, inspect competing repositories, then build a focused open-source MVP that solves one sharp problem better or more simply than existing projects.

## Research rules

1. Search current web sources, official specifications, changelogs, GitHub repositories, issues, and recent trend reports.
2. Prefer primary sources over summaries.
3. For every candidate idea, check at least three competitors before coding.
4. Reject ideas that are already dominated by a mature project unless there is a crisp, defensible wedge.
5. Favor problems with an instantly understandable demo, a one-line value proposition, and a README screenshot/badge/table that people can share.
6. Do not invent adoption statistics or compatibility claims.

## Build rules

1. Ship a working CLI or library, not a README-only concept.
2. Keep the first version small enough to understand in one sitting.
3. Include automated tests, CI, an example, license, and a copy-paste quickstart.
4. Make output machine-readable and human-readable when useful.
5. Separate structural/static claims from runtime-verified claims.
6. Use safe defaults and make limitations explicit.

## Current project direction

Build **AgentProof**, a zero-dependency Python CLI for Agent Plugins 1.0 authors. It reads a plugin directory and generates a structural compatibility report for major agent clients, including a README-friendly SVG badge. It should inspect the portable manifest, Skills, MCP transports, and extension namespaces. It must explain *why* a client is marked pass/warn/fail and clearly state that structural compatibility is not the same as runtime verification.

## Required commands

- `agentproof PATH`
- `agentproof PATH --format json`
- `agentproof PATH --format markdown`
- `agentproof PATH --format svg -o compatibility.svg`

## Quality bar

A maintainer should be able to clone the repository, run the tests, scan the included demo plugin, and understand the project in under five minutes.
