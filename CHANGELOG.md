# Changelog

## [1.2.0] - 2026-03-09

### Added
- **URL / Web Content parsing**: `scripts/url_parser.py` to fetch a URL and extract Open Graph metadata (og:title, og:description, og:image) and platform hint (twitter, reddit, medium, etc.).
- **Record schema extensions** (optional, backward compatible): `source_url`, `source_platform`, `og_title`, `og_image`, `og_description` on local records for "see article → share → auto-capture" flow.
- **Draft JSON**: optional `source_url` (and optional pre-filled `og_*`); when `source_text` is a single URL or `source_url` is provided, `write_record.py` auto-fetches metadata and enriches title/body.

### Changed
- `write_record.py` now returns structured error codes: `NOTION_AUTH_FAILED`, `INVALID_INPUT`, `UNKNOWN_ERROR`.

---

## [1.1.0] - 2026-01-21

### Added
- Bi-directional brain: `/search`, `/recall`, `/trace` commands
- Rich content rendering (code blocks, link previews)
- `PRIMARY_LANGUAGE` setting for localized record generation
- Context-aware capture with related record suggestions

### Fixed
- Central storage resolution for cross-project usage

---

## [1.0.0] - 2026-01-15

### Added
- Initial release
- Record types: Decision, Worklog, Idea, Backlog, Note
- Notion API integration (page mode)
- Local-first storage with JSON + Markdown
