import os
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Resolution Constraints
ENV_VAR_NAME = "ANTIGRAVITY_LOG_HOME"
MARKER_FILENAME = ".agentic/CENTRAL_LOG_MARKER"
LOG_DIR_NAME = ".agentic/logs"

# Determine path to config.json (sibling to scripts/ parent)
# Structure: skill_root/scripts/log_manager.py -> skill_root/config.json
SCRIPT_DIR = Path(__file__).parent.absolute()
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_ROOT / "config.json"


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: Dict[str, Any]):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save config to {CONFIG_FILE}: {e}", file=sys.stderr)


def is_valid_log_home(path: Path) -> bool:
    """Check if path allows creating logs."""
    try:
        marker = path / MARKER_FILENAME
        logs_dir = path / LOG_DIR_NAME
        
        # If marker exists, it's definitely a candidate
        if marker.exists():
            return True
            
        # Or if we can write to it
        if not path.exists():
            return False
            
        return os.access(path, os.W_OK)
    except Exception:
        return False


def resolve_log_home() -> Path:
    """
    Resolve Central Log Home with priority:
    1. ENV(ANTIGRAVITY_LOG_HOME)
    2. skill.resolved.central_log_home (from config.json)
    3. auto-detect marker (upwards from CWD)
    4. (TTY) ask once & persist
    5. Fail
    """
    
    # 1. Environment Variable
    env_path = os.getenv(ENV_VAR_NAME)
    if env_path:
        path = Path(env_path).resolve()
        # We assume ENV is authoritative; try to ensure dir exists
        return path

    # 2. Persisted Config
    config = load_config()
    resolved_home = config.get("resolved", {}).get("central_log_home")
    if resolved_home:
        path = Path(resolved_home).resolve()
        if path.exists():
            return path
        # If configured path is missing, fall through to re-detect/ask

    # 3. Auto-detect (Marker)
    # Start from CWD and look up
    cwd = Path.cwd()
    search_path = cwd
    while True:
        if (search_path / MARKER_FILENAME).exists():
            return search_path
        if search_path.parent == search_path:  # Root
            break
        search_path = search_path.parent
        
    # 4. Interactive Ask (if TTY)
    if sys.stdin.isatty():
        print("\n\033[33m⚠️  Central Log Home not configured.\033[0m")
        print("Please specify where to store execution logs (e.g. your local brain repo path).")
        print("This will be saved to skill config and not asked again.\n")
        
        while True:
            user_input = input("Log Home Path > ").strip()
            if not user_input:
                continue
                
            path = Path(user_input).expanduser().resolve()
            if not path.exists():
                print(f"Path does not exist: {path}")
                create = input("Create it? [y/N] ").lower()
                if create == 'y':
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        print(f"Error creating directory: {e}")
                        continue
                else:
                    continue
            
            # Persist selection
            if "resolved" not in config:
                config["resolved"] = {}
            config["resolved"]["central_log_home"] = str(path)
            config["central_log"] = {
                "strategy": "interactive_fallback_resolved",
                "format": "json"
            }
            save_config(config)
            
            # Create marker to robustify future detection
            try:
                marker = path / MARKER_FILENAME
                if not marker.parent.exists():
                    marker.parent.mkdir(parents=True, exist_ok=True)
                marker.touch()
            except Exception:
                pass # Non-critical
                
            print(f"✅ Configured Central Log Home: {path}\n")
            return path

    # 5. Fail
    raise RuntimeError(
        "Could not determine Central Log Home.\n"
        f"Please set {ENV_VAR_NAME} or run in interactive mode to configure."
    )


def ensure_log_home_exists(home: Path) -> Path:
    logs_dir = home / LOG_DIR_NAME
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def write_central_log(
    task_intent: str,
    event_data: Dict[str, Any],
    status: str = "COMPLETED"
) -> Optional[Path]:
    try:
        home = resolve_log_home()
        logs_dir = ensure_log_home_exists(home)
        
        timestamp = datetime.now().isoformat()
        safe_slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in task_intent.lower())[:50]
        filename = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{safe_slug}.json"
        log_file = logs_dir / filename
        
        log_entry = {
            "meta": {
                "timestamp": timestamp,
                "log_version": "1.0",
                "event_id": str(uuid.uuid4())
            },
            "context": {
                "workspace_cwd": str(Path.cwd()),
                "repo_root": str(home), # In this context, log home is often the repo root
                "tool": "keeponfirst-local-brain-skill"
            },
            "task": {
                "intent": task_intent,
                "status": status
            },
            "data": event_data
        }
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
            
        return log_file
    except Exception as e:
        # Fail gracefully - logging should not break the main flow
        print(f"Warning: Failed to write central log: {e}", file=sys.stderr)
        return None
