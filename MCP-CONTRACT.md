# MCP contract

Servers in this repository are portable, self-describing MCP packages. An agent must be able to read a server's manifest and know how to launch it, what it needs, and what it exposes — without connecting first.

## Package layout

Place each server at `servers/<category>/<name>/` with this shape:

```text
name/
├── server.json        # manifest — required, the entry point
├── README.md          # optional, human setup notes
└── <implementation>   # server source, in any language
```

The server directory name and the manifest `name` must match. Use lowercase letters, digits, and hyphens. The `<category>` directory is a broad, reusable bucket (`travel`, `productivity`, `development`, …), not a per-server label.

## Manifest

`server.json` is the contract. Required fields:

| Field | Meaning |
|---|---|
| `name` | Matches the directory name. |
| `category` | Matches the parent directory name. |
| `description` | One sentence, at least 40 characters, that says what the server is for. |
| `version` | Server version string. |
| `transport` | `stdio`, `streamable-http`, or `sse`. |
| `launch` | `{ "command": ..., "args": [...], "cwd": "." }` — how to start it. |
| `auth` | `none`, `env`, or `oauth`. |
| `tools` | `{ "count": <int>, "search": "none" \| "regex" \| "bm25" }`. |

Optional fields: `runtime` (e.g. `python>=3.12`), `env` (declared variables), `resources` / `prompts` (`{ "count": <int> }`), `companion_skills` (list of `category/name` skills that pair with this server), `tags`.

### `env` — declare, never commit

Every environment variable the server reads is declared as an object:

```jsonc
{ "name": "DISCORD_WEBHOOK_URL", "required": false, "secret": true,
  "description": "Discord webhook for price-drop alerts." }
```

`name` is `UPPER_SNAKE_CASE`. `required` says whether the server is usable without it. `secret: true` marks credentials. **Never commit a secret value, a `.env` file, or a populated credential.** The manifest declares the variable; the operator supplies it at runtime.

## Tool search

A large tool surface wastes context and degrades tool selection. This repository enforces a threshold:

> **If `tools.count` is greater than 20, the server must apply a search transform, and `tools.search` must be `regex` or `bm25`.**

Use [FastMCP search transforms](https://gofastmcp.com/servers/transforms/tool-search) so `list_tools()` returns `search_tools` + `call_tool` instead of the full catalog. Prefer **BM25** (natural-language ranking) for agent use; use **regex** only when callers already know tool names.

```python
from fastmcp.server.transforms.search import BM25SearchTransform
mcp.add_transform(BM25SearchTransform(max_results=5))
```

Servers at or below the threshold set `"search": "none"`.

## Companion skills

A server may ship usage skills that are inseparable from its tool surface. Mount them from the server with a FastMCP skills provider rather than duplicating them here:

```python
from fastmcp.server.providers.skills import SkillProvider
mcp.add_provider(SkillProvider(Path(__file__).parent / "skills"))
```

Portable, standalone skills belong in [skill-tap](https://github.com/batteryshark/skill-tap), not inside a server. Cross-reference them with the `companion_skills` field; do not copy them in.

## Portability

Prefer launchers that need no build step and pin their version: `uvx`, `npx`, `uv run`, or `docker`. Write `launch` so that a clone runs with one command from the server directory. Keep host-specific MCP client configuration out of the package — the manifest carries everything a client needs to generate its own config.

## Executable code

Prefer the language standard library and add dependencies only when they earn their place. Python servers declare dependencies in `pyproject.toml` (with a committed `uv.lock`) or use [PEP 723](https://peps.python.org/pep-0723/) inline metadata for single-file servers. FastMCP 3.x or newer is recommended. Do not commit `__pycache__`, virtualenvs, build caches, or mutable runtime state.

## Validation

Run the repository checks before publishing:

```sh
python3 scripts/validate_mcp.py
python3 -m unittest discover -s tests
```

Also start each changed server and confirm it lists the tools, resources, and prompts its manifest claims.
