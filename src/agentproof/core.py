"""Static Agent Plugins 1.0 compatibility analysis."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agentproof.profiles import PROFILES, ClientProfile

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
ALLOWED_PLUGIN_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
PLUGIN_NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^(?!.*--)[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    location: str | None = None


@dataclass(frozen=True)
class Components:
    skills: tuple[str, ...]
    mcp_transports: tuple[str, ...]
    extension_namespaces: tuple[str, ...]


@dataclass(frozen=True)
class ClientResult:
    client: str
    label: str
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Report:
    plugin_name: str
    version: str | None
    valid_portable_core: bool
    components: Components
    findings: tuple[Finding, ...]
    clients: tuple[ClientResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "plugin_name": self.plugin_name,
            "version": self.version,
            "valid_portable_core": self.valid_portable_core,
            "components": asdict(self.components),
            "findings": [asdict(item) for item in self.findings],
            "clients": [asdict(item) for item in self.clients],
        }


def analyze_plugin(root: Path) -> Report:
    root = root.resolve()
    findings: list[Finding] = []
    manifest_path = root / "plugin.json"
    plugin_name = root.name
    version: str | None = None
    manifest: dict[str, Any] = {}

    if not root.is_dir():
        findings.append(Finding("error", "AP001", "Plugin path is not a directory", str(root)))
    elif not manifest_path.is_file():
        findings.append(Finding("error", "AP002", "Missing root plugin.json", str(manifest_path)))
    else:
        manifest = _read_json_object(manifest_path, findings, "AP003")
        if manifest:
            plugin_name = str(manifest.get("name") or root.name)
            raw_version = manifest.get("version")
            version = raw_version if isinstance(raw_version, str) else None
            _validate_manifest(manifest, manifest_path, findings)

    skills = _scan_skills(root, findings)
    mcp_transports = _scan_mcp(root, findings)
    extension_namespaces = _scan_extensions(manifest, findings, manifest_path)
    components = Components(
        skills=tuple(skills),
        mcp_transports=tuple(sorted(mcp_transports)),
        extension_namespaces=tuple(extension_namespaces),
    )

    clients = tuple(_score_client(profile, components, findings) for profile in PROFILES)
    valid_portable_core = not any(item.severity == "error" for item in findings)

    return Report(
        plugin_name=plugin_name,
        version=version,
        valid_portable_core=valid_portable_core,
        components=components,
        findings=tuple(findings),
        clients=clients,
    )


def _read_json_object(path: Path, findings: list[Finding], code: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(Finding("error", code, f"Invalid JSON: {exc}", str(path)))
        return {}
    if not isinstance(data, dict):
        findings.append(Finding("error", code, "Expected a JSON object", str(path)))
        return {}
    return data


def _validate_manifest(manifest: dict[str, Any], path: Path, findings: list[Finding]) -> None:
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        findings.append(Finding("error", "AP010", f"$schema must be {PLUGIN_SCHEMA}", str(path)))

    name = manifest.get("name")
    if not isinstance(name, str) or not PLUGIN_NAME_RE.fullmatch(name):
        findings.append(Finding("error", "AP011", "name must use lowercase letters, numbers, dots, or hyphens", str(path)))

    unknown = sorted(set(manifest) - ALLOWED_PLUGIN_FIELDS)
    if unknown:
        findings.append(
            Finding(
                "error",
                "AP012",
                "Non-portable top-level manifest fields: " + ", ".join(unknown),
                str(path),
            )
        )

    extensions = manifest.get("extensions")
    if extensions is not None and not isinstance(extensions, dict):
        findings.append(Finding("warning", "AP013", "extensions should be an object keyed by client namespace", str(path)))


def _scan_skills(root: Path, findings: list[Finding]) -> list[str]:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    if not skills_dir.is_dir():
        findings.append(Finding("error", "AP020", "skills must be a directory", str(skills_dir)))
        return []

    names: list[str] = []
    for child in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            findings.append(Finding("warning", "AP021", "Only immediate skill directories are portable", str(child)))
            continue
        skill_file = child / "SKILL.md"
        if not skill_file.is_file():
            findings.append(Finding("error", "AP022", "Skill directory is missing SKILL.md", str(child)))
            continue
        frontmatter = _parse_frontmatter(skill_file)
        declared = frontmatter.get("name")
        description = frontmatter.get("description")
        if declared != child.name or not SKILL_NAME_RE.fullmatch(child.name):
            findings.append(
                Finding(
                    "error",
                    "AP023",
                    "Skill frontmatter name must match its kebab-case directory name",
                    str(skill_file),
                )
            )
        if not isinstance(description, str) or not description.strip():
            findings.append(Finding("error", "AP024", "Skill requires a non-empty description", str(skill_file)))
        names.append(child.name)
    return names


def _parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def _scan_mcp(root: Path, findings: list[Finding]) -> set[str]:
    path = root / "mcp.json"
    if not path.exists():
        return set()
    data = _read_json_object(path, findings, "AP030")
    if not data:
        return set()
    if set(data) - {"$schema", "mcpServers"}:
        findings.append(Finding("error", "AP031", "mcp.json has non-portable top-level fields", str(path)))
    if data.get("$schema") != MCP_SCHEMA:
        findings.append(Finding("error", "AP032", f"mcp.json $schema must be {MCP_SCHEMA}", str(path)))
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        findings.append(Finding("error", "AP033", "mcpServers must be an object", str(path)))
        return set()

    transports: set[str] = set()
    for name, config in servers.items():
        if not isinstance(config, dict):
            findings.append(Finding("error", "AP034", f"MCP server {name!r} must be an object", str(path)))
            continue
        transport = config.get("type")
        if transport not in {"stdio", "streamable-http", "sse"}:
            findings.append(Finding("error", "AP035", f"MCP server {name!r} has an unknown type", str(path)))
            continue
        transports.add(str(transport))
        if transport == "stdio" and not isinstance(config.get("command"), str):
            findings.append(Finding("error", "AP036", f"stdio server {name!r} requires command", str(path)))
        if transport in {"streamable-http", "sse"} and not isinstance(config.get("url"), str):
            findings.append(Finding("error", "AP037", f"remote server {name!r} requires url", str(path)))
    return transports


def _scan_extensions(
    manifest: dict[str, Any], findings: list[Finding], manifest_path: Path
) -> list[str]:
    extensions = manifest.get("extensions")
    if not isinstance(extensions, dict):
        return []
    namespaces: list[str] = []
    for namespace, value in sorted(extensions.items()):
        if not isinstance(namespace, str) or "." not in namespace:
            findings.append(Finding("warning", "AP040", f"Suspicious extension namespace: {namespace!r}", str(manifest_path)))
            continue
        if not isinstance(value, dict):
            findings.append(Finding("warning", "AP041", f"Extension {namespace!r} should be an object", str(manifest_path)))
        namespaces.append(namespace)
    return namespaces


def _score_client(profile: ClientProfile, components: Components, findings: list[Finding]) -> ClientResult:
    reasons: list[str] = []
    blocking = any(item.severity == "error" for item in findings)
    if blocking:
        reasons.append("Portable core has validation errors")

    if components.skills and not profile.skills:
        reasons.append("Skills are not supported by this profile")

    for transport in components.mcp_transports:
        supported = {
            "stdio": profile.mcp_stdio,
            "streamable-http": profile.mcp_streamable_http,
            "sse": profile.mcp_sse,
        }[transport]
        if not supported:
            reasons.append(f"MCP transport {transport} is not supported")

    if components.extension_namespaces and not profile.portable_extensions:
        reasons.append("Client-specific extension namespaces are not portable across all clients")

    if blocking or any("not supported" in reason for reason in reasons):
        status = "fail"
    elif reasons:
        status = "warn"
    else:
        status = "pass"
        reasons.append(profile.note)

    return ClientResult(profile.id, profile.label, status, tuple(reasons))
