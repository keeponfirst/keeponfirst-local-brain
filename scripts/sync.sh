#!/bin/bash
# Sync scripts to skill directory (run from repo root)
set -e
SKILL_DIR="skills/keeponfirst-local-brain-skill/scripts"
SCRIPT_DIR="scripts"
cp "$SCRIPT_DIR/config.py" "$SKILL_DIR/"
cp "$SCRIPT_DIR/notion_api.py" "$SKILL_DIR/"
cp "$SCRIPT_DIR/write_record.py" "$SKILL_DIR/"
cp "$SCRIPT_DIR/log_manager.py" "$SKILL_DIR/"
cp "$SCRIPT_DIR/search.py" "$SKILL_DIR/"
cp "$SCRIPT_DIR/url_parser.py" "$SKILL_DIR/"
echo "✅ Scripts synced to skill directory"
