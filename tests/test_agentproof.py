from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentproof.core import MCP_SCHEMA, PLUGIN_SCHEMA, analyze_plugin
from agentproof.render import render_markdown, render_svg


class AgentProofTests(unittest.TestCase):
    def make_plugin(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "plugin.json").write_text(
            json.dumps({"$schema": PLUGIN_SCHEMA, "name": "demo-plugin", "version": "0.1.0"}),
            encoding="utf-8",
        )
        skill = root / "skills" / "hello"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: hello\ndescription: Say hello.\n---\n\nSay hello.\n",
            encoding="utf-8",
        )
        return root

    def test_valid_skill_only_plugin_passes(self):
        report = analyze_plugin(self.make_plugin())
        self.assertTrue(report.valid_portable_core)
        self.assertEqual(report.components.skills, ("hello",))
        self.assertTrue(all(client.status == "pass" for client in report.clients))

    def test_codex_warns_or_fails_on_sse(self):
        root = self.make_plugin()
        (root / "mcp.json").write_text(
            json.dumps(
                {
                    "$schema": MCP_SCHEMA,
                    "mcpServers": {"legacy": {"type": "sse", "url": "https://example.com/sse"}},
                }
            ),
            encoding="utf-8",
        )
        report = analyze_plugin(root)
        codex = next(item for item in report.clients if item.client == "codex")
        self.assertEqual(codex.status, "fail")
        self.assertIn("sse", " ".join(codex.reasons))

    def test_nonportable_manifest_field_is_error(self):
        root = self.make_plugin()
        (root / "plugin.json").write_text(
            json.dumps({"$schema": PLUGIN_SCHEMA, "name": "demo-plugin", "hooks": {}}),
            encoding="utf-8",
        )
        report = analyze_plugin(root)
        self.assertFalse(report.valid_portable_core)
        self.assertIn("AP012", {item.code for item in report.findings})

    def test_extension_namespace_produces_warning_status(self):
        root = self.make_plugin()
        (root / "plugin.json").write_text(
            json.dumps(
                {
                    "$schema": PLUGIN_SCHEMA,
                    "name": "demo-plugin",
                    "extensions": {"com.example.client": {"feature": True}},
                }
            ),
            encoding="utf-8",
        )
        report = analyze_plugin(root)
        self.assertTrue(report.valid_portable_core)
        self.assertTrue(all(client.status == "warn" for client in report.clients))

    def test_markdown_and_svg_render(self):
        report = analyze_plugin(self.make_plugin())
        markdown = render_markdown(report)
        svg = render_svg(report)
        self.assertIn("| Codex |", markdown)
        self.assertIn("<svg", svg)
        self.assertIn("Cursor", svg)


if __name__ == "__main__":
    unittest.main()
