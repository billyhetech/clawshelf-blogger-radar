#!/usr/bin/env python3
"""
blogger-radar / scripts / deliver.py
Push a pre-generated report to all enabled delivery channels.

The agent (Claude) writes the final report markdown to a temp file,
then calls this script to handle delivery. This script has NO LLM dependency.

Usage:
  python scripts/deliver.py --report /tmp/br-report.txt
  python scripts/deliver.py --report /tmp/br-report.txt --config ~/.blogger-radar/config.json
  python scripts/deliver.py --report /tmp/br-report.txt --env ~/.blogger-radar/.env
  python scripts/deliver.py --report /tmp/br-report.txt --channel slack
  python scripts/deliver.py --report /tmp/br-report.txt --dry-run
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# -- Path setup ----------------------------------------------------
ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# -- Pusher registry -----------------------------------------------
from pushers.notion_pusher import NotionPusher
from pushers.email_pusher import EmailPusher
from pushers.wechat_pusher import WeChatPusher
from pushers.slack_pusher import SlackPusher
from pushers.discord_pusher import DiscordPusher
from pushers.telegram_pusher import TelegramPusher
from pushers.feishu_pusher import FeishuPusher

PUSHER_REGISTRY = {
    "notion": NotionPusher,
    "email": EmailPusher,
    "slack": SlackPusher,
    "discord": DiscordPusher,
    "telegram": TelegramPusher,
    "feishu": FeishuPusher,
    "wechat": WeChatPusher,
}

DEFAULT_CONFIG_PATH = Path.home() / ".blogger-radar" / "config.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("deliver")


def load_env(env_path: Path | None = None) -> None:
    """Load .env file into environment variables if dotenv is available."""
    try:
        from dotenv import load_dotenv
        # Search order: explicit path → ~/.blogger-radar/.env → skill root .env
        candidates = [env_path] if env_path else [
            Path.home() / ".blogger-radar" / ".env",
            ROOT / ".env",
        ]
        for path in candidates:
            if path and path.exists():
                load_dotenv(path)
                log.debug(f"Loaded env from {path}")
                break
    except ImportError:
        pass  # python-dotenv not installed; rely on shell-exported vars


def load_config(config_path: Path) -> dict:
    """Load blogger-radar config from JSON file."""
    if not config_path.exists():
        log.error(
            f"❌ Config not found: {config_path}\n"
            "   Run blogger-radar interactively first to create your config."
        )
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def build_channel_cfg(channel_entry: dict) -> dict:
    """
    Build a pusher-compatible config dict by merging the delivery entry
    with credential values from environment variables.
    """
    channel = channel_entry.get("channel", "")
    cfg = dict(channel_entry)

    # Inject credentials from env vars based on channel type
    env_map = {
        "notion": {
            "token": "NOTION_TOKEN",
            "database_id": "NOTION_DATABASE_ID",
        },
        "email": {
            "smtp_host": "SMTP_HOST",
            "smtp_port": "SMTP_PORT",
            "smtp_user": "SMTP_USER",
            "smtp_pass": "SMTP_PASS",
        },
        "slack": {
            "webhook_url": "SLACK_WEBHOOK_URL",
        },
        "discord": {
            "webhook_url": "DISCORD_WEBHOOK_URL",
        },
        "telegram": {
            "bot_token": "TELEGRAM_BOT_TOKEN",
            "chat_id": "TELEGRAM_CHAT_ID",
        },
        "feishu": {
            "webhook_url": "FEISHU_WEBHOOK_URL",
        },
        "wechat": {
            "webhook_url": "WECHAT_WEBHOOK_URL",
        },
    }

    for cfg_key, env_var in env_map.get(channel, {}).items():
        if cfg_key not in cfg or not cfg[cfg_key]:
            value = os.environ.get(env_var)
            if value:
                cfg[cfg_key] = value

    return cfg


async def run(args) -> None:
    env_path = Path(args.env).expanduser() if args.env else None
    load_env(env_path)

    # -- Read report -----------------------------------------------
    report_path = Path(args.report)
    if not report_path.exists():
        log.error(f"❌ Report file not found: {report_path}")
        sys.exit(1)

    report_text = report_path.read_text(encoding="utf-8").strip()
    if not report_text:
        log.error(f"❌ Report file is empty: {report_path}")
        sys.exit(1)

    date_str = datetime.now().strftime("%Y-%m-%d")
    report = {
        "markdown": report_text,
        "date": date_str,
        "blogger_count": report_text.count("\n## "),  # rough count from headers
    }

    log.info(f"📄 Report loaded ({len(report_text)} chars)")

    # -- Load config -----------------------------------------------
    config_path = Path(args.config).expanduser()
    cfg = load_config(config_path)
    delivery = cfg.get("delivery", [])

    if not delivery:
        log.warning("⚠️  No delivery channels configured in config.")
        return

    # -- Filter channels -------------------------------------------
    if args.channel:
        delivery = [d for d in delivery if d.get("channel") == args.channel]
        if not delivery:
            log.error(f"❌ Channel '{args.channel}' not found in delivery config.")
            sys.exit(1)

    enabled = [d for d in delivery if d.get("enabled", False)]
    if not enabled:
        log.info("ℹ️  No enabled delivery channels. Nothing to push.")
        return

    if args.dry_run:
        channels = [d["channel"] for d in enabled]
        log.info(f"✅ Dry run. Would push to: {', '.join(channels)}")
        return

    # -- Push to each channel -------------------------------------
    log.info(f"── Pushing to {len(enabled)} channel(s) ────────────")
    results = {}

    for entry in enabled:
        channel_name = entry.get("channel", "unknown")
        pusher_cls = PUSHER_REGISTRY.get(channel_name)

        if pusher_cls is None:
            log.warning(f"  ⚠️  No pusher registered for '{channel_name}', skipping")
            results[channel_name] = "skipped"
            continue

        channel_cfg = build_channel_cfg(entry)
        log.info(f"  📤 Pushing to {channel_name}...")

        try:
            pusher = pusher_cls(channel_cfg)
            success = await pusher.push(report)
            if success:
                log.info(f"     ✓ {channel_name} success")
                results[channel_name] = "ok"
            else:
                log.error(f"     ✗ {channel_name} push returned failure")
                results[channel_name] = "failed"
        except Exception as e:
            log.error(f"     ✗ {channel_name} error: {e}")
            results[channel_name] = f"error: {e}"

    # -- Summary ---------------------------------------------------
    ok = sum(1 for v in results.values() if v == "ok")
    failed = sum(1 for v in results.values() if v not in ("ok", "skipped"))
    log.info(f"🎉 Delivery complete: {ok} succeeded, {failed} failed")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Push a generated report to configured delivery channels."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to the report markdown file (e.g. /tmp/br-report.txt)",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to config.json (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="Push to this specific channel only (overrides config)",
    )
    parser.add_argument(
        "--env",
        type=str,
        help="Path to .env credentials file (default: ~/.blogger-radar/.env then skill root .env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print which channels would receive the report without pushing",
    )
    args = parser.parse_args()
    asyncio.run(run(args))
