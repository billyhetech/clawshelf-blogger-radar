"""
fetchers/substack_fetcher.py
Fetches Substack articles via RSS feed. No API key required — most reliable source.
RSS URL format: https://{slug}.substack.com/feed
"""
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import httpx
import xml.etree.ElementTree as ET

log = logging.getLogger("radar.fetcher.substack")


class SubstackFetcher:
    def __init__(self, config: dict):
        self.slug = config.get("slug", "")

    async def fetch(self, days_lookback: int = 7) -> list[dict]:
        if not self.slug:
            return []
        rss_url = f"https://{self.slug}.substack.com/feed"
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_lookback)

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(rss_url, headers={"User-Agent": "blogger-radar/1.0"})
                resp.raise_for_status()
                root = ET.fromstring(resp.text)
        except Exception as e:
            log.error(f"Substack RSS fetch failed for {self.slug}: {e}")
            return []

        posts = []
        ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
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
            desc = item.findtext("description", "")
            # strip HTML tags
            import re
            body = re.sub(r"<[^>]+>", "", desc or "")[:500]

            posts.append({
                "id": link,
                "platform": "substack",
                "date": pub_date.strftime("%Y-%m-%d"),
                "title": title,
                "body": body,
                "url": link,
            })

        return posts
