import os
import sys
from pathlib import Path
import log_manager

print(f"Python Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print(f"Script Location: {log_manager.__file__}")
print(f"Is TTY? {sys.stdin.isatty()}")
print(f"Env Var ({log_manager.ENV_VAR_NAME}): {os.getenv(log_manager.ENV_VAR_NAME)}")

try:
    print("\n--- Starting Resolution ---")
    home = log_manager.resolve_log_home()
    print(f"✅ Resolved Home: {home}")
except Exception as e:
    print(f"❌ Resolution Failed: {e}")

print("\n--- Marker Check ---")
marker = Path(".agentic/CENTRAL_LOG_MARKER")
print(f"Marker in CWD? {marker.exists()}")
print(f"Repo Guess Path: {log_manager.SKILL_ROOT.parent}")
# In global install, SKILL_ROOT is .../skills/keeponfirst-local-brain-skill
# So parent is .../skills/ which shouldn't have marker

