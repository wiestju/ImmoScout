# AI agents (MCP)

`immoscout` ships a [Model Context Protocol](https://modelcontextprotocol.io) server, so any
MCP client — Claude Desktop, Claude Code, Cursor, … — can search real estate natively.

## Install & run

```bash
pip install "immoscout[mcp]"
immoscout-mcp        # runs the server over stdio
```

## Register it

For example, in Claude Desktop's `mcpServers` config:

```json
{
  "mcpServers": {
    "immoscout": { "command": "immoscout-mcp" }
  }
}
```

## Tools the agent gets

| Tool | Description |
| --- | --- |
| `search_listings` | Search by region, type, price/rooms/space bounds; returns listings. |
| `count_listings` | Count matches without fetching them. |
| `get_expose` | Full details for one listing ID. |
| `suggest_regions` | Resolve a place name to region paths. |

`region` accepts a place name (e.g. `"München"`) — the server resolves it to the right
geocode path automatically.

## Example prompts

- *"How many 2-room apartments under 1200 € are listed in Berlin right now?"*
- *"Find the three cheapest apartments in Munich above 60 m² and summarize them."*
- *"Look up the region path for Heidelberg, then search houses to buy there."*

The agent picks the right tools, resolves regions, and reads the typed results back to you.
