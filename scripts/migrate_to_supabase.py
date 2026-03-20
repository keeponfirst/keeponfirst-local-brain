#!/usr/bin/env python3
"""
Phase 6 — Migrate local records to Supabase.

Reads all JSON records from the local brain directory and upserts them
to Supabase. Safe to run multiple times (idempotent via upsert_record RPC).

Usage:
    python scripts/migrate_to_supabase.py [--dry-run] [--limit N]

Required env vars (or .env file):
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
    KOF_USER_ID
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RECORDS_ROOT = PROJECT_ROOT / "records"

RECORD_TYPE_DIRS = {
    "decision": "decisions",
    "worklog": "worklogs",
    "idea": "ideas",
    "backlog": "backlogs",
    "note": "other",
}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    load_dotenv(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description="Migrate local records to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Print records without uploading")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of records (0 = all)")
    args = parser.parse_args()

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    user_id = os.environ.get("KOF_USER_ID", "").strip()

    if not url or not key or not user_id:
        print("❌ 需要設定環境變數：SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, KOF_USER_ID")
        print("   請複製 .env.example 為 .env 並填入實際值")
        sys.exit(1)

    records = load_all_records()
    total = len(records)

    if args.limit > 0:
        records = records[: args.limit]

    print(f"🔍 找到 {total} 筆本地記錄，準備遷移 {len(records)} 筆")

    if args.dry_run:
        print("🔵 DRY RUN — 不實際上傳")
        for r in records:
            print(f"  - [{r['record_type']}] {r['title']} ({r.get('created_at', '')[:10]})")
        return

    pushed = 0
    skipped = 0
    failed = 0

    for i, record in enumerate(records, 1):
        try:
            result = upsert_record(url, key, user_id, record)
            if result:
                pushed += 1
                print(f"  ✅ [{i}/{len(records)}] {record['title'][:50]}")
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            print(f"  ❌ [{i}/{len(records)}] {record['title'][:50]}: {e}")

    print(f"\n{'='*50}")
    print(f"✅ 成功: {pushed}  ⏭️ 略過: {skipped}  ❌ 失敗: {failed}")
    print(f"Migration 完成！")


def load_all_records() -> list[dict]:
    """Load all JSON records from the local brain directory."""
    records = []

    for record_type, folder in RECORD_TYPE_DIRS.items():
        dir_path = RECORDS_ROOT / folder
        if not dir_path.exists():
            continue

        for json_file in sorted(dir_path.glob("*.json")):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Normalize record type
                if "record_type" not in data:
                    data["record_type"] = record_type
                if "id" not in data:
                    data["id"] = json_file.stem

                records.append(data)
            except Exception as e:
                print(f"  ⚠️  跳過 {json_file.name}: {e}")

    # Sort by created_at ascending (oldest first)
    records.sort(key=lambda r: r.get("created_at", ""))
    return records


def upsert_record(url: str, key: str, user_id: str, record: dict) -> bool:
    """Push one record to Supabase via upsert_record RPC."""
    tags = record.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    created_at = record.get("created_at", datetime.utcnow().isoformat() + "Z")
    local_id = record.get("id", "")
    content = record.get("content") or record.get("body") or record.get("final_body") or ""
    source_url = record.get("source_url") or record.get("url")

    payload = {
        "p_id": local_id,
        "p_user_id": user_id,
        "p_local_id": local_id,
        "p_device_id": "migration",
        "p_record_type": record.get("record_type", "note"),
        "p_title": record.get("title", "Untitled"),
        "p_source_text": content,
        "p_final_body": content,
        "p_tags": tags,
        "p_source_url": source_url,
        "p_source_platform": "claude_code",
        "p_og_title": None,
        "p_og_image": None,
        "p_key_insight": record.get("key_insight"),
        "p_date": created_at[:10] if created_at else None,
        "p_is_deleted": False,
        "p_updated_at": created_at,
    }

    resp = requests.post(
        f"{url}/rest/v1/rpc/upsert_record",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )

    if resp.status_code in (200, 201, 204):
        return True
    elif resp.status_code == 409:
        return False  # Already exists (conflict = skipped)
    else:
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")


if __name__ == "__main__":
    main()
