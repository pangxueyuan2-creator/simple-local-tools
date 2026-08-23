"""Client capability profiles used for structural compatibility checks.

These profiles intentionally describe packaging-level support, not a promise
that authentication, marketplace installation, or every runtime behavior works.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientProfile:
    id: str
    label: str
    skills: bool
    mcp_stdio: bool
    mcp_streamable_http: bool
    mcp_sse: bool
    portable_extensions: bool
    note: str


PROFILES: tuple[ClientProfile, ...] = (
    ClientProfile(
        id="codex",
        label="Codex",
        skills=True,
        mcp_stdio=True,
        mcp_streamable_http=True,
        mcp_sse=False,
        portable_extensions=False,
        note="Portable Skills and MCP are supported; client-specific extensions may require a Codex package.",
    ),
    ClientProfile(
        id="cursor",
        label="Cursor",
        skills=True,
        mcp_stdio=True,
        mcp_streamable_http=True,
        mcp_sse=True,
        portable_extensions=False,
        note="Portable Skills and MCP are supported; client-specific extension namespaces vary by client.",
    ),
    ClientProfile(
        id="vscode",
        label="VS Code",
        skills=True,
        mcp_stdio=True,
        mcp_streamable_http=True,
        mcp_sse=True,
        portable_extensions=False,
        note="VS Code loads the portable Skills and MCP core and ignores unsupported client extensions.",
    ),
    ClientProfile(
        id="copilot",
        label="Copilot",
        skills=True,
        mcp_stdio=True,
        mcp_streamable_http=True,
        mcp_sse=True,
        portable_extensions=False,
        note="Agent Plugins 1.0 is supported across current GitHub Copilot agent surfaces; extra capabilities can be client-specific.",
    ),
    ClientProfile(
        id="kiro",
        label="Kiro",
        skills=True,
        mcp_stdio=True,
        mcp_streamable_http=True,
        mcp_sse=True,
        portable_extensions=False,
        note="Portable core support is ecosystem-reported; verify the exact Kiro build before making runtime claims.",
    ),
)
