import json
from pathlib import Path

def parse_markdown(text):
    blocks = []
    lines = text.split('\n')
    i = 0
    in_code_block = False
    code_content = []
    code_lang = "plain text"

    # Skip title (first line) if it starts with #
    if lines and lines[0].startswith('# '):
        i = 1

    while i < len(lines):
        line = lines[i]
        
        # Code Block
        if line.strip().startswith('```'):
            if in_code_block:
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
                in_code_block = True
                code_lang = line.strip().replace('```', '').strip() or "plain text"
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue

        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        # Headers
        if line.startswith('## '):
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
        elif stripped.startswith('- '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]}
            })
        elif stripped.startswith('|'):
             # Simplify tables to code block for now to ensure rendering
             blocks.append({
                "object": "block",
                "type": "code",
                "code": {"rich_text": [{"type": "text", "text": {"content": line}}], "language": "plain text"}
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
    path = Path("/Users/pershing/.gemini/antigravity/brain/a2a311bc-eac1-4152-8400-653c89295403/medium_article_generated.md")
    if not path.exists():
        return
    
    content = path.read_text()
    blocks = parse_markdown(content)
    print(json.dumps(blocks))

if __name__ == "__main__":
    main()
