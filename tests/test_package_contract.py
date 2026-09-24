"""Packaging-only checks; no live gateway or production profile is loaded."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin" / "codex_tasks"


def test_plugin_manifest_requires_installation_specific_settings():
    manifest = yaml.safe_load((PLUGIN / "plugin.yaml").read_text(encoding="utf-8"))
    schema = manifest["config_schema"]
    assert schema["profile"]["required"] is True
    assert schema["owner_conversation_id"]["required"] is True
    assert schema["cwd"]["required"] is True
    assert schema["state_path"]["default"] == "gateway/codex_app_tasks.sqlite"


def test_plugin_has_no_deployment_specific_absolute_paths_or_ids():
    for path in (PLUGIN / "__init__.py", PLUGIN / "plugin.yaml"):
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text
        assert "/Applications/" not in text
        assert re.search(r"\b\d{17,20}\b", text) is None


def test_plugin_exposes_owner_recovery_command():
    plugin_text = (PLUGIN / "__init__.py").read_text(encoding="utf-8")
    assert "codex-recover" in plugin_text


def test_config_example_is_placeholder_only():
    text = (ROOT / "examples" / "ownerreview-config.yaml").read_text(encoding="utf-8")
    assert "DISCORD_OWNER_DM_ID" in text
    assert "/path/to/codex/workspace" in text
    assert "/Users/" not in text
