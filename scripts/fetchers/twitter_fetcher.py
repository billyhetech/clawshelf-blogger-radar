"""
fetchers/twitter_fetcher.py
Fetches Twitter/X content.
Strategy 1 (recommended): Official API v2 with Bearer Token (500k tweet reads/month free).
Strategy 2 (fallback): Nitter public instance RSS (unstable, instances may disappear).
"""
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import httpx
import xml.etree.ElementTree as ET

log = logging.getLogger("radar.fetcher.twitter")

# Public Nitter instances, polled in priority order
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]


class TwitterFetcher:
    def __init__(self, config: dict):
        self.handle = config.get("handle", "").lstrip("@")
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")

    async def fetch(self, days_lookback: int = 7) -> list[dict]:
        if not self.handle:
            return []
        if self.bearer_token:
            return await self._fetch_official(days_lookback)
        else:
            log.info(f"  ℹ️  No TWITTER_BEARER_TOKEN, using nitter RSS fallback for @{self.handle}")
            return await self._fetch_nitter(days_lookback)

    # ── Official API v2 ──────────────────────────────────
    async def _fetch_official(self, days_lookback: int) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_lookback)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # 1. resolve user ID
                user_resp = await client.get(
                    f"https://api.twitter.com/2/users/by/username/{self.handle}",
                    headers={"Authorization": f"Bearer {self.bearer_token}"},
                )
                user_resp.raise_for_status()
                user_id = user_resp.json()["data"]["id"]

                # 2. fetch recent tweets
                tweet_resp = await client.get(
                    f"https://api.twitter.com/2/users/{user_id}/tweets",
                    headers={"Authorization": f"Bearer {self.bearer_token}"},
                    params={
                        "start_time": cutoff,
                        "max_results": 20,
                        "tweet.fields": "created_at,public_metrics,entities",
                        "exclude": "retweets,replies",  # original tweets only
                    },
                )
                tweet_resp.raise_for_status()
                tweets = tweet_resp.json().get("data", [])
        except Exception as e:
            log.error(f"Twitter API error for @{self.handle}: {e}")
            return []

        posts = []
        for t in tweets:
            posts.append({
                "id": t["id"],
                "platform": "twitter",
                "date": t.get("created_at", "")[:10],
                "title": t["text"][:80] + "..." if len(t["text"]) > 80 else t["text"],
                "body": t["text"],
                "url": f"https://twitter.com/{self.handle}/status/{t['id']}",
                "metrics": t.get("public_metrics", {}),
            })
        return posts

    # ── Nitter RSS Fallback ──────────────────────────────
    async def _fetch_nitter(self, days_lookback: int) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_lookback)
        for instance in NITTER_INSTANCES:
            rss_url = f"{instance}/{self.handle}/rss"
            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    resp = await client.get(rss_url, headers={"User-Agent": "blogger-radar/1.0"})
                    if resp.status_code != 200:
                        continue
                    root = ET.fromstring(resp.text)
                    break
            except Exception:
                continue
        else:
            log.error(f"All nitter instances failed for @{self.handle}")
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

            raw = item.findtext("title", "") or item.findtext("description", "")
            body = re.sub(r"<[^>]+>", "", raw).strip()
            link = item.findtext("link", "")

            posts.append({
                "id": link,
                "platform": "twitter",
                "date": pub_date.strftime("%Y-%m-%d"),
                "title": body[:80],
                "body": body,
                "url": link.replace(instance, "https://twitter.com"),
            })
        return posts
