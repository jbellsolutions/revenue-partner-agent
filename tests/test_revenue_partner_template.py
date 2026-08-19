from __future__ import annotations

import importlib.util
import base64
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / "files"
SKILL = FILES / "skills/go-to-market/revenue-partner/SKILL.md"
SB = FILES / "local-packages/super-browser"


def load_builder():
    spec = importlib.util.spec_from_file_location("revenue_partner_builder", ROOT / "build_template.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RevenuePartnerTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def test_template_identity_is_revenue_partner(self):
        self.assertEqual(self.builder.NAME, "revenue-partner-agent")
        self.assertRegex(self.builder.VERSION, r"^\d+\.\d+\.\d+$")
        self.assertNotIn("Buzz", self.builder.template["template"]["name"])
        self.assertIn("Revenue Partner", self.builder.template["template"]["description"])

    def test_required_product_files_exist(self):
        required = [
            SKILL,
            SKILL.parent / "references/operating-system.md",
            SKILL.parent / "references/campaign-contract.md",
            SKILL.parent / "references/source-ledger.md",
            SKILL.parent / "references/acceptance-tests.md",
            FILES / "agent-knowledge/INDEX.md",
            FILES / "agent-knowledge/01.Agent Operating System/02.Permissions.md",
            FILES / "agent-knowledge/02.GTM System/01.Company and Offer.md",
            FILES / "agent-knowledge/02.GTM System/02.ICP and Fit.md",
            FILES / "agent-knowledge/03.Campaigns/INDEX.md",
            FILES / "safe-env-bridge.py",
            SB / "UPSTREAM_COMMIT",
            SB / "pyproject.toml",
            SB / "src/super_browser/mcp_server.py",
            SB / ".codex-plugin/plugin.json",
            SB / ".mcp.json",
            SB / "scripts/verify-super-browser",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), str(path))

    def test_config_wires_super_browser_stdio_mcp(self):
        config = (FILES / "config.yaml").read_text()
        self.assertIn("super-browser:", config)
        self.assertIn("/usr/local/bin/super-browser-server", config)
        self.assertIn("SUPER_BROWSER_STATE_DIR", config)
        self.assertNotIn("Buzz", config)

    def test_builder_installs_and_validates_super_browser(self):
        text = (ROOT / "build_template.py").read_text()
        self.assertIn("local-packages/super-browser", text)
        self.assertIn("playwright install chromium", text)
        self.assertIn("super_browser.providers", text)
        self.assertIn("super_browser.mcp_server", text)
        self.assertIn("revenue-partner-smoke", text)
        self.assertIn("requirements-runtime.lock", text)
        self.assertIn("--require-hashes", text)
        self.assertIn("list_resources", text)

    def test_resume_hook_never_sources_or_raw_echoes_secrets(self):
        hook = self.builder.ON_RESUME
        self.assertIn("revenue-partner-env-bridge", hook)
        self.assertNotIn(". /root/.env", hook)
        self.assertNotIn(". /root/.hermes/.env", hook)
        self.assertNotIn('echo "${K}=${V}"', hook)

    def test_gateway_execs_through_safe_environment_bridge(self):
        gateway = (FILES / "gateway-run.sh").read_text()
        self.assertIn("revenue-partner-env-bridge --exec", gateway)
        self.assertNotIn(". /root/.env", gateway)
        self.assertNotIn('. "$HERMES_HOME/.env"', gateway)

    def test_unavailable_local_validation_fails_closed(self):
        with mock.patch.dict(sys.modules, {"jsonschema": None}):
            self.assertFalse(self.builder.local_validate())

    def test_publish_requires_successful_local_or_remote_validation(self):
        with (
            mock.patch.object(self.builder, "local_validate", return_value=False),
            mock.patch.object(self.builder, "remote_validate", return_value=False),
            mock.patch.object(self.builder, "publish") as publish,
            mock.patch.object(self.builder, "API_KEY", "test-only-placeholder"),
            mock.patch.object(sys, "argv", ["build_template.py", "--publish"]),
        ):
            with self.assertRaises(SystemExit):
                self.builder.main()
            publish.assert_not_called()

    def test_http_failures_are_not_reported_as_success(self):
        original = self.builder._req
        try:
            setattr(self.builder, "_req", lambda *args, **kwargs: (409, "collision"))
            self.assertFalse(self.builder.publish())
            setattr(self.builder, "_req", lambda *args, **kwargs: (500, "failed"))
            self.assertFalse(self.builder.remote_validate())
            self.assertFalse(self.builder.build_and_stream())
        finally:
            setattr(self.builder, "_req", original)

    def test_launch_without_workspace_is_controlled_error(self):
        env = os.environ.copy()
        env["ORGO_API_KEY"] = "test-only-placeholder"
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_template.py"), "--launch"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--launch requires a workspace_id", result.stderr + result.stdout)
        self.assertNotIn("IndexError", result.stderr)

    def test_template_declares_optional_provider_secrets_without_values(self):
        names = {item["name"] for item in self.builder.template["secrets"]}
        for name in {
            "browser_use_api_key",
            "airtop_api_key",
            "decodo_proxy",
            "hyperbrowser_api_key",
            "steel_api_key",
            "browserbase_api_key",
        }:
            self.assertIn(name, names)
        rendered = str(self.builder.template)
        supplied_key = os.environ.get("ORGO_API_KEY", "")
        if supplied_key:
            self.assertNotIn(supplied_key, rendered)

    def test_vendor_is_pinned_and_importable(self):
        commit = (SB / "UPSTREAM_COMMIT").read_text().strip()
        self.assertEqual(commit, "552822fd86a74d574ff9c0d87db6e6b82f929d96")
        for rel in (
            ".codex-plugin/plugin.json",
            ".mcp.json",
            "references/provider-matrix.md",
            "skills/playwright-specialist/SKILL.md",
            "skills/super-browser-orchestrator/SKILL.md",
            "configs/hermes-mcp.yaml",
            "docs/setup-walkthrough.md",
            "scripts/super-browser",
            "scripts/verify-super-browser",
        ):
            self.assertTrue((SB / rel).exists(), rel)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SB / "src")
        env["SUPER_BROWSER_REPO_ROOT"] = str(SB)
        code = (
            "from super_browser.providers import PROVIDERS; "
            "assert len(PROVIDERS) == 8; "
            "from super_browser.mcp_server import main, list_resources; "
            "assert len(list_resources()) >= 20; "
            "print(','.join(PROVIDERS))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], env=env, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().split(",")), 8)

        manifest_code = (
            "from pathlib import Path; from super_browser.bundle import build_bundle_manifest; "
            f"m=build_bundle_manifest(Path({str(SB)!r})); "
            "assert m['status']=='ok' and not m['missing_required_paths']"
        )
        manifest = subprocess.run(
            [sys.executable, "-c", manifest_code], env=env, text=True, capture_output=True, check=False
        )
        self.assertEqual(manifest.returncode, 0, manifest.stderr)

    def test_super_browser_ad_campaign_phrases_require_approval(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SB / "src")
        env["SUPER_BROWSER_REPO_ROOT"] = str(SB)
        blocked_phrases = [
            "launch an ad campaign",
            "create an ad",
            "run the campaign",
            "create a campaign",
            "launch a paid social campaign",
            "run an advertising campaign",
            "activate the ads",
            "launch a paid-social campaign",
            "create an email campaign",
            "launch our ad campaign",
            "create the new ad campaign",
            "start a B2B campaign",
            "activate an influencer campaign",
            "run my advertising campaign",
            "enable our retargeting ads",
            "turn on the search campaign",
            "take our campaign live",
            "kick off our campaign",
            "fire up that email campaign",
            "go live with the B2B campaign",
            "roll out our influencer campaign",
            "deploy the new campaign",
            "schedule my campaign",
            "promote our campaign",
            "Draft an internal ad campaign plan, then launch it",
            "Create an ad campaign draft for internal review only; then publish it",
            "For internal review, outline the campaign and activate it",
            "Draft campaign copy, do not publish it; launch the campaign instead",
            "Prepare an internal advertising strategy. After review, go live with it",
            "Create a campaign proposal for review and schedule it tomorrow",
            "Create a local CSV of leads, then launch the ad campaign",
            "Export prospects to a local JSON file and activate the advertising campaign",
            "Save customer leads locally; then schedule our campaign",
            "Launch adverts",
            "Fire up an advert",
            "Search for ad campaign examples, then launch it",
            "Send me a report on the ad campaign, then activate it",
            "Review our campaign metrics and then schedule it",
            "What is this ad campaign? Then turn it on",
            "Analyze and then launch our ad campaign",
            "Explain how to launch the campaign",
            "Compare these campaigns and activate the winner",
            "Draft an internal campaign plan, then greenlight it",
            "Send me a report on the ad campaign, then greenlight it",
            "Search for ad campaign examples, then greenlight one",
            "Analyze the campaign and greenlight it",
            "draft an ad campaign plan for internal review; do not launch it",
            "create an ad campaign draft for internal review only; do not publish",
            "Draft an internal advert plan without launching it",
            "Launch it after you draft an internal ad campaign plan",
            "Activate it before drafting the internal advert proposal",
            "Greenlight it after you draft an internal ad campaign plan",
            "Draft an internal campaign plan to greenlight it",
            "Draft an internal advert plan: greenlight it",
            "Draft internal advertising copy—ship it",
            "For review only, draft a campaign plan to commission it",
            "Never launch it; draft an internal campaign plan, afterward greenlight it",
        ]
        safe_phrases = [
            "research examples of ad campaigns",
            "analyze our ad campaign performance",
            "compare three advertising campaigns",
            "what is an ad campaign?",
            "explain advertising campaign metrics",
            "give me a report on ad campaigns",
            "Submit the public search form for visible advert examples",
        ]
        with tempfile.TemporaryDirectory() as state_dir:
            env["SUPER_BROWSER_STATE_DIR"] = state_dir
            code = (
                "import super_browser.runtime as runtime; "
                f"blocked={blocked_phrases!r}; safe={safe_phrases!r}; "
                "runtime.execute_plan=lambda plan: (_ for _ in ()).throw(RuntimeError('provider execution reached')); "
                "blocked_runs=[runtime.create_run(goal, execute=True) for goal in blocked]; "
                "safe_runs=[runtime.create_run(goal, execute=False) for goal in safe]; "
                "assert all(run.status == 'awaiting_approval' for run in blocked_runs), "
                "list(zip(blocked, [run.status for run in blocked_runs])); "
                "assert all(run.status == 'planned' and not run.approvals for run in safe_runs), "
                "list(zip(safe, [(run.status, len(run.approvals)) for run in safe_runs]))"
            )
            result = subprocess.run(
                [sys.executable, "-c", code], env=env, text=True, capture_output=True, check=False
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_payload_contains_skill_vendor_and_vault_seed(self):
        setup = self.builder.template["apps"][0]["install"]
        self.assertIn("agent-knowledge", setup)
        self.assertIn("super-browser", setup)
        inline = "\n".join(item.get("inline", "") for item in self.builder.template["files"])
        supplied_key = os.environ.get("ORGO_API_KEY", "")
        if supplied_key:
            self.assertNotIn(supplied_key, inline)

    def test_payload_ships_only_curated_revenue_partner_skill(self):
        payload = next(item for item in self.builder.template["files"] if item["to"].endswith("payload.tgz.b64"))
        with tarfile.open(fileobj=io.BytesIO(base64.b64decode(payload["inline"])), mode="r:gz") as archive:
            skill_files = {
                member.name
                for member in archive.getmembers()
                if member.name.startswith("hermes/skills/") and member.name.endswith("/SKILL.md")
            }
        self.assertEqual(skill_files, {"hermes/skills/go-to-market/revenue-partner/SKILL.md"})

    def test_agentphone_is_deny_by_default_and_cannot_enable_full_tools(self):
        bridge = (FILES / "agentphone-bridge/agentphone_bridge.py").read_text()
        bridge_env = (FILES / "agentphone-bridge/env").read_text()
        self.assertNotIn("HERMES_YOLO_MODE", bridge_env)
        self.assertNotIn("FULL_HERMES_TOOLSETS", bridge + bridge_env)
        self.assertNotIn('"all"', bridge_env)
        self.assertIn("if not allowed or sender not in allowed", bridge)
        self.assertIn('(\"web\", \"vision\")', bridge)
        self.assertIn("explicit operator approval", bridge)

    def test_public_metadata_does_not_point_to_base_template(self):
        self.assertNotIn("source", self.builder.template["template"])

    def test_shipped_template_has_no_base_runtime_identity(self):
        rendered = str(self.builder.template)
        for legacy in ("nicks-stack", "Dewey", "Minions", "Hubert"):
            self.assertNotIn(legacy, rendered)
        self.assertIn("/opt/revenue-partner/stage", rendered)
        self.assertIn("revenue-partner-onboard-launch.sh", rendered)

    def test_readme_qualifies_campaign_enforcement_boundary(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("Hard runtime gating is implemented in Super Browser and the AgentPhone bridge", readme)
        self.assertIn("rather than a claimed universal campaign-record gate", readme)


if __name__ == "__main__":
    unittest.main()
