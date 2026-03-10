
import sys
import os
from pathlib import Path

# Add current directory to path so we can import config
sys.path.append(os.path.dirname(__file__))

import config
import log_manager

print(f"CWD: {os.getcwd()}")
print(f"Script Dir: {os.path.dirname(__file__)}")

try:
    print("--- Log Manager Resolution ---")
    log_home = log_manager.resolve_log_home()
    print(f"Resolved Log Home: {log_home}")
except Exception as e:
    print(f"Log Manager Failed: {e}")

print("\n--- Config Resolution ---")
try:
    cfg = config.get_config()
    print(f"Records Dir: {cfg.records_dir}")
except Exception as e:
    print(f"Config Failed: {e}")
