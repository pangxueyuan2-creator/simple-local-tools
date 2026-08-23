"""Render AgentProof reports."""

from __future__ import annotations

import html
import json
from agentproof.core import Report

ICONS = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
COLORS = {"pass": "#2da44e", "warn": "#bf8700", "fail": "#cf222e"}


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: Report) -> str:
    lines = [
        f"# AgentProof report: `{report.plugin_name}`",
        "",
        f"Portable core: {'✅ valid' if report.valid_portable_core else '❌ invalid'}",
        "",
        "| Client | Status | Why |",
        "|---|---|---|",
    ]
    for client in report.clients:
        reason = "; ".join(client.reasons).replace("|", "\\|")
        lines.append(f"| {client.label} | {ICONS[client.status]} {client.status} | {reason} |")

    lines.extend(["", "## Components", ""])
    lines.append("- Skills: " + (", ".join(report.components.skills) or "none"))
    lines.append("- MCP transports: " + (", ".join(report.components.mcp_transports) or "none"))
    lines.append("- Extension namespaces: " + (", ".join(report.components.extension_namespaces) or "none"))

    if report.findings:
        lines.extend(["", "## Findings", ""])
        for finding in report.findings:
            where = f" — `{finding.location}`" if finding.location else ""
            lines.append(f"- **{finding.severity.upper()} {finding.code}**: {finding.message}{where}")
    return "\n".join(lines) + "\n"


def render_svg(report: Report) -> str:
    cells = []
    x = 0
    total_width = 0
    for client in report.clients:
        width = max(86, 9 * len(client.label) + 42)
        cells.append((x, width, client))
        x += width
        total_width += width
    height = 28
    rects: list[str] = []
    texts: list[str] = []
    for x, width, client in cells:
        rects.append(
            f'<rect x="{x}" y="0" width="{width}" height="{height}" fill="{COLORS[client.status]}"/>'
        )
        label = html.escape(f"{client.label} {ICONS[client.status]}")
        texts.append(
            f'<text x="{x + width / 2:.1f}" y="18" text-anchor="middle" '
            'font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" fill="white">'
            f"{label}</text>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}" '
        f'viewBox="0 0 {total_width} {height}" role="img" aria-label="AgentProof compatibility">'
        + "".join(rects)
        + "".join(texts)
        + "</svg>\n"
    )
