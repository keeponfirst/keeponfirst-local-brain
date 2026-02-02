---
description: Publish local markdown content to Notion using the Official MCP
---

This workflow allows you to publish a local markdown file (like an article, research note, or documentation) directly to a Notion page.

1. **Prerequisites**
   - Ensure the Official Notion MCP server is configured (`@notionhq/notion-mcp-server`).
   - You have a target markdown file ready.

2. **Search for Parent Page**
   - Use `notion_post_search` to find the parent page where you want to publish.
   - Example: `Target Page Name`

3. **Create Page**
   - Use `notion_post_page` to create the new page under the identified `parent_id`.
   - **Important**: The content must be converted to Notion Blocks.
   - If the file is complex, you can write a temporary python script to parse it, OR ask the Agent to "read the file and create a Notion page with the same content".

4. **Verify**
   - The tool will return the URL of the created page.
   - Share this URL with the user.

**Example Prompt:**
> "Publish the file `articles/my-draft.md` to Notion under the 'KOF Knowledge Base' page."
