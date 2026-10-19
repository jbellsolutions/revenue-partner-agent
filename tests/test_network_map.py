"""The relcore network map as this agent ships it: a local MCP server with no credential and no send tool."""
import base64
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "files"
PKG = FILES / "local-packages" / "relcore"
SEND_LIKE = re.compile(r"draft|wave|send|sent|reply|replies|approve|apply|import|purge|unsuppress|scorecard|call_ingest|plan_save",
                       re.I)


class NetworkMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = yaml.safe_load((FILES / "config.yaml").read_text())["mcp_servers"]["relcore"]

    def test_relcore_is_local_stdio_with_no_baked_secret(self):
        s = self.server
        self.assertEqual((s["command"], s["args"]), ("python3", ["-m", "relcore.mcp_server", "--mode", "plugin"]))
        self.assertNotIn("url", s)
        for key, value in s["env"].items():
            if key.endswith(("_KEY", "_TOKEN")):
                self.assertEqual(value, "${%s}" % key, f"{key} must come from the bridged environment")
        self.assertTrue(s["env"]["RELCORE_VAULT"].startswith("/root/Documents/HermesVault/"),
                        "cards render into the agent's Obsidian vault")

    def test_pinned_tools_can_read_record_and_map_but_never_send_or_bulk_import(self):
        include = self.server["tools"]["include"]
        self.assertEqual(len(include), len(set(include)))
        for name in include:
            self.assertTrue(name.startswith("rel_"), name)
            self.assertIsNone(SEND_LIKE.search(name.replace("rel_network_plan", "rel_network_preview")), name)
        for name in ("rel_network_plan", "rel_network_map", "rel_network_job", "rel_network_report",
                     "rel_network_deep_plan", "rel_network_page_add", "rel_network_deep",
                     "rel_network_li_allow", "rel_network_li_record", "rel_network_li_block", "rel_suppress"):
            self.assertIn(name, include)

    def test_deep_pass_reaches_claude_opus(self):
        env = self.server["env"]
        self.assertEqual(env["ANTHROPIC_API_KEY"], "${ANTHROPIC_API_KEY}", "the deep pass runs on Claude Opus 5.5")
        bridge = (FILES / "safe-env-bridge.py").read_text()
        self.assertEqual(bridge.count('"ANTHROPIC_API_KEY"'), 2, "both key lists carry the Anthropic key")

    def test_vendored_server_registers_every_pinned_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(PKG), "TRP_REPO": str(PKG), "PYTHONDONTWRITEBYTECODE": "1",
                   "RELCORE_HOME": f"{tmp}/home", "RELCORE_VAULT": f"{tmp}/vault",
                   "RELCORE_STOP_FILE": f"{tmp}/STOP"}
            msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
            out = subprocess.run([sys.executable, "-m", "relcore.mcp_server", "--mode", "plugin"], cwd=tmp, env=env,
                                 input="\n".join(json.dumps(m) for m in msgs) + "\n", capture_output=True, text=True,
                                 timeout=60, check=True)
        tools = next(json.loads(line) for line in out.stdout.splitlines() if json.loads(line).get("id") == 2)
        names = {t["name"] for t in tools["result"]["tools"]}
        self.assertFalse(set(self.server["tools"]["include"]) - names, "a pinned tool the server does not register")

    def test_vendored_copy_records_its_upstream_commit(self):
        upstream = (PKG / "UPSTREAM.md").read_text()
        self.assertRegex(upstream, r"commit `[0-9a-f]{40}`")
        tracked = subprocess.check_output(["git", "ls-files", "--", str(PKG.relative_to(ROOT))], cwd=ROOT, text=True)
        self.assertNotIn("__pycache__", tracked, "no build artifacts in the vendored copy")
        for need in ("relcore/network/__init__.py", "policies/permissions.json", "data/revenue-partnerships.json"):
            self.assertTrue((PKG / need).is_file(), need)

    def test_payload_ships_relcore_and_the_skill(self):
        sys.path.insert(0, str(ROOT))
        import build_template
        payload = next(item for item in build_template.template["files"] if item["to"].endswith("payload.tgz.b64"))
        with tarfile.open(fileobj=io.BytesIO(base64.b64decode(payload["inline"])), mode="r:gz") as archive:
            names = set(archive.getnames())
        self.assertIn("hermes/local-packages/relcore/relcore/network/__init__.py", names)
        self.assertIn("hermes/local-packages/relcore/policies/permissions.json", names)
        self.assertIn("hermes/skills/go-to-market/network-map/SKILL.md", names)

    def test_skill_keeps_the_linkedin_and_bulk_import_rules(self):
        skill = (FILES / "skills/go-to-market/network-map/SKILL.md").read_text()
        for rule in ("never theirs", "rel_network_li_block", "Never solve or route around it",
                     "Send no messages and post no content, ever", "zero writes", "rel_network_page_add",
                     "potentially knows", "Never run the deep pass on a weaker model", "relcore network apply",
                     "do-not-contact"):
            self.assertIn(rule, skill)


if __name__ == "__main__":
    unittest.main()
