#!/usr/bin/env python3
"""
Keeponfirst Local Brain - Health Check
Quick diagnostic for all dependencies.

Usage:
    python health_check.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Resolve skill root (health_check.py is in scripts/)
SCRIPT_DIR = Path(__file__).parent.absolute()
SKILL_ROOT = SCRIPT_DIR.parent

# Add script dir to path for imports
sys.path.insert(0, str(SCRIPT_DIR))


def check_env_file() -> Dict[str, Any]:
    """Check if .env file exists and has required keys."""
    env_path = SKILL_ROOT / ".env"
    if not env_path.exists():
        return {
            "status": "FAIL",
            "message": ".env 檔案不存在",
            "hint": f"請複製 .env.example 並設定: cp {SKILL_ROOT}/.env.example {env_path}"
        }
    
    # Check for NOTION_TOKEN
    from dotenv import dotenv_values
    env_vars = dotenv_values(env_path)
    
    if not env_vars.get("NOTION_TOKEN"):
        return {
            "status": "FAIL", 
            "message": "NOTION_TOKEN 未設定",
            "hint": "請到 notion.so/my-integrations 建立 Integration 並複製 Token"
        }
    
    return {
        "status": "OK",
        "message": f".env 設定正常 (NOTION_TOKEN: {env_vars['NOTION_TOKEN'][:10]}...)"
    }


def check_notion_api() -> Dict[str, Any]:
    """Test Notion API connectivity."""
    try:
        from config import get_config
        from notion_api import NotionClient
        
        config = get_config()
        client = NotionClient()
        
        # Try to retrieve the parent page (lightweight check)
        if config.notion_parent:
            # Simple API call to verify connectivity
            import requests
            headers = {
                "Authorization": f"Bearer {config.notion_token}",
                "Notion-Version": "2022-06-28"
            }
            start = datetime.now()
            resp = requests.get(
                f"https://api.notion.com/v1/pages/{config.notion_parent}",
                headers=headers,
                timeout=10
            )
            latency = (datetime.now() - start).total_seconds() * 1000
            
            if resp.status_code == 200:
                return {
                    "status": "OK",
                    "message": f"Notion API 連線正常 ({latency:.0f}ms)",
                    "parent_id": config.notion_parent[:8] + "..."
                }
            elif resp.status_code == 401:
                return {
                    "status": "FAIL",
                    "message": "Token 無效或已過期",
                    "hint": "請到 notion.so/my-integrations 檢查 Token"
                }
            elif resp.status_code == 404:
                return {
                    "status": "FAIL",
                    "message": "找不到 Parent Page",
                    "hint": "請確認 NOTION_PARENT 設定正確，且 Integration 有存取權限"
                }
            else:
                return {
                    "status": "FAIL",
                    "message": f"API 回應異常: {resp.status_code}",
                    "hint": resp.text[:100]
                }
        else:
            return {
                "status": "WARN",
                "message": "NOTION_PARENT 未設定",
                "hint": "執行 python scripts/init_brain.py 初始化"
            }
            
    except ImportError as e:
        return {
            "status": "FAIL",
            "message": f"缺少依賴: {e}",
            "hint": "執行 pip install -r scripts/requirements.txt"
        }
    except Exception as e:
        error_msg = str(e).lower()
        if "dns" in error_msg or "resolve" in error_msg or "getaddrinfo" in error_msg:
            return {
                "status": "FAIL",
                "message": "DNS 解析失敗",
                "hint": "請檢查網路連線，嘗試 ping api.notion.com"
            }
        elif "timeout" in error_msg:
            return {
                "status": "FAIL",
                "message": "連線逾時",
                "hint": "請檢查網路連線或防火牆設定"
            }
        return {
            "status": "FAIL",
            "message": str(e),
            "hint": "請檢查網路連線"
        }


def check_local_storage() -> Dict[str, Any]:
    """Verify local storage is writable."""
    try:
        from config import get_config
        config = get_config()
        
        # Check records dir
        records_dir = config.records_dir
        if not records_dir.exists():
            records_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = records_dir / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
            return {
                "status": "OK",
                "message": f"本地儲存正常",
                "path": str(records_dir)
            }
        except PermissionError:
            return {
                "status": "FAIL",
                "message": f"無寫入權限: {records_dir}",
                "hint": "請檢查目錄權限或變更 Central Log 位置"
            }
            
    except Exception as e:
        return {
            "status": "FAIL",
            "message": str(e)
        }


def check_mcp_config() -> Dict[str, Any]:
    """
    Check MCP configuration.
    Search upward from skill root for .mcp.json or mcp_config.json.
    Also check common IDE-specific locations.
    """
    mcp_files = [".mcp.json", "mcp_config.json"]
    found_configs = []
    
    # 1. Search upward from skill root
    search_path = SKILL_ROOT
    while True:
        for mcp_file in mcp_files:
            candidate = search_path / mcp_file
            if candidate.exists():
                found_configs.append(str(candidate))
        
        if search_path.parent == search_path:  # Root
            break
        search_path = search_path.parent
    
    # 2. Check common IDE locations
    home = Path.home()
    ide_locations = [
        home / ".gemini" / "antigravity" / "mcp_config.json",  # Antigravity
        home / ".cursor" / "mcp.json",  # Cursor
        home / ".claude" / "mcp.json",  # Claude
    ]
    
    for loc in ide_locations:
        if loc.exists() and str(loc) not in found_configs:
            found_configs.append(str(loc))
    
    if not found_configs:
        return {
            "status": "WARN",
            "message": "未找到 MCP 設定檔",
            "hint": "如需使用 MCP 功能，請參考 docs/NOTION_MCP_SETUP.md"
        }
    
    # Check if notion-mcp-server is configured
    notion_mcp_found = False
    for config_path in found_configs:
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                servers = config.get("mcpServers", config.get("servers", {}))
                if any("notion" in k.lower() for k in servers.keys()):
                    notion_mcp_found = True
                    break
        except Exception:
            pass
    
    if notion_mcp_found:
        return {
            "status": "OK",
            "message": "MCP 設定正常 (notion-mcp-server 已配置)",
            "configs": found_configs
        }
    else:
        return {
            "status": "WARN",
            "message": "MCP 設定存在但未配置 notion-mcp-server",
            "configs": found_configs,
            "hint": "如需搜尋/回顧功能，請配置 notion-mcp-server"
        }


def print_result(name: str, result: Dict[str, Any]):
    """Print formatted check result."""
    status = result["status"]
    emoji = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(status, "❓")
    
    print(f"{emoji} {name}: {result['message']}")
    
    if "path" in result:
        print(f"   📁 {result['path']}")
    if "configs" in result:
        for c in result["configs"]:
            print(f"   📄 {c}")
    if "hint" in result and status != "OK":
        print(f"   💡 {result['hint']}")


def main():
    print("🔍 Keeponfirst Local Brain 健康檢查")
    print("=" * 45)
    print()
    
    checks = [
        ("環境設定 (.env)", check_env_file),
        ("Notion API", check_notion_api),
        ("本地儲存", check_local_storage),
        ("MCP 設定", check_mcp_config),
    ]
    
    results = []
    for name, check_fn in checks:
        result = check_fn()
        results.append((name, result))
        print_result(name, result)
        print()
    
    # Summary
    print("=" * 45)
    ok_count = sum(1 for _, r in results if r["status"] == "OK")
    warn_count = sum(1 for _, r in results if r["status"] == "WARN")
    fail_count = sum(1 for _, r in results if r["status"] == "FAIL")
    
    if fail_count == 0 and warn_count == 0:
        print("🎉 所有檢查通過！")
    elif fail_count == 0:
        print(f"⚠️  {ok_count} 通過, {warn_count} 警告")
    else:
        print(f"❌ {ok_count} 通過, {warn_count} 警告, {fail_count} 失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
