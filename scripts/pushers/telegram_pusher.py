#!/usr/bin/env python3
"""
blogger-radar / scripts / pushers / telegram_pusher.py
Push the daily report to a Telegram chat via Bot API.

Setup:
  1. Message @BotFather on Telegram → /newbot → follow prompts
  2. Copy the bot token (format: 123456789:ABCDefgh...)
  3. Add the bot to your target chat/channel and make it an admin
  4. Find the chat ID:
     - Personal chat: message the bot, then visit
       https://api.telegram.org/bot<TOKEN>/getUpdates and read "chat.id"
     - Group/channel: use a negative ID like -100123456789
  5. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file

Config entry in ~/.blogger-radar/config.json:
  { "channel": "telegram", "enabled": true }

Environment variables required:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""

import logging
from datetime import datetime

import httpx

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

# Telegram MarkdownV2 message limit is 4096 chars
MSG_CHAR_LIMIT = 4000


class TelegramPusher:
    def __init__(self, cfg: dict) -> None:
        self.bot_token = cfg.get("bot_token", "")
        self.chat_id = cfg.get("chat_id", "")
        self.parse_mode = cfg.get("parse_mode", "HTML")  # HTML is simpler than MarkdownV2

    async def push(self, report: dict) -> bool:
        if not self.bot_token:
            log.error("❌ TELEGRAM_BOT_TOKEN not set")
            return False
        if not self.chat_id:
            log.error("❌ TELEGRAM_CHAT_ID not set")
            return False

        markdown = report.get("markdown", "")
        date_str = report.get("date", datetime.now().strftime("%Y-%m-%d"))

        messages = self._split_report(markdown, date_str)
        url = TELEGRAM_API.format(token=self.bot_token)

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                for i, text in enumerate(messages):
                    payload = {
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": self.parse_mode,
                        "disable_web_page_preview": True,
                    }
                    resp = await client.post(url, json=payload)
                    data = resp.json()
                    if not data.get("ok"):
                        log.error(f"✗ Telegram message {i+1} failed: {data.get('description')}")
                        return False
            log.info(f"✓ Telegram push success ({len(messages)} message(s))")
            return True
        except Exception as e:
            log.error(f"✗ Telegram push error: {e}")
            return False

    def _split_report(self, markdown: str, date_str: str) -> list[str]:
        """
        Convert markdown to HTML and split into Telegram-sized chunks.
        Telegram supports a useful subset of HTML tags: <b>, <i>, <a>, <code>, <pre>.
        """
        html = self._md_to_html(markdown)

        if len(html) <= MSG_CHAR_LIMIT:
            return [html]

        # Split at double newlines to avoid breaking mid-paragraph
        parts = html.split("\n\n")
        messages = []
        current = ""
        for part in parts:
            if len(current) + len(part) + 2 > MSG_CHAR_LIMIT:
                if current:
                    messages.append(current.strip())
                current = part
            else:
                current += ("\n\n" if current else "") + part
        if current:
            messages.append(current.strip())

        return messages

    def _md_to_html(self, markdown: str) -> str:
        """Light Markdown → Telegram HTML conversion."""
        lines = []
        for line in markdown.splitlines():
            # H1/H2 → bold
            if line.startswith("## "):
                line = f"<b>{line[3:]}</b>"
            elif line.startswith("# "):
                line = f"<b>{line[2:]}</b>"
            # Bold **text**
            import re
            line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
            # Italic *text*
            line = re.sub(r"\*(.+?)\*", r"<i>\1</i>", line)
            # Links [text](url)
            line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
            # Inline code `code`
            line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
            # Blockquote >
            if line.startswith("> "):
                line = f"<i>{line[2:]}</i>"
            # Horizontal rule
            if line.strip() == "---":
                line = "──────────────────"
            lines.append(line)
        return "\n".join(lines)
