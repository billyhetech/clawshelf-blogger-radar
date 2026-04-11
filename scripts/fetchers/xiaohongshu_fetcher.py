"""
fetchers/xiaohongshu_fetcher.py
Fetches Xiaohongshu content.

⚠️  Important: Xiaohongshu has no public API and aggressive bot detection.
Three strategies are available:

Strategy 1 (recommended, stable): RSSHub bridge
  - Self-host RSSHub and subscribe to a user's notes feed
  - RSSHub route: /xiaohongshu/user/{uid}
  - Requires a self-hosted or public RSSHub instance

Strategy 2 (fallback, fragile): Direct HTTP scraping
  - Easily triggers Xiaohongshu's bot detection; unreliable in production
  - Use for local dev/debugging only

Strategy 3 (most stable, manual): Manual mode
  - Set mode: manual in bloggers.yaml to skip automatic fetching
  - Pair with manual Notion entries for a reliable workflow

See references/platforms.md → Xiaohongshu for full setup instructions.
"""
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import httpx
import xml.etree.ElementTree as ET

log = logging.getLogger("radar.fetcher.xiaohongshu")


class XiaohongshuFetcher:
    def __init__(self, config: dict):
        self.uid = config.get("uid", "")
        self.mode = config.get("mode", "rsshub")  # rsshub | manual
        self.rsshub_base = os.environ.get(
            "RSSHUB_BASE_URL",
            "https://rsshub.app"   # public instance — unreliable, self-hosting recommended
        )

    async def fetch(self, days_lookback: int = 7) -> list[dict]:
        if not self.uid:
            return []

        if self.mode == "manual":
            log.info(f"  ℹ️  Xiaohongshu uid={self.uid} is set to manual mode, skipping auto-fetch")
            return []

        if self.mode == "rsshub":
            return await self._fetch_rsshub(days_lookback)

        return []

    async def _fetch_rsshub(self, days_lookback: int) -> list[dict]:
        """Fetch Xiaohongshu notes via RSSHub."""
        rss_url = f"{self.rsshub_base}/xiaohongshu/user/{self.uid}"
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_lookback)

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                headers = {"User-Agent": "blogger-radar/1.0"}
                access_key = os.environ.get("RSSHUB_ACCESS_KEY", "")
                if access_key:
                    headers["Authorization"] = f"Bearer {access_key}"

                resp = await client.get(rss_url, headers=headers)
                if resp.status_code != 200:
                    log.warning(f"  ⚠️  RSSHub returned {resp.status_code} for Xiaohongshu uid={self.uid}")
                    log.warning(f"      URL: {rss_url}")
                    log.warning("      Tip: self-host RSSHub and set RSSHUB_BASE_URL")
                    return []
                root = ET.fromstring(resp.text)
        except Exception as e:
            log.error(f"Xiaohongshu RSSHub fetch failed: {e}")
            return []

        posts = []
        for item in root.findall(".//item"):
            pub_date_str = item.findtext("pubDate", "")
            try:
                pub_date = parsedate_to_datetime(pub_date_str)
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if pub_date < cutoff:
                continue

            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = re.sub(r"<[^>]+>", "", item.findtext("description", ""))[:500]

            posts.append({
                "id": link,
                "platform": "xiaohongshu",
                "date": pub_date.strftime("%Y-%m-%d"),
                "title": title,
                "body": desc,
                "url": link,
            })

        log.info(f"  Xiaohongshu: fetched {len(posts)} notes (via RSSHub)")
        return posts
