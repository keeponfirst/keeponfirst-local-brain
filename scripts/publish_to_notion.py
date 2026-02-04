import os
import re
from pathlib import Path
from notion_client import Client
from config import get_config

def parse_markdown(text):
    blocks = []
    lines = text.split('\n')
    i = 0
    in_code_block = False
    code_content = []
    code_lang = "plain text"

    while i < len(lines):
        line = lines[i]
        
        # Code Block
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_content)}}],
                        "language": code_lang if code_lang else "plain text"
                    }
                })
                in_code_block = False
                code_content = []
            else:
                # Start of code block
                in_code_block = True
                code_lang = line.strip().replace('```', '').strip() or "plain text"
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue

        # Headers
        if line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
            })
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
            })
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
            })
        # List Items
        elif line.strip().startswith('- '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line.strip()[2:]}}]}
            })
        # Empty Line
        elif not line.strip():
            pass 
        # Table (skip for now, or treat as code/text)
        elif line.strip().startswith('|'):
             blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
            })
        # Paragraph
        else:
             blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
            })
        
        i += 1
        
    return blocks

def main():
    config = get_config()
    client = Client(auth=config.notion_token)
    
    # Read Article
    article_path = Path("/Users/pershing/.gemini/antigravity/brain/a2a311bc-eac1-4152-8400-653c89295403/medium_article_generated.md")
    if not article_path.exists():
        print("Article file not found.")
        return
        
    content = article_path.read_text()
    
    # Extract Title (First line usually)
    lines = content.split('\n')
    title = "Generated Article"
    if lines and lines[0].startswith('# '):
        title = lines[0][2:]
        content = "\n".join(lines[1:]) # Remove title from body
        
    blocks = parse_markdown(content)
    
    print(f"Creating page '{title}' under parent {config.notion_parent}...")
    
    try:
        response = client.pages.create(
            parent={"page_id": config.notion_parent},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            children=blocks[:100] # Notion limit 100 blocks per request
        )
        # If > 100 blocks, append children (TODO if needed, article is short)
        
        print(f"✅ Successfully created page: {response['url']}")
        
    except Exception as e:
        print(f"❌ Error creating page: {e}")

if __name__ == "__main__":
    main()
