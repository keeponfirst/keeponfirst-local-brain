#!/usr/bin/env python3
"""
Keeponfirst Local Brain - Initialization Script
Creates the root "🧠 Local Brain" page in Notion.

Usage:
    python init_brain.py <seed_page_url_or_id>
    
Example:
    python init_brain.py https://www.notion.so/My-Page-abc123...
    python init_brain.py abc12345-1234-1234-1234-123456789abc
"""

import sys
import re
from config import get_config
from notion_api import NotionClient


def extract_page_id(input_str: str) -> str:
    """Extract page ID from URL or return as-is if already an ID."""
    # Already a UUID format
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', input_str):
        return input_str
    
    # URL format - extract the ID from the end
    # https://www.notion.so/Page-Name-abc123def456...
    # https://www.notion.so/abc123def456...
    match = re.search(r'([a-f0-9]{32})(?:\?|$)', input_str)
    if match:
        raw_id = match.group(1)
        # Convert to UUID format
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    
    # Try without dashes
    if re.match(r'^[a-f0-9]{32}$', input_str):
        return f"{input_str[:8]}-{input_str[8:12]}-{input_str[12:16]}-{input_str[16:20]}-{input_str[20:]}"
    
    raise ValueError(f"Could not extract page ID from: {input_str}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python init_brain.py <seed_page_url_or_id>")
        print()
        print("This script creates the '🧠 Local Brain' root page.")
        print("Provide any Notion page URL or ID where you have write access.")
        print()
        print("Example:")
        print("  python init_brain.py https://www.notion.so/My-Page-abc123...")
        sys.exit(1)
    
    seed_input = sys.argv[1]
    
    try:
        seed_page_id = extract_page_id(seed_input)
        print(f"📌 Seed page ID: {seed_page_id}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Load config and create client
    try:
        config = get_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check if already initialized
    if not config.needs_initialization():
        print(f"⚠️  Already initialized with root page: {config.notion_parent}")
        print("   To reinitialize, delete .local_state.json first.")
        sys.exit(0)
    
    # Create client and initialize
    print("🚀 Creating Local Brain root page...")
    client = NotionClient(config)
    
    try:
        root_page = client.initialize_root_page(seed_page_id)
        print()
        print("✅ Success! Root page created:")
        print(f"   📝 Page ID: {root_page.page_id}")
        print(f"   🔗 URL: {root_page.url}")
        print()
        print("You can now use /capture to record your thoughts!")
    except Exception as e:
        print(f"❌ Failed to create root page: {e}")
        print()
        print("Make sure:")
        print("  1. Your Integration has access to the seed page")
        print("  2. The seed page URL/ID is correct")
        sys.exit(1)


if __name__ == "__main__":
    main()
