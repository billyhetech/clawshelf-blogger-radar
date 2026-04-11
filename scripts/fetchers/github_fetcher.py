"""
fetchers/github_fetcher.py
Fetches a GitHub user's recent public activity (commits, releases, issues).
Most reliable platform — full official REST API.
"""
import logging
import os
from datetime import datetime, timedelta, timezone
import httpx

log = logging.getLogger("radar.fetcher.github")
BASE = "https://api.github.com"


class GitHubFetcher:
    def __init__(self, config: dict):
        self.username = config.get("username", "")
        self.watch_repos = config.get("watch_repos", [])  # empty list = watch all repos
        self.token = os.environ.get("GITHUB_TOKEN", "")

    @property
    def _headers(self):
        h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def fetch(self, days_lookback: int = 7) -> list[dict]:
        if not self.username:
            return []
        since = (datetime.now(timezone.utc) - timedelta(days=days_lookback)).isoformat()
        posts = []
        async with httpx.AsyncClient(headers=self._headers, timeout=30) as client:
            # public events stream
            url = f"{BASE}/users/{self.username}/events/public"
            try:
                resp = await client.get(url, params={"per_page": 50})
                resp.raise_for_status()
                events = resp.json()
            except Exception as e:
                log.error(f"GitHub events fetch failed: {e}")
                return []

            for event in events:
                created = event.get("created_at", "")
                if created < since:
                    continue
                repo_name = event.get("repo", {}).get("name", "")
                # apply watch_repos filter if configured
                if self.watch_repos:
                    short_name = repo_name.split("/")[-1]
                    if short_name not in self.watch_repos:
                        continue

                etype = event.get("type", "")
                payload = event.get("payload", {})
                post = self._parse_event(etype, payload, repo_name, created)
                if post:
                    posts.append(post)

        return posts

    def _parse_event(self, etype, payload, repo, date) -> dict | None:
        repo_url = f"https://github.com/{repo}"
        if etype == "PushEvent":
            commits = payload.get("commits", [])
            messages = [c["message"].split("\n")[0] for c in commits[:3]]
            return {
                "id": f"gh-push-{date}",
                "platform": "github",
                "date": date[:10],
                "title": f"Push to {repo}",
                "body": " | ".join(messages),
                "url": repo_url,
            }
        elif etype == "CreateEvent" and payload.get("ref_type") == "tag":
            return {
                "id": f"gh-release-{date}",
                "platform": "github",
                "date": date[:10],
                "title": f"New release: {repo} @ {payload.get('ref','')}",
                "body": f"Released tag {payload.get('ref','')} on {repo}",
                "url": f"{repo_url}/releases",
            }
        elif etype == "IssuesEvent":
            issue = payload.get("issue", {})
            return {
                "id": f"gh-issue-{date}",
                "platform": "github",
                "date": date[:10],
                "title": f"Issue: {issue.get('title', '')}",
                "body": (issue.get("body") or "")[:300],
                "url": issue.get("html_url", repo_url),
            }
        return None
