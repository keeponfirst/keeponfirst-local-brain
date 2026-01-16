#!/bin/bash
# Keeponfirst Local Brain - Project Initialization Script
# Run this in any project to set up Local Brain

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(pwd)"

echo "🧠 Initializing Keeponfirst Local Brain..."
echo "   Skill directory: $SKILL_DIR"
echo "   Project root: $PROJECT_ROOT"
echo ""

# Create records directories
echo "📁 Creating records directories..."
mkdir -p records/{decisions,worklogs,ideas,backlogs}
touch records/decisions/.gitkeep
touch records/worklogs/.gitkeep
touch records/ideas/.gitkeep
touch records/backlogs/.gitkeep

# Copy scripts
echo "📜 Copying scripts..."
mkdir -p scripts
cp "$SKILL_DIR/scripts/config.py" scripts/
cp "$SKILL_DIR/scripts/notion_api.py" scripts/
cp "$SKILL_DIR/scripts/write_record.py" scripts/
cp "$SKILL_DIR/scripts/requirements.txt" scripts/

# Create .env.example if not exists
if [ ! -f ".env.example" ]; then
  echo "📝 Creating .env.example..."
  cat > .env.example << 'EOF'
# Notion Integration Token
# Get from: https://www.notion.so/my-integrations
NOTION_TOKEN=secret_xxxxx

# Parent Page or Database ID
# Copy from the Notion page URL
NOTION_PARENT=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Mode: "page" or "database"
# page = creates child pages (simpler)
# database = creates items in a database (requires schema)
NOTION_MODE=page
EOF
fi

# Create .env from example if not exists
if [ ! -f ".env" ]; then
  echo "📝 Creating .env from template..."
  cp .env.example .env
  echo "   ⚠️  Remember to edit .env with your Notion credentials!"
fi

# Create Python virtual environment
if [ ! -d ".venv" ]; then
  echo "🐍 Creating Python virtual environment..."
  python3 -m venv .venv
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate
pip install -q -r scripts/requirements.txt

# Add to .gitignore if exists
if [ -f ".gitignore" ]; then
  if ! grep -q "^\.env$" .gitignore; then
    echo "" >> .gitignore
    echo "# Local Brain" >> .gitignore
    echo ".env" >> .gitignore
    echo ".venv/" >> .gitignore
  fi
fi

echo ""
echo "✅ Keeponfirst Local Brain initialized!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Notion credentials"
echo "  2. Use '/kof-cap' or '/kof-idea' to start capturing"
echo ""
