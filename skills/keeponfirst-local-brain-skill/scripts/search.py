#!/usr/bin/env python3
"""
Search Notion Brain.
Usage: 
    python search.py "query string"
    python search.py --mode trace "topic"
    python search.py --mode recall "query"
"""

import sys
import argparse
from datetime import datetime
from notion_client import Client
from config import get_config

def format_date(iso_str):
    if not iso_str: return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return iso_str

def main():
    parser = argparse.ArgumentParser(description="Search Notion Brain")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--mode", choices=["search", "trace", "recall"], default="search", help="Output mode")
    
    args = parser.parse_args()
    
    config = get_config()
    client = Client(auth=config.notion_token)
    
    print(f"[{args.mode.upper()}] Searching for: '{args.query}'...\n")
    
    try:
        response = client.search(
            query=args.query,
            sort={"direction": "descending", "timestamp": "last_edited_time"},
            page_size=20
        )
        
        results = []
        for page in response.get("results", []):
            if page["object"] != "page":
                continue
                
            title = "Untitled"
            props = page.get("properties", {})
            for key, val in props.items():
                if val["type"] == "title" and val["title"]:
                    title = val["title"][0]["text"]["content"]
                    break
            
            # Try to get Type
            record_type = "📄"
            # Note: In a real database we'd look for the specific 'Type' property
            # For page-based, we might infer from title emoji if present
            
            results.append({
                "title": title,
                "url": page["url"],
                "last_edited": page["last_edited_time"]
            })

        if not results:
            print("No results found.")
            return

        if args.mode == "trace":
            print(f"🔍 Timeline for '{args.query}':\n")
            # Sort by date ascending for trace
            results.sort(key=lambda x: x["last_edited"])
            
            for res in results:
                date_str = format_date(res['last_edited'])
                print(f"📅 {date_str} | {res['title']}")
                print(f"   🔗 {res['url']}")
                print("")
                
        elif args.mode == "recall":
            print(f"📊 Summary for '{args.query}':\n")
            print(f"Found {len(results)} related records.")
            print("## Recent Activity")
            
            for res in results[:5]: # Show top 5
                date_str = format_date(res['last_edited'])
                print(f"- {date_str}: {res['title']}")
                
        else: # Normal search
            for i, res in enumerate(results, 1):
                date_str = format_date(res['last_edited'])
                print(f"{i}. {res['title']}")
                print(f"   {date_str} | {res['url']}")
                print("")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
