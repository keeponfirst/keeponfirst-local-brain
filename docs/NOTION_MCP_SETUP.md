# Notion MCP Setup Guide

The **Notion MCP (Model Context Protocol)** server allows your Agent (Antigravity/Gemini) to not just *write* to Notion, but also **read, search, and understand** your existing Brain.

## Why Setup MCP?

- **Context Awareness**: The Agent can read your previous Worklogs to help write new ones.
- **Search**: Ask "What was that idea I had about graph databases?" and the Agent can find it.
- **Bi-directional**: Turns your Local Brain into a true interactive partner.

## Setup Instructions

### 1. Requirements

You need `uv` installed, or another way to run the python package.

### 2. Configure Claude Desktop (or your MCP Client)

Add the following to your MCP configuration file (typically `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "notion": {
      "command": "uvx",
      "args": [
        "mcp-server-notion"
      ],
      "env": {
        "NOTION_API_TOKEN": "secret_YOUR_NOTION_TOKEN_HERE"
      }
    }
  }
}
```

> [!NOTE]
> Reuse the same `NOTION_TOKEN` you generated for the Local Brain (`.env` file).

### 3. Verify

Restart your MCP Client (e.g., Claude Desktop). You should see the `notion` server tool available.

### 4. Capabilities

Once connected, the Agent gains these tools:
- `notion_read_page`: Read content of a page.
- `notion_search`: Search pages in your workspace.
- `notion_append_block`: Add content to pages (complementing our local script).

## Integration with Local Brain

When this MCP server is active, you can ask questions like:
> "Summarize my worklogs from last week"
> "Find the decision record about the database migration"

The Agent will use the MCP tools to query your Notion Brain directly.
