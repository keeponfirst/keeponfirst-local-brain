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
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

import requests as _req

from config import get_config, PROJECT_ROOT
from notion_api import NotionClient, RecordData, NotionPage
import log_manager
import uuid as _uuid

# Optional: URL metadata extraction (optional import to avoid hard dep at import time)
try:
    from url_parser import parse_url
except ImportError:
    parse_url = None


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
    notion_sync_status: str = "SUCCESS"  # SUCCESS | PENDING | FAILED
    notion_error: Optional[str] = None
    # Optional: URL / web / social source (backward compatible)
    source_url: Optional[str] = None
    source_platform: Optional[str] = None  # twitter, reddit, medium, etc.
    og_title: Optional[str] = None
    og_image: Optional[str] = None
    og_description: Optional[str] = None
    # Supabase sync
    supabase_id: Optional[str] = None
    supabase_sync_status: str = "PENDING"  # PENDING | SUCCESS | FAILED | SKIPPED
    supabase_error: Optional[str] = None


def _is_single_url(text: str) -> bool:
    """True if text is effectively a single URL (with optional whitespace)."""
    if not text or not text.strip():
        return False
    s = text.strip()
    return s.startswith(("http://", "https://")) and " " not in s


def _extract_url_from_text(text: str) -> Optional[str]:
    """Extract first URL from text if present."""
    if not text:
        return None
    s = text.strip()
    if s.startswith(("http://", "https://")):
        end = len(s)
        for i, c in enumerate(s):
            if c in " \n\t":
                end = i
                break
        return s[:end]
    return None


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
    if getattr(record, "source_url", None):
        lines.append(f"**Source:** [{record.source_url}]({record.source_url})")
    if getattr(record, "source_platform", None):
        lines.append(f"**Platform:** {record.source_platform}")
    if getattr(record, "og_image", None):
        lines.append(f"**OG Image:** {record.og_image}")
    
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
    local_id = str(_uuid.uuid4())

    # Parse input
    record_type = input_data.get("type", "idea")
    title = input_data.get("title", "Untitled")
    body = input_data.get("body", "")
    source_text = input_data.get("source_text", "")
    date = input_data.get("date")
    tags = input_data.get("tags", [])
    source_url = input_data.get("source_url")
    source_platform = input_data.get("source_platform")
    og_title = input_data.get("og_title")
    og_image = input_data.get("og_image")
    og_description = input_data.get("og_description")

    # Optional: resolve URL metadata when source_url given or source_text is a single URL
    if parse_url and (source_url or _is_single_url(source_text)):
        url_to_parse = source_url or _extract_url_from_text(source_text)
        if url_to_parse:
            meta = parse_url(url_to_parse)
            if not meta.error:
                source_url = source_url or meta.source_url
                source_platform = source_platform or meta.source_platform
                og_title = og_title or meta.og_title
                og_image = og_image or meta.og_image
                og_description = og_description or meta.og_description
                if (not title or title == "Untitled") and meta.og_title:
                    title = meta.og_title
                if not body.strip() and meta.og_description:
                    body = meta.og_description
            # if meta.error, keep any caller-provided fields and leave rest None
    
    # Create record data for Notion
    notion_data = RecordData(
        record_type=record_type,
        title=title,
        body_markdown=body,
        date=date,
        tags=tags
    )
    
    # Write to Notion (unless dry run) - with fallback on failure
    notion_result: Optional[NotionPage] = None
    notion_error: Optional[str] = None
    notion_sync_status = "SUCCESS"
    
    if not dry_run:
        try:
            client = NotionClient()
            notion_result = client.create_record(notion_data)
        except Exception as e:
            # Notion failed - record error but continue with local write
            notion_error = str(e)
            notion_sync_status = "PENDING"
            print(f"⚠️  Notion sync failed (will write locally): {e}", file=sys.stderr)
    
    # Create local record (always, even if Notion failed)
    local_record = LocalRecord(
        type=record_type,
        title=title,
        created_at=datetime.now().isoformat(),
        notion_page_id=notion_result.page_id if notion_result else None,
        notion_url=notion_result.url if notion_result else None,
        source_text=source_text,
        final_body=body,
        tags=tags,
        date=date,
        notion_sync_status=notion_sync_status,
        notion_error=notion_error,
        source_url=source_url,
        source_platform=source_platform,
        og_title=og_title,
        og_image=og_image,
        og_description=og_description,
        supabase_id=local_id,
    )
    
    # Save locally (always, even on dry run for testing)
    if not dry_run:
        md_path, json_path = save_local(local_record, config)
        # Supabase sync (optional — skip if not configured)
        _sync_to_supabase(local_record, local_id, config)
    else:
        md_path = json_path = Path("/dry-run/would-save-here")
    
    return {
        "success": True,  # Local write succeeded
        "dry_run": dry_run,
        "notion_synced": notion_result is not None,
        "notion_pending": notion_error is not None,
        "notion_error": notion_error,
        "notion_page_id": local_record.notion_page_id,
        "notion_url": local_record.notion_url,
        "local_md": str(md_path),
        "local_json": str(json_path),
        "supabase_synced": local_record.supabase_sync_status == "SUCCESS",
        "supabase_error": local_record.supabase_error,
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
        error_code = "UNKNOWN_ERROR"
        if "NOTION_TOKEN" in str(e):
            error_code = "NOTION_AUTH_FAILED"
        elif "Invalid" in str(e):
            error_code = "INVALID_INPUT"
        print(json.dumps({
            "success": False,
            "error_code": error_code,
            "error": str(e)
        }, indent=2))
        sys.exit(1)


def _sync_to_supabase(record: LocalRecord, local_id: str, config) -> None:
    """Sync record to Supabase. Silently skips if not configured."""
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    user_id = os.environ.get("KOF_USER_ID", "").strip()

    if not url or not key or not user_id:
        record.supabase_sync_status = "SKIPPED"
        return

    try:
        resp = _req.post(
            f"{url}/rest/v1/rpc/upsert_record",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "p_id": local_id,
                "p_user_id": user_id,
                "p_local_id": local_id,
                "p_device_id": "claude_code",
                "p_record_type": record.type,
                "p_title": record.title,
                "p_source_text": record.source_text or "",
                "p_final_body": record.final_body or "",
                "p_tags": record.tags or [],
                "p_source_url": record.source_url,
                "p_source_platform": record.source_platform,
                "p_og_title": record.og_title,
                "p_og_image": record.og_image,
                "p_key_insight": None,
                "p_date": record.date,
                "p_is_deleted": False,
                "p_updated_at": record.created_at,
            },
            timeout=10,
        )
        if resp.ok:
            record.supabase_sync_status = "SUCCESS"
        else:
            record.supabase_sync_status = "FAILED"
            record.supabase_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        record.supabase_sync_status = "FAILED"
        record.supabase_error = str(e)[:200]


if __name__ == "__main__":
    main()
