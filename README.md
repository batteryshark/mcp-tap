# MCP Tap

![MCP Tap — a retro comic-book mascot](assets/mcp-tap-480.png)

MCP Tap is a public registry of portable, self-describing [Model Context Protocol](https://modelcontextprotocol.io) servers. It is the sibling of [Skills Tap](https://github.com/batteryshark/skills-tap): where Skills Tap dispenses *knowledge* you copy, MCP Tap dispenses *capability* you connect to. Each server carries a `server.json` manifest so an agent knows how to launch it, what it needs, and what it exposes — before it ever connects.

## Servers

### Travel

| Server | Connect to it for | Tools |
|---|---|---|
| [`sandals`](servers/travel/sandals/) | Sandals/Beaches resort search, room availability, restaurant menus, and Discord price-drop alerts. | 13 |

## Use a server

Every server is self-describing. Read its [`server.json`](servers/travel/sandals/server.json) for the transport, launch command, required environment, and tool/resource/prompt counts, then wire it into your MCP client.

```sh
git clone https://github.com/batteryshark/mcp-tap.git
cd mcp-tap/servers/travel/sandals
uv run server            # stdio transport
```

Point your agent's MCP config at that command. For example, a stdio client entry:

```jsonc
{
  "sandals": {
    "command": "uv",
    "args": ["run", "server"],
    "cwd": "mcp-tap/servers/travel/sandals",
    "env": { "DISCORD_WEBHOOK_URL": "…optional…" }
  }
}
```

Servers that expose more than 20 tools apply a [search transform](https://gofastmcp.com/servers/transforms/tool-search): the client sees `search_tools` + `call_tool` and discovers the rest on demand. The manifest's `tools.search` field tells you which strategy is in use.

## Add a server

Put new servers under a broad category in `servers/`, follow the [MCP contract](MCP-CONTRACT.md), and run:

```sh
python3 scripts/validate_mcp.py
python3 -m unittest discover -s tests
```

Never commit secrets or `.env` files — declare required variables in the manifest's `env` list and let the operator supply them at runtime.

## License

MIT. See [LICENSE](LICENSE).
