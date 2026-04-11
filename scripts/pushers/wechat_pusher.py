"""
pushers/wechat_pusher.py
Pushes the daily briefing to a WeChat Work group bot via Webhook.
Uses WeChat Work Markdown format; auto-truncates oversized reports and appends a Notion link.
"""
import logging
import os
import httpx

log = logging.getLogger("radar.pusher.wechat")
MAX_LEN = 4096  # WeChat Work Markdown message character limit


def _trim_report(markdown: str, max_len: int, notion_url: str = "") -> str:
    """Trim report to fit within max_len, appending a Notion link if available."""
    if len(markdown) <= max_len:
        return markdown
    suffix = f"\n\n...\n> 📄 [Full report in Notion]({notion_url})" if notion_url else "\n\n...(truncated)"
    trim_at = max_len - len(suffix)
    # find the last clean paragraph break
    cut = markdown[:trim_at].rfind("\n\n")
    if cut == -1:
        cut = trim_at
    return markdown[:cut] + suffix


class WeChatPusher:
    def __init__(self, config: dict):
        self.webhook_url = os.environ.get("WECHAT_WEBHOOK_URL", config.get("webhook_url", ""))
        self.max_length = config.get("max_length", MAX_LEN)

    async def push(self, report: dict) -> bool:
        if not self.webhook_url:
            log.error("WECHAT_WEBHOOK_URL not configured")
            return False

        # attach Notion URL if available (populated after a successful Notion push)
        notion_url = report.get("metadata", {}).get("notion_url", "")
        content = _trim_report(report["markdown"], self.max_length, notion_url)

        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(self.webhook_url, json=payload)
                data = resp.json()
                if data.get("errcode") == 0:
                    log.info("  ✓ WeChat webhook push success")
                    return True
                else:
                    log.error(f"  ✗ WeChat error: {data}")
                    return False
        except Exception as e:
            log.error(f"  ✗ WeChat push exception: {e}")
            return False
