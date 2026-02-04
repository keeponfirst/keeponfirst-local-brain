
import asyncio
import sys
import os
from pathlib import Path

# Add package source to path
sys.path.append(os.path.abspath("packages/kof-notebooklm-mcp/src"))

from kof_notebooklm_mcp.tools.create_notebook import create_notebook
from kof_notebooklm_mcp.tools.add_source import add_source
from kof_notebooklm_mcp.config import get_config

RESEARCH_FILE = Path("/Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/records/other/20260203_125943_note_research-openai-codex-app-2026-new-launch-vs-compe.md")

async def main():
    print("Reading research content...")
    content = RESEARCH_FILE.read_text()
    
    # Clean up frontmatter or keep it? Keeping it is fine for NotebookLM context.
    
    print("Creating new notebook: 'AI Coding Tools Research (2026)'...")
    nb_result = await create_notebook(title="AI Coding Tools Research (2026)")
    
    if nb_result.error:
        print(f"Error creating notebook: {nb_result.error}")
        return

    notebook_id = nb_result.notebook_id
    print(f"Notebook created! ID: {notebook_id}")
    print(f"URL: {nb_result.url}")
    
    print("Adding research as source...")
    source_result = await add_source(
        notebook_id=notebook_id,
        source_type="text",
        text=content,
        title="Codex App Research Note"
    )
    
    if source_result.success:
        print(f"✅ Source added successfully! Source ID: {source_result.source_id}")
    else:
        print(f"❌ Failed to add source: {source_result.error}")

if __name__ == "__main__":
    asyncio.run(main())
