# 📡 Blogger Radar

> Daily AI-powered intelligence briefing on the creators you track — across Twitter/X, Xiaohongshu, YouTube, Substack, and GitHub.

**Built for [`billyhetech`](https://github.com/billyhetech)** · AI Application Architect · Build in Public

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Claude API](https://img.shields.io/badge/Powered_by-Claude_API-D97706?logo=anthropic&logoColor=white)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](#english) · [中文](#中文)

---

## English

### What it does

Blogger Radar monitors a configurable list of creators, fetches their past 7 days of content from multiple platforms, and delivers a structured daily briefing — every morning at 8:00 AM (Asia/Shanghai).

Each briefing includes:
- **Weekly highlights** — key themes and notable posts
- **New tools & products** mentioned
- **Content strategy observations**
- **💡 Opportunity angles** — content gaps you can cover (tailored for billyhetech)

### Supported platforms

| Platform | Method | Auth |
|---|---|---|
| Twitter / X | Official API v2 · Nitter RSS fallback | Bearer Token (optional) |
| Xiaohongshu | RSSHub bridge | Self-hosted RSSHub (optional) |
| YouTube | Data API v3 | API Key (optional) |
| Substack | RSS feed | None |
| GitHub | REST API v3 | Token (optional, for higher limits) |

### Push channels

| Channel | Method |
|---|---|
| **Notion** | Creates a new database page per day |
| **Email** | SMTP (Gmail / Resend / any provider) |
| **WeChat Work** | Webhook (企业微信机器人) |

### Architecture

```
run_radar.py
├── fetchers/          ← One fetcher per platform
│   ├── twitter_fetcher.py
│   ├── xiaohongshu_fetcher.py
│   ├── youtube_fetcher.py
│   ├── substack_fetcher.py
│   └── github_fetcher.py
├── summarizer.py      ← Claude API analysis
└── pushers/           ← One pusher per channel
    ├── notion_pusher.py
    ├── email_pusher.py
    └── wechat_pusher.py
```

### Quick start

**1. Configure bloggers**

```bash
cp config/bloggers.example.yaml config/bloggers.yaml
# Edit config/bloggers.yaml — add the creators you want to track
```

**2. Configure push channels & language**

```bash
cp config/push.example.yaml config/push.yaml
# Set report.language: "en" or "zh" (default: "en")
# Enable/disable Notion, Email, WeChat channels
```

**3. Set secrets (GitHub Actions)**

Go to your repo → Settings → Secrets and variables → Actions:

| Secret | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `NOTION_TOKEN` | if Notion enabled | Integration token |
| `NOTION_DATABASE_ID` | if Notion enabled | Target database ID |
| `SMTP_HOST` | if Email enabled | e.g. smtp.gmail.com |
| `SMTP_USER` | if Email enabled | Sender address |
| `SMTP_PASS` | if Email enabled | App password |
| `WECHAT_WEBHOOK_URL` | if WeChat enabled | Robot webhook URL |
| `TWITTER_BEARER_TOKEN` | optional | Official API (fallback to Nitter) |
| `YOUTUBE_API_KEY` | optional | YouTube Data API v3 |
| `GITHUB_TOKEN` | optional | Higher rate limits |
| `RSSHUB_BASE_URL` | optional | Self-hosted RSSHub for Xiaohongshu |

**4. Enable the workflow**

```bash
cp assets/github-actions-workflow.yml .github/workflows/blogger-radar.yml
git add . && git commit -m "ci: enable blogger-radar workflow" && git push
```

The workflow runs daily at UTC 00:00 (Beijing 08:00). Manually trigger anytime via Actions → Run workflow.

**5. Test locally**

```bash
pip install -r requirements.txt
cp env.example .env  # fill in your keys
export $(cat .env | xargs)

python scripts/run_radar.py --dry-run          # no push, console output
python scripts/run_radar.py --blogger swyx     # single blogger
python scripts/run_radar.py --platform github  # single platform
```

### Adding a blogger

Edit `config/bloggers.yaml` and add an entry:

```yaml
- id: your-blogger-slug
  name: "Blogger Display Name"
  tags: [AI, RAG]
  note: "Why you're tracking this person"
  platforms:
    twitter:
      handle: "@handle"
      enabled: true
    github:
      username: "handle"
      enabled: true
      watch_repos: ["repo-name"]  # empty = all repos
    substack:
      slug: "authorslug"
      enabled: true
    youtube:
      channel_id: "UCxxxxx"
      enabled: false
    xiaohongshu:
      uid: "xxxxxxxx"
      enabled: false
```

### Extending

**New platform**: Create `scripts/fetchers/newplatform_fetcher.py` implementing `async def fetch(self, days_lookback) -> list[dict]`, then register in `run_radar.py`'s `FETCHER_REGISTRY`.

**New push channel**: Create `scripts/pushers/newchannel_pusher.py` implementing `async def push(self, report) -> bool`, then register in `PUSHER_REGISTRY`.

---

## 中文

→ [查看中文文档 README.zh.md](README.zh.md)

---

## Agent compatibility

This project ships with a `SKILL.md` following the standard skill specification, making it compatible with:

- **Claude** (claude.ai Projects)
- **OpenClaw**
- **OpenCode**
- Any agent platform supporting SKILL.md

---

## License

MIT · Built with ❤️ by [billyhetech](https://github.com/billyhetech)
