"""
fetchers/youtube_fetcher.py
Fetches a YouTube channel's latest videos via YouTube Data API v3.
Requires: YOUTUBE_API_KEY env var (free quota is sufficient for daily use).
"""
import logging
import os
from datetime import datetime, timedelta, timezone
import httpx

log = logging.getLogger("radar.fetcher.youtube")
BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeFetcher:
    def __init__(self, config: dict):
        self.channel_id = config.get("channel_id", "")
        self.max_videos = config.get("max_videos", 5)
        self.api_key = os.environ.get("YOUTUBE_API_KEY", "")

    async def fetch(self, days_lookback: int = 7) -> list[dict]:
        if not self.channel_id:
            return []
        if not self.api_key:
            log.warning("YOUTUBE_API_KEY not set, skipping YouTube fetch")
            return []

        published_after = (
            datetime.now(timezone.utc) - timedelta(days=days_lookback)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{BASE}/search",
                    params={
                        "key": self.api_key,
                        "channelId": self.channel_id,
                        "part": "snippet",
                        "order": "date",
                        "publishedAfter": published_after,
                        "maxResults": self.max_videos,
                        "type": "video",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            log.error(f"YouTube API error: {e}")
            return []

        posts = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            vid_id = item.get("id", {}).get("videoId", "")
            posts.append({
                "id": vid_id,
                "platform": "youtube",
                "date": snip.get("publishedAt", "")[:10],
                "title": snip.get("title", ""),
                "body": snip.get("description", "")[:400],
                "url": f"https://youtube.com/watch?v={vid_id}",
                "thumbnail": snip.get("thumbnails", {}).get("medium", {}).get("url", ""),
            })
        return posts
