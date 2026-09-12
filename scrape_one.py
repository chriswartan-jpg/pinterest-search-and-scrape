#!/usr/bin/env python3
"""Single-shot Pinterest scrape for programmatic/subprocess use.

Wraps pinterest_browser_scraper.pinterest_search_scraper() with a stable
CLI contract (args in, manifest.json out) for callers that invoke this as
a subprocess, rather than the batch/search_terms.txt workflow in run.py.
"""
import argparse
import json
import os
import sys

from pinterest_browser_scraper import pinterest_search_scraper


def main():
    parser = argparse.ArgumentParser(description="Scrape Pinterest for one search term and write a manifest.json")
    parser.add_argument("--query", required=True, help="Search term")
    parser.add_argument("--count", type=int, default=50, help="Number of images to download")
    parser.add_argument("--out", required=True, help="Output directory for images and manifest.json")
    parser.add_argument("--scrolls", type=int, default=10, help="Number of scroll passes")
    parser.add_argument("--workers", type=int, default=5, help="Parallel download workers")
    parser.add_argument("--no-headless", action="store_true", help="Show the browser window instead of running headless")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    result = pinterest_search_scraper(
        args.query,
        output_folder=args.out,
        max_images=args.count,
        num_scrolls=args.scrolls,
        workers=args.workers,
        headless=not args.no_headless,
    )

    files = sorted(
        f for f in os.listdir(args.out)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
    )
    manifest = {
        "query": args.query,
        "requested": args.count,
        "downloaded": len(files),
        "files": files,
        "success": bool(result.get("success")),
        "error": result.get("error"),
    }
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    if not manifest["success"] or not files:
        print(f"Scrape failed or returned no images: {manifest.get('error', 'no images downloaded')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
