# Notion MCP Setup Guide (Official)

The **Notion MCP (Model Context Protocol)** server allows your Agent (Antigravity/Gemini) to fully interact with your Notion workspace: **read search, write pages, and manage databases**.

We use the **Official Notion MCP Server** (`@notionhq/notion-mcp-server`) for maximum compatibility and feature support.

## Why Setup MCP?

- **Direct Integation**: Create pages and append content directly without custom scripts.
- **Deep Context**: The Agent can read your previous Worklogs to help write new ones.
- **Bi-directional**: Turns your Local Brain into a true interactive partner.

## Setup Instructions

### 1. Requirements

- `npm` (Node.js) installed.
- A Notion Integration Token (from [Notion Developers](https://www.notion.so/my-integrations)).

### 2. Configure MCP Client

Add the following to your MCP configuration file:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": [
        "-y",
        "@notionhq/notion-mcp-server"
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

Restart your MCP Client. You should see tools starting with `notion_` (or `notion-mcp-server_API` depending on client implementation).

### 4. Capabilities

The official server maps the Notion API directly to tools:

| Tool Name | Capability |
| :--- | :--- |
| `notion_post_search` | Search pages or databases |
| `notion_post_page` | Create new pages (supports any parent) |
| `notion_patch_block_children` | Append content to existing blocks |
| `notion_get_block_children` | Read page content |
| `notion_query_data_source` | Query database with filters |

## Workflow Integration

When this MCP server is active, you can ask the Agent to:
1. "Find the page titled 'Project X' and list its sub-pages"
2. "Create a new page 'Meeting Notes' under 'Project X' with this summary..."
3. "Search for 'Database Schema' and tell me the last update time"
