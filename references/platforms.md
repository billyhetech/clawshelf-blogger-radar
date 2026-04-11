# references/platforms.md
# Platform Fetch Strategies

## Table of Contents
1. [Twitter/X](#twitterx)
2. [Xiaohongshu](#xiaohongshu)
3. [YouTube](#youtube)
4. [Substack](#substack)
5. [GitHub](#github)

---

## Twitter/X

**Reliability**: ⭐⭐⭐⭐ (with Bearer Token) / ⭐⭐ (Nitter fallback)

### Official API v2 (recommended)
- Free tier: 500,000 tweet reads per month
- Get your token: https://developer.twitter.com → Create App → Copy Bearer Token
- Configure via: `TWITTER_BEARER_TOKEN` env var
- Fetches original tweets only (retweets and replies excluded)

### Nitter fallback (no token)
- Uses public Nitter instance RSS feeds — no authentication required
- Risk: Nitter instances can shut down without notice
- Multiple instances are polled in rotation as a safeguard

---

## Xiaohongshu

**Reliability**: ⭐⭐ (RSSHub) / ⭐ (direct scrape)

> ⚠️ Xiaohongshu has no official API and is the most fragile part of the system.

### Strategy 1: Self-hosted RSSHub (recommended)

RSSHub is an open-source RSS generator with Xiaohongshu support.

**Deploy RSSHub (free options):**
```bash
# Option A: Vercel one-click
# Fork https://github.com/DIYgod/RSSHub → deploy to Vercel

# Option B: Railway
railway up  # uses the official Docker image

# Option C: Local dev/test
docker run -d -p 1200:1200 diygod/rsshub
```

**Xiaohongshu route:**
- User notes: `/xiaohongshu/user/{uid}`
- Find the UID: open the user's profile page on the Xiaohongshu web app → extract the numeric string from the URL

**Environment variables:**
```
RSSHUB_BASE_URL=https://your-rsshub.vercel.app
RSSHUB_ACCESS_KEY=your_access_key  # optional, for private instances
```

### Strategy 2: Manual mode
Set `mode: manual` in `config/bloggers.yaml` to skip automatic fetching for a blogger.
Useful as a fallback — pair with manual Notion entries or periodic manual updates.

---

## YouTube

**Reliability**: ⭐⭐⭐⭐⭐ (official API, most stable)

### YouTube Data API v3
- Free quota: 10,000 units/day (each search costs ~100 units)
- Get an API key: https://console.cloud.google.com → Enable YouTube Data API v3
- Configure via: `YOUTUBE_API_KEY` env var

### How to find a Channel ID
- **Method 1:** Channel page → right-click → View Page Source → search `channelId`
- **Method 2:** `https://www.youtube.com/@handle/about` → inspect URL parameters
- **Method 3:** Use https://ytlarge.com/youtube/channel-id-finder/

---

## Substack

**Reliability**: ⭐⭐⭐⭐⭐ (RSS, no auth needed)

### RSS Feed
- URL format: `https://{slug}.substack.com/feed`
- `slug` = the author's Substack subdomain prefix
- No authentication required — standard RSS/Atom format
- Returns article title, excerpt, and publish date

---

## GitHub

**Reliability**: ⭐⭐⭐⭐⭐ (official API)

### GitHub REST API v3
- Unauthenticated: 60 requests/hour (sufficient for small-scale use)
- Authenticated: 5,000 requests/hour
- Configure via: `GITHUB_TOKEN` env var (read-only Personal Access Token is enough)

### What is monitored
- `PushEvent` — commits (includes commit messages)
- `CreateEvent` (tag) — new releases
- `IssuesEvent` — issue activity
- Use `watch_repos` in `config/bloggers.yaml` to monitor only specific repositories
