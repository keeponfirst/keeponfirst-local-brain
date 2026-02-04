import asyncio
import os
import sys

# Ensure we can import the local package
sys.path.append(os.path.join(os.getcwd(), "packages/kof-notebooklm-mcp/src"))

from kof_notebooklm_mcp.tools.create_notebook import create_notebook
from kof_notebooklm_mcp.tools.add_source import add_source
from kof_notebooklm_mcp.tools.ask import ask
from kof_notebooklm_mcp.client.browser import shutdown_browser
from dotenv import load_dotenv

async def main():
    load_dotenv()
    try:
        # 1. Create Notebook
        print("Creating notebook...")
        nb_result = await create_notebook(title="KOF-MCP Dev Story")
        notebook_id = nb_result.notebook_id
        print(f"Created notebook: {notebook_id}")

        # 2. Add Source (Read from artifact)
        notes_path = "/Users/pershing/.gemini/antigravity/brain/a2a311bc-eac1-4152-8400-653c89295403/dev_story_notes.md"
        with open(notes_path, "r") as f:
            content = f.read()
        
        print("Adding source...")
        await add_source(notebook_id=notebook_id, source_type="text", text=content, title="Dev Notes")

        # 3. Ask for Article
        prompt = """
        請根據這份開發筆記，寫一篇生動的 Medium 技術文章。
        
        標題建議：從零到 PyPI：我如何用逆向工程打造 NotebookLM MCP 工具
        
        文章結構要求：
        1. 引言：為什麼開發者需要這個？(痛點)
        2. 技術解密：逆向工程的挑戰 (Auth, Selectors)
        3. 架構決策：Monorepo vs Standalone 的思考
        4. PyPI 上架心得：Trusted Publisher 的便利性
        5. 結語：Dogfooding 的快樂
        
        語氣：熱情、技術硬核但易讀、鼓勵開源。
        """
        
        print("Generating article...")
        answer = await ask(notebook_id=notebook_id, question=prompt)
        
        # Output the result wrapped in a marker for easy parsing
        print("\n---ARTICLE_START---")
        print(answer.answer)
        print("---ARTICLE_END---")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await shutdown_browser()

if __name__ == "__main__":
    asyncio.run(main())
