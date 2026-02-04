
import asyncio
import sys
import os

# Add package source to path just in case, though pip list showed it installed
sys.path.append(os.path.abspath("packages/kof-notebooklm-mcp/src"))

from kof_notebooklm_mcp.tools.list_notebooks import list_notebooks
from kof_notebooklm_mcp.config import get_config

async def main():
    print("Checking NotebookLM configuration...")
    config = get_config()
    print(f"Profile Path: {config.profile_path}")
    
    print("Listing notebooks...")
    try:
        result = await list_notebooks(limit=10)
        
        if result.error:
            print(f"Error: {result.error}")
            return

        print(f"Found {result.total} notebooks:")
        for nb in result.notebooks:
            print(f"- [{nb.id}] {nb.name}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
