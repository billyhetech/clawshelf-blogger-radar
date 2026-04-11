#!/usr/bin/env python3
"""
blogger-radar / scripts / fetch_all.py
Fetch recent posts for all configured bloggers and write raw JSON to disk.

The agent (Claude) reads that JSON file, applies prompts/summarize-blogger.md
and prompts/report-format.md to produce the final report, then calls deliver.py.
This script has NO LLM dependency.

Usage:
  python scripts/fetch_all.py
  python scripts/fetch_all.py --config ~/.blogger-radar/config.json
  python scripts/fetch_all.py --output /tmp/br-fetch-result.json
  python scripts/fetch_all.py --blogger swyx
  python scripts/fetch_all.py --platform github
  python scripts/fetch_all.py --dry-run   # print JSON to stdout, skip file write
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# -- Path setup ----------------------------------------------------
ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# -- Fetcher registry ----------------------------------------------
from fetchers.twitter_fetcher import TwitterFetcher
from fetchers.xiaohongshu_fetcher import XiaohongshuFetcher
from fetchers.youtube_fetcher import YouTubeFetcher
from fetchers.substack_fetcher import SubstackFetcher
from fetchers.github_fetcher import GitHubFetcher

FETCHER_REGISTRY = {
    "twitter": TwitterFetcher,
    "xiaohongshu": XiaohongshuFetcher,
    "youtube": YouTubeFetcher,
    "substack": SubstackFetcher,
    "github": GitHubFetcher,
}

DEFAULT_CONFIG_PATH = Path.home() / ".blogger-radar" / "config.json"
DEFAULT_OUTPUT_PATH = Path("/tmp/br-fetch-result.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("fetch_all")


def load_config(config_path: Path) -> dict:
    """Load blogger-radar config from JSON file."""
    if not config_path.exists():
        log.error(
            f"❌ Config not found: {config_path}\n"
            "   Run blogger-radar interactively first to create your config."
        )
        sys.exit(1)

    with open(config_path) as f:
        cfg = json.load(f)

    if not cfg.get("setupComplete"):
        log.error("❌ Setup not complete. Run blogger-radar interactively to finish setup.")
        sys.exit(1)

    return cfg


def build_fetch_params(cfg: dict) -> dict:
    """Extract fetch parameters from config with sensible defaults."""
    report_cfg = cfg.get("report", {})
    return {
        "days_lookback": report_cfg.get("daysLookback", 7),
        "max_posts_per_blogger": report_cfg.get("maxPostsPerBlogger", 10),
    }


async def fetch_blogger(
    blogger: dict,
    fetch_params: dict,
    platform_filter: str | None,
) -> dict:
    """Fetch all enabled platform content for one blogger."""
    days = fetch_params["days_lookback"]
    max_posts = fetch_params["max_posts_per_blogger"]
    posts_by_platform = {}
    platforms = blogger.get("platforms", {})

    for platform_name, platform_handle in platforms.items():
        if platform_filter and platform_name != platform_filter:
            continue
        if platform_name not in FETCHER_REGISTRY:
            log.warning(f"  ⚠️  Unknown platform '{platform_name}', skipping")
            continue

        # Build a minimal platform config dict (handle + any extra settings)
        if isinstance(platform_handle, str):
            platform_cfg = {"handle": platform_handle, "enabled": True}
        elif isinstance(platform_handle, dict):
            platform_cfg = {**platform_handle, "enabled": True}
        else:
            continue

        log.info(f"  📥 {blogger['name']} / {platform_name}...")
        try:
            fetcher = FETCHER_REGISTRY[platform_name](platform_cfg)
            posts = await fetcher.fetch(days_lookback=days)
            posts_by_platform[platform_name] = posts[:max_posts]
            log.info(f"     ✓ {len(posts_by_platform[platform_name])} post(s)")
        except Exception as e:
            log.error(f"     ✗ {platform_name} fetch failed: {e}")
            posts_by_platform[platform_name] = []

    return {
        "blogger": {
            "id": blogger.get("id", blogger.get("name", "unknown")),
            "name": blogger.get("name", blogger.get("id", "unknown")),
            "tags": blogger.get("tags", []),
            "note": blogger.get("note", ""),
        },
        "posts_by_platform": posts_by_platform,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


async def run(args) -> None:
    config_path = Path(args.config).expanduser()
    cfg = load_config(config_path)
    fetch_params = build_fetch_params(cfg)

    bloggers = cfg.get("bloggers", [])
    if not bloggers:
        log.error("❌ No bloggers configured. Add bloggers via blogger-radar setup.")
        sys.exit(1)

    if args.blogger:
        bloggers = [b for b in bloggers if b.get("id") == args.blogger or b.get("name") == args.blogger]
        if not bloggers:
            log.error(f"❌ Blogger '{args.blogger}' not found in config.")
            sys.exit(1)

    log.info(f"🚀 Fetching {len(bloggers)} blogger(s)...")

    tasks = [fetch_blogger(b, fetch_params, args.platform) for b in bloggers]
    results = await asyncio.gather(*tasks)

    # Filter out bloggers with zero posts
    non_empty = [r for r in results if any(r["posts_by_platform"].values())]
    if not non_empty:
        log.warning("⚠️  No posts found for any blogger. Check fetcher logs above.")

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "blogger_count": len(non_empty),
        "language": cfg.get("language", "en"),
        "results": non_empty,
    }

    if args.dry_run:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        log.info("✅ Dry run complete. Output printed to stdout.")
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    log.info(f"✅ Fetch complete. Output written to {output_path}")
    log.info(f"   {len(non_empty)} blogger(s) with data ready for agent summarization.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch recent posts for all configured bloggers."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to config.json (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Path for output JSON (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--blogger",
        type=str,
        help="Only fetch for this blogger ID",
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=list(FETCHER_REGISTRY.keys()),
        help="Only fetch from this platform",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON to stdout instead of writing to file",
    )
    args = parser.parse_args()
    asyncio.run(run(args))
