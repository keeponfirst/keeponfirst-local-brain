"""
Keeponfirst Local Brain - Notion API Client
Minimal wrapper for Notion API operations.
Supports auto-creation of Root Page for first-time setup.
"""

import json
from typing import Optional
from dataclasses import dataclass
from notion_client import Client
from config import get_config, Config


@dataclass
class NotionPage:
    """Result of a Notion page creation."""
    page_id: str
    url: str


@dataclass
class RecordData:
    """Structured record data for Notion write."""
    record_type: str  # decision, worklog, idea, backlog
    title: str
    body_markdown: str
    date: Optional[str] = None  # ISO format YYYY-MM-DD
    tags: Optional[list[str]] = None


class NotionClient:
    """Minimal Notion API client for Keeponfirst Local Brain."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.client = Client(auth=self.config.notion_token)
    
    def initialize_root_page(self, seed_page_id: str) -> NotionPage:
        """
        Create the Local Brain root page under a seed page.
        This is called once during first-time setup.
        
        Args:
            seed_page_id: Any page ID where user has write access
            
        Returns:
            NotionPage with the new root page info
        """
        # Create the root page with nice formatting
        blocks = [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "This is your Local Brain root page. All records will be created as child pages here."}}],
                    "icon": {"emoji": "🧠"}
                }
            },
            {"object": "block", "type": "divider", "divider": {}},
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Record Types"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "⚖️ Decision — Important choices and trade-offs"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📝 Worklog — Daily activities and progress"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "💡 Idea — Unformed thoughts and inspirations"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📋 Backlog — Future tasks and TODOs"}}]}
            },
        ]
        
        response = self.client.pages.create(
            parent={"page_id": seed_page_id},
            properties={
                "title": {
                    "title": [{"text": {"content": "🧠 Local Brain"}}]
                }
            },
            children=blocks
        )
        
        root_page = NotionPage(
            page_id=response["id"],
            url=response["url"]
        )
        
        # Save to local state
        self.config.save_root_page(root_page.page_id)
        
        return root_page
    
    def create_record(self, record: RecordData) -> NotionPage:
        """
        Create a record in Notion.
        Uses either database or page mode based on config.
        """
        if self.config.needs_initialization():
            raise ValueError(
                "Root page not initialized. Call initialize_root_page() first, "
                "or set NOTION_PARENT in .env"
            )
        
        if self.config.notion_mode == "database":
            return self._create_in_database(record)
        else:
            return self._create_as_child_page(record)
    
    def _create_as_child_page(self, record: RecordData) -> NotionPage:
        """Create record as a child page under parent page."""
        # Build page content blocks
        blocks = self._markdown_to_blocks(record)
        
        # Create the page
        response = self.client.pages.create(
            parent={"page_id": self.config.notion_parent},
            properties={
                "title": {
                    "title": [{"text": {"content": record.title}}]
                }
            },
            children=blocks
        )
        
        return NotionPage(
            page_id=response["id"],
            url=response["url"]
        )
    
    def _create_in_database(self, record: RecordData) -> NotionPage:
        """Create record in a Notion database with minimal properties."""
        # Build properties - only use what's likely to exist
        properties = {
            "Name": {"title": [{"text": {"content": record.title}}]}
        }
        
        # Try to add optional properties (may fail if schema doesn't match)
        # The body will contain full structured content anyway
        
        # Build page content blocks
        blocks = self._markdown_to_blocks(record)
        
        response = self.client.pages.create(
            parent={"database_id": self.config.notion_parent},
            properties=properties,
            children=blocks
        )
        
        return NotionPage(
            page_id=response["id"],
            url=response["url"]
        )
    
    def _markdown_to_blocks(self, record: RecordData) -> list[dict]:
        """Convert record to Notion blocks."""
        blocks = []
        
        # Header with type and metadata
        type_emoji = {
            "decision": "⚖️",
            "worklog": "📝",
            "idea": "💡",
            "backlog": "📋"
        }.get(record.record_type, "📄")
        
        # Type callout
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": f"Type: {record.record_type.upper()}"}}],
                "icon": {"emoji": type_emoji}
            }
        })
        
        # Date if provided
        if record.date:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"📅 {record.date}"}}]
                }
            })
        
        # Tags if provided
        if record.tags:
            tags_text = " ".join([f"#{tag}" for tag in record.tags])
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"🏷️ {tags_text}"}}]
                }
            })
        
        # Divider
        blocks.append({"object": "block", "type": "divider", "divider": {}})
        
        # Body content - parse markdown into blocks
        blocks.extend(self._parse_markdown_body(record.body_markdown))
        
        return blocks
    
    def _parse_markdown_body(self, markdown: str) -> list[dict]:
        """
        Parse markdown into Notion blocks.
        Supports: Headers, Lists, Quotes, Code Blocks, and basic Bookmarks.
        """
        blocks = []
        lines = markdown.strip().split("\n")
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Code Blocks
            if line.strip().startswith("```"):
                language = line.strip()[3:] or "plain text"
                code_content = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_content.append(lines[i])
                    i += 1
                
                # Consume the closing ```
                if i < len(lines):
                    i += 1
                
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_content)}}],
                        "language": self._map_language(language)
                    }
                })
                continue
            
            # Headers
            if line.startswith("### "):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
                })
            elif line.startswith("## "):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
                })
            elif line.startswith("# "):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
                })
            # Bullet list
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
                })
            # Numbered list
            elif len(line) > 2 and line[0].isdigit() and line[1:3] in (". ", ") "):
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
                })
            # Quote
            elif line.startswith("> "):
                blocks.append({
                    "object": "block",
                    "type": "quote",
                    "quote": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
                })
            # Bookmark (Standalone URL)
            elif line.strip().startswith("http") and " " not in line.strip():
                blocks.append({
                    "object": "block",
                    "type": "bookmark",
                    "bookmark": {"url": line.strip()}
                })
            # Regular paragraph
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
                })
            
            i += 1
        
        return blocks

    def _map_language(self, lang: str) -> str:
        """Map common language names to Notion API supported languages."""
        lang = lang.lower().strip()
        mapping = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "md": "markdown",
            "sh": "bash",
            "shell": "bash",
            "json": "json",
            "html": "html",
            "css": "css",
            "sql": "sql",
            "go": "go",
            "java": "java",
            "c": "c",
            "cpp": "c++",
            "c++": "c++",
            "rs": "rust",
            "rust": "rust",
            "rb": "ruby",
            "ruby": "ruby",
            "php": "php",
            "swift": "swift",
            "kt": "kotlin",
            "dart": "dart",
            "yaml": "yaml",
            "yml": "yaml",
            "xml": "xml",
            "dockerfile": "docker",
            "docker": "docker"
        }
        return mapping.get(lang, "plain text")
    
    def test_connection(self) -> bool:
        """Test Notion API connection."""
        try:
            if self.config.notion_parent:
                # Try to retrieve the parent
                if self.config.notion_mode == "database":
                    self.client.databases.retrieve(self.config.notion_parent)
                else:
                    self.client.pages.retrieve(self.config.notion_parent)
            else:
                # Just test the token by getting user info
                self.client.users.me()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test connection
    print("Testing Notion connection...")
    client = NotionClient()
    if client.test_connection():
        print("✅ Notion connection successful!")
        if client.config.needs_initialization():
            print("⚠️  Root page not initialized. Run init_brain.py to set up.")
    else:
        print("❌ Notion connection failed. Check your .env settings.")
