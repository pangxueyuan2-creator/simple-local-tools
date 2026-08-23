# AgentProof

> **Know where your Agent Plugin actually works.**

AgentProof is a tiny, zero-dependency compatibility reporter for the new **Agent Plugins 1.0** ecosystem. Point it at a portable agent plugin and it explains whether the package's *structure* is compatible with Codex, Cursor, VS Code, GitHub Copilot, and Kiro — then generates a README-friendly SVG badge.

```text
PASS  Codex
PASS  Cursor
PASS  VS Code
PASS  Copilot
PASS  Kiro
```

Why now? Agent Plugins 1.0 was published in August 2026 as a vendor-neutral package format for Agent Skills and MCP servers. The portable core is shared, but real client support still differs by transport, authentication flow, extensions, installation path, and release version. Plugin READMEs are already growing hand-maintained compatibility tables. AgentProof makes the structural part reproducible.

## Quick start

```bash
git clone https://github.com/pangxueyuan2-creator/agentproof.git
cd agentproof
python -m pip install -e .

agentproof examples/demo-plugin
```

Generate a report:

```bash
agentproof . --format markdown -o compatibility.md
agentproof . --format json -o compatibility.json
agentproof . --format svg -o compatibility.svg
```

Then put the SVG in your README:

```md
![Agent compatibility](compatibility.svg)
```

## What it checks

AgentProof currently performs **static structural checks**:

- root `plugin.json` uses the canonical Agent Plugins 1.0 schema
- plugin names and top-level fields stay inside the portable contract
- `skills/<name>/SKILL.md` is discoverable and its frontmatter matches the directory
- `mcp.json` uses the canonical schema and declares explicit transports
- MCP transports are compared with the built-in client capability profiles
- client-specific `extensions` are surfaced as portability warnings

## What it does *not* claim

A green badge does **not** prove that OAuth works, a marketplace install succeeds, an MCP endpoint is reachable, or every client version behaves identically. AgentProof v0.1 reports *structural compatibility*. Runtime verification is deliberately a separate future layer.

That distinction matters. A surprising number of compatibility tables on the internet quietly mix "schema-valid", "installed once", and "production call succeeded" into the same green checkmark. Humans do love a reassuring emoji.

## Example

The included demo is a minimal Skills-only Agent Plugins 1.0 package:

```bash
agentproof examples/demo-plugin --format markdown
```

Output includes a client matrix, discovered components, and any validation findings.

## CI

```yaml
- run: python -m pip install -e .
- run: agentproof . --format markdown -o compatibility.md
```

The repository test matrix covers Python 3.11, 3.12, and 3.13.

## Roadmap

- [x] Agent Plugins 1.0 manifest checks
- [x] Agent Skills discovery checks
- [x] MCP transport compatibility checks
- [x] Markdown / JSON / SVG output
- [ ] Versioned client profiles with evidence URLs and dates
- [ ] GitHub Action that comments compatibility diffs on PRs
- [ ] Runtime probes for opt-in client verification
- [ ] Agent Plugins 1.1 working-draft profile

## Research basis

The project exists because the ecosystem is moving quickly:

- Agent Plugins 1.0 is the current published vendor-neutral format for portable Agent Skills and MCP servers.
- GitHub announced Agent Plugins 1.0 support across VS Code, Copilot CLI, and the Copilot app in August 2026.
- The official specification explicitly separates the portable package contract from how clients expose and operate the plugin.
- Real plugin repositories already publish client-by-client compatibility evidence because schema conformance alone does not prove runtime behavior.

See `PROJECT_PROMPT.md` for the research/build prompt used to create this MVP.

## License

MIT
