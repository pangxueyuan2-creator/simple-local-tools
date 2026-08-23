"""Command-line interface for AgentProof."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentproof import __version__
from agentproof.core import Report, analyze_plugin
from agentproof.render import render_json, render_markdown, render_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentproof",
        description="Structural compatibility reports for Agent Plugins 1.0",
    )
    parser.add_argument("path", nargs="?", default=".", type=Path, help="Agent Plugin directory")
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json", "svg"),
        default="text",
        help="Output format",
    )
    parser.add_argument("-o", "--output", type=Path, help="Write output to a file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_plugin(args.path)
    content = _render(report, args.format)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")

    return 0 if report.valid_portable_core else 1


def _render(report: Report, fmt: str) -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "markdown":
        return render_markdown(report)
    if fmt == "svg":
        return render_svg(report)
    return _render_text(report)


def _render_text(report: Report) -> str:
    lines = [
        f"AgentProof: {report.plugin_name}",
        f"Portable core: {'PASS' if report.valid_portable_core else 'FAIL'}",
        "",
    ]
    for client in report.clients:
        lines.append(f"{client.status.upper():4}  {client.label}")
        for reason in client.reasons:
            lines.append(f"      {reason}")
    if report.findings:
        lines.extend(["", "Findings:"])
        for finding in report.findings:
            where = f" ({finding.location})" if finding.location else ""
            lines.append(f"  [{finding.severity.upper()}] {finding.code}: {finding.message}{where}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
