#!/usr/bin/env python3
"""
Keeponfirst Local Brain - Record Writer
Writes records to Notion and syncs to local storage.

Usage:
    python write_record.py --input record.json
    python write_record.py --dry-run --input record.json
    echo '{"type": "idea", ...}' | python write_record.py --stdin
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

from config import get_config, PROJECT_ROOT
from notion_api import NotionClient, RecordData, NotionPage
import log_manager


@dataclass
class LocalRecord:
    """Complete record stored locally."""
    type: str
    title: str
    created_at: str
    notion_page_id: Optional[str]
    notion_url: Optional[str]
    source_text: str
    final_body: str
    tags: Optional[list[str]] = None
    date: Optional[str] = None


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a filesystem-safe slug."""
    # Replace spaces and special chars
    slug = text.lower()
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in slug)
    # Remove consecutive dashes
    while "--" in slug:
        slug = slug.replace("--", "-")
    # Trim
    slug = slug.strip("-")
    return slug[:max_length]


def generate_filename(record_type: str, title: str) -> str:
    """Generate filename: timestamp_type_slug"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(title)
    return f"{timestamp}_{record_type}_{slug}"


def save_local(record: LocalRecord, config) -> tuple[Path, Path]:
    """Save record to local storage as markdown and JSON."""
    config.ensure_dirs()
    
    # Determine subdirectory
    type_dirs = {
        "decision": "decisions",
        "worklog": "worklogs",
        "idea": "ideas",
        "backlog": "backlogs"
    }
    subdir = type_dirs.get(record.type, "other")
    base_dir = config.records_dir / subdir
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    base_name = generate_filename(record.type, record.title)
    
    # Save JSON
    json_path = base_dir / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(record), f, ensure_ascii=False, indent=2)
    
    # Save Markdown (human readable)
    md_path = base_dir / f"{base_name}.md"
    md_content = generate_markdown(record)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return md_path, json_path


def generate_markdown(record: LocalRecord) -> str:
    """Generate human-readable markdown from record."""
    type_emoji = {
        "decision": "⚖️",
        "worklog": "📝",
        "idea": "💡",
        "backlog": "📋"
    }.get(record.type, "📄")
    
    lines = [
        f"# {type_emoji} {record.title}",
        "",
        f"**Type:** {record.type.upper()}",
        f"**Created:** {record.created_at}",
    ]
    
    if record.date:
        lines.append(f"**Date:** {record.date}")
    
    if record.tags:
        lines.append(f"**Tags:** {', '.join(record.tags)}")
    
    if record.notion_url:
        lines.append(f"**Notion:** [{record.notion_page_id[:8]}...]({record.notion_url})")
    
    lines.extend([
        "",
        "---",
        "",
        record.final_body,
        "",
        "---",
        "",
        "## Original Input",
        "",
        f"> {record.source_text}",
    ])
    
    return "\n".join(lines)


def write_record(
    input_data: dict,
    dry_run: bool = False
) -> dict:
    """
    Write a record to Notion and local storage.
    
    Args:
        input_data: Dictionary with record data
        dry_run: If True, skip Notion write but still return what would be written
    
    Returns:
        Dictionary with result information
    """
    config = get_config()
    
    # Parse input
    record_type = input_data.get("type", "idea")
    title = input_data.get("title", "Untitled")
    body = input_data.get("body", "")
    source_text = input_data.get("source_text", "")
    date = input_data.get("date")
    tags = input_data.get("tags", [])
    
    # Create record data for Notion
    notion_data = RecordData(
        record_type=record_type,
        title=title,
        body_markdown=body,
        date=date,
        tags=tags
    )
    
    # Write to Notion (unless dry run)
    notion_result: Optional[NotionPage] = None
    if not dry_run:
        client = NotionClient()
        notion_result = client.create_record(notion_data)
    
    # Create local record
    local_record = LocalRecord(
        type=record_type,
        title=title,
        created_at=datetime.now().isoformat(),
        notion_page_id=notion_result.page_id if notion_result else None,
        notion_url=notion_result.url if notion_result else None,
        source_text=source_text,
        final_body=body,
        tags=tags,
        date=date
    )
    
    # Save locally (always, even on dry run for testing)
    if not dry_run:
        md_path, json_path = save_local(local_record, config)
    else:
        md_path = json_path = Path("/dry-run/would-save-here")
    
    return {
        "success": True,
        "dry_run": dry_run,
        "notion_page_id": local_record.notion_page_id,
        "notion_url": local_record.notion_url,
        "local_md": str(md_path),
        "local_json": str(json_path),
        "record": asdict(local_record)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Write records to Notion and local storage"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to JSON input file"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read JSON from stdin"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written without actually writing"
    )
    
    args = parser.parse_args()
    
    # Read input
    if args.stdin:
        input_data = json.load(sys.stdin)
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        parser.error("Either --input or --stdin is required")
        return
    
    # Execute
    try:
        result = write_record(input_data, dry_run=args.dry_run)
        # Central Log
        log_manager.write_central_log(
            task_intent=f"capture_{result['record']['type']}",
            event_data={
                "record_type": result['record']['type'],
                "title": result['record']['title'],
                "notion_url": result['notion_url'],
                "local_path": result['local_md'],
                "tags": result['record']['tags']
            },
            status="SUCCESS"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
