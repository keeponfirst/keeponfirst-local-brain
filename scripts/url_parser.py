#!/usr/bin/env python3
"""
Keeponfirst Local Brain - URL / Web Content Parser
Fetches a URL and extracts Open Graph metadata and platform hint.
Used for "see article → share → auto-capture" flow.

Usage:
    python url_parser.py "https://example.com/article"
    echo '{"url": "https://..."}' | python url_parser.py --stdin
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Optional: use requests with a simple timeout and user-agent to avoid blocks
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; KOF-LocalBrain/1.0; +https://github.com/keeponfirst/keeponfirst-local-brain)",
}
REQUEST_TIMEOUT = 15

# Map hostnames to source_platform (optional, for social / known sites)
PLATFORM_DOMAINS = {
    "twitter.com": "twitter",
    "x.com": "twitter",
    "reddit.com": "reddit",
    "threads.net": "threads",
    "facebook.com": "facebook",
    "www.facebook.com": "facebook",
    "medium.com": "medium",
    "github.com": "github",
    "youtube.com": "youtube",
    "www.youtube.com": "youtube",
}


@dataclass
class URLMetadata:
    """Structured metadata extracted from a URL."""
    source_url: str
    source_platform: Optional[str] = None  # twitter, reddit, medium, etc.
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    page_title: Optional[str] = None  # <title> fallback
    error: Optional[str] = None  # if fetch/parse failed


def _platform_from_url(url: str) -> Optional[str]:
    """Infer platform from URL host."""
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower().lstrip("www.")
        if not host:
            return None
        # exact match
        if host in PLATFORM_DOMAINS:
            return PLATFORM_DOMAINS[host]
        # subdomain match (e.g. subdomain.reddit.com)
        for domain, platform in PLATFORM_DOMAINS.items():
            if host == domain or host.endswith("." + domain):
                return platform
        return None
    except Exception:
        return None


def _og_content(soup: BeautifulSoup, prop: str) -> Optional[str]:
    """Get content of meta property (og:title, og:description, og:image)."""
    tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": re.compile(prop, re.I)})
    if not tag or not tag.get("content"):
        return None
    return (tag.get("content") or "").strip() or None


def parse_url(url: str) -> URLMetadata:
    """
    Fetch URL and extract OG metadata + platform.
    Returns URLMetadata; error field set on failure.
    """
    if not url or not url.startswith(("http://", "https://")):
        return URLMetadata(source_url=url, error="Invalid or missing URL")
    source_url = url.rstrip("/")
    platform = _platform_from_url(source_url)

    try:
        resp = requests.get(
            source_url,
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        og_title = _og_content(soup, "og:title")
        og_description = _og_content(soup, "og:description")
        og_image = _og_content(soup, "og:image")
        page_title = None
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            page_title = title_tag.string.strip() or None

        return URLMetadata(
            source_url=source_url,
            source_platform=platform,
            og_title=og_title or page_title,
            og_description=og_description,
            og_image=og_image,
            page_title=page_title,
        )
    except requests.RequestException as e:
        return URLMetadata(source_url=source_url, source_platform=platform, error=str(e))
    except Exception as e:
        return URLMetadata(source_url=source_url, source_platform=platform, error=str(e))


def main():
    parser = argparse.ArgumentParser(description="Parse URL and extract OG metadata")
    parser.add_argument("url", nargs="?", help="URL to parse")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin: {\"url\": \"...\"}")
    args = parser.parse_args()

    if args.stdin:
        data = json.load(sys.stdin)
        url = data.get("url", "")
    elif args.url:
        url = args.url
    else:
        parser.error("Provide url as argument or use --stdin")
        return

    result = parse_url(url)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    if result.error:
        sys.exit(1)


if __name__ == "__main__":
    main()
