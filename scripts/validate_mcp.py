#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate portable MCP server packages in this repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVERS_ROOT = ROOT / "servers"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
LINK_RE = re.compile(r"\[[^]]*]\(([^)]+)\)")

TRANSPORTS = {"stdio", "streamable-http", "sse"}
AUTH = {"none", "env", "oauth"}
SEARCH = {"none", "regex", "bm25"}
TOOL_SEARCH_THRESHOLD = 20
SECRET_FILES = {".env", ".env.local", "credentials.json", "secrets.json"}


def validate_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        target = target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        file_target = target.split("#", 1)[0]
        if file_target and not (path.parent / file_target).exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link to {target}")
    return errors


def validate_count(obj: object, field: str, where: str, errors: list[str]) -> None:
    if obj is None:
        return
    if not isinstance(obj, dict) or not isinstance(obj.get("count"), int) or obj["count"] < 0:
        errors.append(f"{where}: {field} must be an object with a non-negative integer count")


def validate_server(server_dir: Path) -> list[str]:
    errors: list[str] = []
    relative = server_dir.relative_to(ROOT)
    name = server_dir.name
    category = server_dir.parent.name

    if not NAME_RE.fullmatch(name):
        errors.append(f"{relative}: invalid directory name")

    manifest_path = server_dir / "server.json"
    if not manifest_path.is_file():
        return [f"{relative}: missing server.json"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{manifest_path.relative_to(ROOT)}: invalid JSON ({exc})"]
    where = str(manifest_path.relative_to(ROOT))

    required = {"name", "category", "description", "version", "transport", "launch", "auth", "tools"}
    missing = required - manifest.keys()
    if missing:
        errors.append(f"{where}: missing required fields: {', '.join(sorted(missing))}")

    if manifest.get("name") != name:
        errors.append(f"{where}: name must match directory ({name})")
    if manifest.get("category") != category:
        errors.append(f"{where}: category must match parent directory ({category})")
    if len(str(manifest.get("description", "")).strip()) < 40:
        errors.append(f"{where}: description is too short to be useful")
    if not str(manifest.get("version", "")).strip():
        errors.append(f"{where}: version must be a non-empty string")

    if manifest.get("transport") not in TRANSPORTS:
        errors.append(f"{where}: transport must be one of {sorted(TRANSPORTS)}")
    if manifest.get("auth") not in AUTH:
        errors.append(f"{where}: auth must be one of {sorted(AUTH)}")

    launch = manifest.get("launch")
    if not isinstance(launch, dict) or not isinstance(launch.get("command"), str) \
            or not isinstance(launch.get("args"), list) \
            or not all(isinstance(arg, str) for arg in launch.get("args", [])):
        errors.append(f"{where}: launch must have a string command and a list of string args")

    tools = manifest.get("tools")
    if not isinstance(tools, dict) or not isinstance(tools.get("count"), int) \
            or tools.get("search") not in SEARCH:
        errors.append(f"{where}: tools must have an integer count and search in {sorted(SEARCH)}")
    elif tools["count"] > TOOL_SEARCH_THRESHOLD and tools["search"] == "none":
        errors.append(
            f"{where}: {tools['count']} tools exceeds {TOOL_SEARCH_THRESHOLD}; "
            f"set tools.search to 'regex' or 'bm25' (see MCP-CONTRACT.md)"
        )

    validate_count(manifest.get("resources"), "resources", where, errors)
    validate_count(manifest.get("prompts"), "prompts", where, errors)

    env = manifest.get("env", [])
    if env is not None:
        if not isinstance(env, list):
            errors.append(f"{where}: env must be a list")
        else:
            for entry in env:
                if not isinstance(entry, dict) or not ENV_RE.fullmatch(str(entry.get("name", ""))):
                    errors.append(f"{where}: each env entry needs an UPPER_SNAKE name")
                    continue
                if not isinstance(entry.get("required"), bool) or not isinstance(entry.get("secret"), bool):
                    errors.append(f"{where}: env '{entry.get('name')}' needs boolean required and secret")
                if len(str(entry.get("description", "")).strip()) < 10:
                    errors.append(f"{where}: env '{entry.get('name')}' needs a description")

    companions = manifest.get("companion_skills", [])
    if not isinstance(companions, list) or not all(isinstance(c, str) for c in companions):
        errors.append(f"{where}: companion_skills must be a list of 'category/name' strings")

    tags = manifest.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        errors.append(f"{where}: tags must be a list of strings")

    for secret in SECRET_FILES:
        if (server_dir / secret).exists():
            errors.append(f"{relative}/{secret}: secret files must not be committed")

    readme = server_dir / "README.md"
    if readme.is_file():
        errors.extend(validate_links(readme))
    return errors


def main() -> int:
    manifests = sorted(SERVERS_ROOT.glob("*/*/server.json"))
    if not manifests:
        print("No servers found", file=sys.stderr)
        return 1

    errors: list[str] = []
    for manifest in manifests:
        errors.extend(validate_server(manifest.parent))
    for path in (ROOT / "README.md", ROOT / "MCP-CONTRACT.md"):
        errors.extend(validate_links(path))

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Validated {len(manifests)} server package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
