"""
pushers/notion_pusher.py
Pushes the daily briefing to a Notion database.
Each run creates a new Page with the report content converted to Notion Blocks.
"""
import logging
import os
import re
from datetime import datetime
import httpx

log = logging.getLogger("radar.pusher.notion")
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _md_to_notion_blocks(markdown: str) -> list[dict]:
    """Convert Markdown to Notion Blocks (supports h1/h2/h3, bullets, paragraphs, dividers)."""
    blocks = []
    for line in markdown.split("\n"):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if line_stripped.startswith("### "):
            blocks.append(_heading(line_stripped[4:], 3))
        elif line_stripped.startswith("## "):
            blocks.append(_heading(line_stripped[3:], 2))
        elif line_stripped.startswith("# "):
            blocks.append(_heading(line_stripped[2:], 1))
        elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
            blocks.append(_bullet(line_stripped[2:]))
        elif line_stripped.startswith("---"):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        else:
            blocks.append(_paragraph(line_stripped))

    # Notion API limit: 100 blocks per request (truncate for simplicity)
    return blocks[:100]


def _heading(text: str, level: int) -> dict:
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text[:2000]}}]
        },
    }


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


class NotionPusher:
    def __init__(self, config: dict):
        self.database_id = _resolve_env(config.get("database_id", ""))
        self.token = os.environ.get("NOTION_TOKEN", "")
        self.icon = config.get("page_icon", "📡")
        self.props = config.get("properties", {})

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    async def push(self, report: dict) -> bool:
        if not self.token or not self.database_id:
            log.error("NOTION_TOKEN or NOTION_DATABASE_ID not configured")
            return False

        date_str = report["date"]
        title = f"📡 Blogger Radar {date_str}"
        blocks = _md_to_notion_blocks(report["markdown"])

        page_data = {
            "parent": {"database_id": self.database_id},
            "icon": {"type": "emoji", "emoji": self.icon},
            "properties": {
                self.props.get("title_field", "Name"): {
                    "title": [{"text": {"content": title}}]
                },
                **({self.props.get("date_field", "Date"): {"date": {"start": date_str}}}
                   if self.props.get("date_field") else {}),
            },
            "children": blocks,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{NOTION_API}/pages", headers=self._headers, json=page_data
                )
                if resp.status_code in (200, 201):
                    page_url = resp.json().get("url", "")
                    log.info(f"  ✓ Notion page created: {page_url}")
                    return True
                else:
                    log.error(f"  ✗ Notion API error {resp.status_code}: {resp.text[:300]}")
                    return False
        except Exception as e:
            log.error(f"  ✗ Notion push exception: {e}")
            return False


def _resolve_env(value: str) -> str:
    """Resolve ${ENV_VAR} style references to their environment variable values."""
    match = re.match(r"^\$\{(.+)\}$", value)
    if match:
        return os.environ.get(match.group(1), "")
    return value
