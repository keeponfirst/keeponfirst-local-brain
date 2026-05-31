#!/usr/bin/env python3
"""
Import self-improvement learnings from workspace .learnings into keeponfirst-local-brain records.

V1 scope:
- LEARNINGS.md -> worklog (or decision when decision-like)
- ERRORS.md -> backlog
- FEATURE_REQUESTS.md -> backlog
- de-dup by entry id via state file
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


ENTRY_RE = re.compile(r"^##\s*\[(?P<id>[^\]]+)\]\s*(?P<title>.*)$", re.MULTILINE)


@dataclass
class LearningEntry:
    source_file: str
    entry_id: str
    title: str
    summary: str
    suggested_action: str
    tags: list[str]
    raw: str


class Syncer:
    def __init__(self, project_root: Path, since_days: int | None = None):
        self.project_root = project_root
        self.workspace_root = project_root.parent
        self.learnings_dir = self.workspace_root / ".learnings"
        self.records_dir = project_root / "records"
        self.state_path = project_root / ".agentic" / "self_improvement_sync_state.json"
        self.state = self._load_state()
        self.since_days = since_days
        self.cutoff = datetime.now() - timedelta(days=since_days) if since_days is not None else None

    def _load_state(self) -> dict:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        return {"processed_ids": []}

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _parse_entries(self, path: Path) -> List[LearningEntry]:
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8")
        matches = list(ENTRY_RE.finditer(text))
        entries: List[LearningEntry] = []

        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[start:end].strip()

            entry_id = m.group("id").strip()
            title = m.group("title").strip() or "Untitled"

            summary = self._extract_section(block, "Summary")
            suggested_action = self._extract_section(block, "Suggested Action")
            tags_str = self._extract_metadata_value(block, "Tags")
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

            entries.append(
                LearningEntry(
                    source_file=path.name,
                    entry_id=entry_id,
                    title=title,
                    summary=summary,
                    suggested_action=suggested_action,
                    tags=tags,
                    raw=block,
                )
            )

        return entries

    @staticmethod
    def _extract_section(block: str, heading: str) -> str:
        p = re.compile(rf"###\s*{re.escape(heading)}\s*(.*?)(?=\n###\s|\Z)", re.S)
        m = p.search(block)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_metadata_value(block: str, key: str) -> str:
        p = re.compile(rf"-\s*{re.escape(key)}\s*:\s*(.+)$", re.M)
        m = p.search(block)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _slug(text: str, max_len: int = 60) -> str:
        s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text).strip("-").lower()
        return s[:max_len] if s else "entry"

    def _extract_logged_dt(self, entry: LearningEntry) -> datetime | None:
        m = re.search(r"\*\*Logged\*\*:\s*(.+)$", entry.raw, re.M)
        if not m:
            return None
        raw = m.group(1).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(raw)
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
        except Exception:
            return None

    def _within_since_window(self, entry: LearningEntry) -> bool:
        if self.cutoff is None:
            return True
        dt = self._extract_logged_dt(entry)
        if dt is None:
            # If no timestamp found, keep entry to avoid silent data loss.
            return True
        return dt >= self.cutoff

    def _target_type(self, entry: LearningEntry) -> str:
        # V1 mapping
        if entry.source_file == "ERRORS.md":
            return "backlog"
        if entry.source_file == "FEATURE_REQUESTS.md":
            return "backlog"

        # LEARNINGS.md default to worklog; promote obvious decision-like entries
        hay = f"{entry.title} {entry.summary}"
        if any(k in hay for k in ["決策", "決定", "選擇", "switch", "adopt"]):
            return "decision"
        return "worklog"

    def _write_record(self, entry: LearningEntry, dry_run: bool = False) -> dict:
        record_type = self._target_type(entry)
        subdir = {
            "decision": "decisions",
            "worklog": "worklogs",
            "backlog": "backlogs",
        }.get(record_type, "other")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{ts}_{record_type}_{self._slug(entry.title)}"
        out_dir = self.records_dir / subdir
        out_dir.mkdir(parents=True, exist_ok=True)

        body_lines = [
            f"Imported from self-improvement: `{entry.source_file}`",
            "",
            "## Summary",
            entry.summary or "(empty)",
            "",
            "## Suggested Action",
            entry.suggested_action or "(none)",
            "",
            "## Source Entry ID",
            f"- {entry.entry_id}",
        ]

        md = "\n".join([
            f"# {entry.title}",
            "",
            f"**Type:** {record_type.upper()}",
            f"**Imported At:** {datetime.now().isoformat()}",
            f"**Tags:** {', '.join(entry.tags) if entry.tags else 'self-improvement'}",
            "",
            "---",
            "",
            *body_lines,
        ])

        payload = {
            "type": record_type,
            "title": entry.title,
            "created_at": datetime.now().isoformat(),
            "source": "self-improvement",
            "source_file": entry.source_file,
            "source_entry_id": entry.entry_id,
            "tags": entry.tags,
            "summary": entry.summary,
            "suggested_action": entry.suggested_action,
        }

        md_path = out_dir / f"{base}.md"
        json_path = out_dir / f"{base}.json"

        if not dry_run:
            md_path.write_text(md, encoding="utf-8")
            json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "entry_id": entry.entry_id,
            "type": record_type,
            "md": str(md_path),
            "json": str(json_path),
        }

    def run(self, dry_run: bool = False) -> dict:
        files = ["LEARNINGS.md", "ERRORS.md", "FEATURE_REQUESTS.md"]
        imported = []
        skipped = []

        for f in files:
            for entry in self._parse_entries(self.learnings_dir / f):
                if not self._within_since_window(entry):
                    skipped.append(f"{entry.entry_id}:out_of_range")
                    continue
                if entry.entry_id in self.state["processed_ids"]:
                    skipped.append(entry.entry_id)
                    continue
                result = self._write_record(entry, dry_run=dry_run)
                imported.append(result)
                if not dry_run:
                    self.state["processed_ids"].append(entry.entry_id)

        if not dry_run:
            self._save_state()

        return {
            "success": True,
            "dry_run": dry_run,
            "workspace_learnings_dir": str(self.learnings_dir),
            "imported_count": len(imported),
            "skipped_count": len(skipped),
            "imported": imported,
            "skipped_ids": skipped,
        }


def main():
    parser = argparse.ArgumentParser(description="Import self-improvement learnings into local-brain records")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--since", type=int, default=None, help="Only import entries logged in the last N days")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    syncer = Syncer(project_root, since_days=args.since)
    result = syncer.run(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
