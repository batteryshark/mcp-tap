# sandals

Luxury travel concierge MCP server for Sandals and Beaches Resorts. Built on FastMCP 3.x.

See [`server.json`](server.json) for the full manifest. Summary:

- **Transport:** stdio (default), or streamable-http when `PORT` is set
- **Tools:** 13 — resort search, room and restaurant lookup, availability and flexible-date checks, and price watches
- **Resources:** 1 (`sandals://resorts/all`) · **Prompts:** 1 (`plan_vacation`)
- **Auth:** environment (`DISCORD_WEBHOOK_URL`, optional)

## Run

```sh
uv run server            # stdio
PORT=8000 uv run server  # streamable-http on :8000
```

## Environment

| Variable | Required | Purpose |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | no | Discord webhook for price-drop alerts. Price-watch tools run but stay silent until it is set. |
| `PORT` | no | Serve over streamable-http on this port instead of stdio. |
| `HOST` | no | Bind host for the HTTP transport (default `127.0.0.1`). |

Never commit a real webhook URL — supply it in your environment at runtime.

## Test

```sh
uv run pytest
```
