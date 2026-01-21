"""
Keeponfirst Local Brain - Configuration Module
Loads environment variables and provides config access.
Supports auto-initialization of Root Page.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Optional
from dotenv import load_dotenv
import log_manager

# Find project root and load .env
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Local state file for storing auto-generated config
STATE_FILE = PROJECT_ROOT / ".local_state.json"


def load_local_state() -> dict:
    """Load local state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_local_state(state: dict) -> None:
    """Save local state to file."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


@dataclass
class Config:
    """Configuration for Keeponfirst Local Brain."""
    
    notion_token: str
    notion_parent: Optional[str]  # Can be None for auto-init mode
    notion_mode: Literal["database", "page"]
    auto_init: bool  # Whether to auto-create root page
    primary_language: str # Preferred language for records (e.g., zh-TW, en)
    
    # Derived paths
    records_dir: Path
    assets_dir: Path
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables and local state."""
        token = os.getenv("NOTION_TOKEN")
        parent = os.getenv("NOTION_PARENT", "").strip()
        mode = os.getenv("NOTION_MODE", "page").lower()
        lang = os.getenv("PRIMARY_LANGUAGE", "en")
        
        if not token:
            raise ValueError("NOTION_TOKEN is required. Set it in .env file.")
        if mode not in ("database", "page"):
            raise ValueError(f"NOTION_MODE must be 'database' or 'page', got: {mode}")
        
        # Check for auto-initialized root page
        auto_init = False
        if not parent:
            state = load_local_state()
            if "root_page_id" in state:
                parent = state["root_page_id"]
                auto_init = True
        
        # Use Central Log Home as the Brain Root
        try:
            brain_root = log_manager.resolve_log_home()
        except Exception:
            # Fallback to local project root if resolution fails
            brain_root = PROJECT_ROOT

        return cls(
            notion_token=token,
            notion_parent=parent if parent else None,
            notion_mode=mode,
            auto_init=auto_init,
            primary_language=lang,
            records_dir=brain_root / "records",
            assets_dir=brain_root / "assets",
        )
    
    def ensure_dirs(self) -> None:
        """Ensure all required directories exist."""
        for subdir in ["decisions", "worklogs", "ideas", "backlogs"]:
            (self.records_dir / subdir).mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "prompts").mkdir(parents=True, exist_ok=True)
    
    def save_root_page(self, page_id: str) -> None:
        """Save auto-created root page ID to local state."""
        state = load_local_state()
        state["root_page_id"] = page_id
        save_local_state(state)
        self.notion_parent = page_id
        self.auto_init = True
    
    def needs_initialization(self) -> bool:
        """Check if we need to initialize (create root page)."""
        return self.notion_parent is None


def get_config() -> Config:
    """Get configuration singleton."""
    return Config.load()


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = get_config()
        print("✅ Configuration loaded successfully!")
        print(f"   Mode: {config.notion_mode}")
        if config.notion_parent:
            print(f"   Parent: {config.notion_parent[:8]}...")
        else:
            print("   Parent: Not set (needs initialization)")
        print(f"   Auto-init: {config.auto_init}")
        print(f"   Records: {config.records_dir}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
