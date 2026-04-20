# 📡 Blogger Radar

> Daily AI-powered intelligence briefing on the creators you track — across Twitter/X, YouTube, Substack, and GitHub.
> **Zero Python, zero installs needed for basic use.**

**Built for [`billyhetech`](https://github.com/billyhetech)** · AI Application Architect · Build in Public

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill_v3-8B5CF6?logo=anthropic&logoColor=white)](https://github.com/topics/openclaw-skill)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](#english) · [中文](README.zh.md)

---

## English

### What it does

Blogger Radar monitors a configurable list of creators, fetches their recent content from multiple platforms, and delivers a structured daily intelligence briefing — in-conversation by default, or pushed to Slack, Discord, Telegram, Feishu, WeChat, Notion, or Email.

The agent handles all fetching and summarization natively. No Python installation, no API keys required to get started.

Each briefing includes:
- **Highlights** — specific notable posts and actions with links
- **New tools & products** mentioned or launched
- **Content strategy observations** — format, tone, cadence patterns
- **Engagement signals** — what's resonating with their audience
- **Trend direction** — rising / stable / declining
- **Content opportunities** — actionable angles you can cover

### Supported platforms

| Platform | Method | Auth required? |
|---|---|---|
| GitHub | Public Events API v3 | No (optional token raises limit 60→5000/hr) |
| Substack | RSS feed | No |
| YouTube | Free Atom feed (no quota) | No |
| Twitter / X | `/x-search` skill · Nitter RSS fallback · Official API v2 | No (optional for better quality) |
| Xiaohongshu | RSSHub bridge | Self-hosted RSSHub only — *Chinese creators* |

### Delivery channels

| Channel | Method |
|---|---|
| **In-conversation** | Default — zero configuration, works immediately |
| **Slack** | Incoming Webhook |
| **Discord** | Webhook |
| **Telegram** | Bot API |
| **Feishu / Lark** | Webhook |
| **WeChat Work** | Webhook (企业微信机器人) |
| **Notion** | Database page per day *(requires Python)* |
| **Email** | SMTP *(requires Python)* |

### Built-in Top 30 list

Blogger Radar ships with a curated list of 30 AI builders across six categories, ready to load on first run:

| Category | Creators |
|---|---|
| General Alpha | Karpathy, Sam Altman, Yann LeCun, Geoffrey Hinton, John Carmack |
| Technical Builders | swyx, Simon Willison, Jason Liu, Jerry Liu, Harrison Chase, Jeremy Howard, David Ha, Shreya Shankar |
| AI × Business | Aaron Levie, Dan Shipper, Ethan Mollick, Peter Yang, Kevin Weil |
| Content / Media | Matt Wolfe, Matthew Berman, Greg Isenberg, Riley Goodside |
| Indie Hackers | steipete, Marc Lou, Meng To, Amjad Massad, Pieter Levels |
| Product Leaders | Guillermo Rauch, Garry Tan, Matt Shumer |

### Quick start (agent / OpenClaw)

The recommended way to use Blogger Radar is through the Claude Code skill:

```
/blogger-radar
```

The agent walks you through setup in under 2 minutes:
1. Choose to use the built-in Top 30 list (one click) or add your own creators
2. Pick your preferred language (English / Chinese / Bilingual)
3. Set delivery: in-conversation is the default, external channels are optional
4. Run your first report immediately

No Python, no YAML editing, no secrets to configure for basic use.

### Local archive

Every report is automatically saved to:
```
~/.blogger-radar/reports/YYYY/MM/YYYY-MM-DD.md
```

Raw fetch data is cached for reprocessing:
```
~/.blogger-radar/cache/YYYY-MM-DD.json
```

Look up past reports conversationally:
- "Show last Tuesday's report"
- "Show April reports"
- "Reprocess April 15th data in Chinese"

### Architecture

```
SKILL.md                       ← self-contained skill spec (all runtime instructions)
~/.blogger-radar/
├── config.json                ← settings and blogger list (created by agent)
├── .env                       ← credentials (optional)
├── reports/YYYY/MM/*.md       ← daily archived reports
└── cache/YYYY-MM-DD.json      ← raw fetch data

scripts/                       ← legacy Python scripts (optional)
├── fetch_all.py               ← for GitHub Actions / non-agent deployments
└── deliver.py                 ← for Notion / Email channels
```

### Manual setup (GitHub Actions / headless)

For deployments without a Claude agent present (e.g. GitHub Actions):

**1. Configure bloggers**

```bash
cp config/bloggers.example.yaml config/bloggers.yaml
# Edit config/bloggers.yaml — add the creators you want to track
```

**2. Configure push channels**

```bash
cp config/push.example.yaml config/push.yaml
# Set report.language: "en" or "zh" (default: "en")
# Enable desired channels
```

**3. Set GitHub Secrets**

Go to your repo → Settings → Secrets and variables → Actions:

| Secret | Required | Description |
|---|---|---|
| `NOTION_TOKEN` | if Notion enabled | Integration token |
| `NOTION_DATABASE_ID` | if Notion enabled | Target database ID |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | if Email enabled | SMTP credentials |
| `WECHAT_WEBHOOK_URL` | if WeChat enabled | Robot webhook URL |
| `SLACK_WEBHOOK_URL` | if Slack enabled | Incoming webhook URL |
| `DISCORD_WEBHOOK_URL` | if Discord enabled | Channel webhook URL |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | if Telegram enabled | Bot credentials |
| `TWITTER_BEARER_TOKEN` | optional | Official API (fallback: Nitter RSS) |
| `GITHUB_TOKEN` | optional | Higher rate limits |
| `RSSHUB_BASE_URL` | optional | Self-hosted RSSHub for Xiaohongshu |

> No `ANTHROPIC_API_KEY` needed in agent mode — the agent (Claude) handles all summarization.

**4. Enable the workflow**

```bash
cp assets/github-actions-workflow.yml .github/workflows/blogger-radar.yml
git add . && git commit -m "ci: enable blogger-radar workflow" && git push
```

The workflow runs daily at UTC 00:00 (Beijing 08:00). Manually trigger anytime via Actions → Run workflow.

**5. Test locally**

```bash
pip install -r requirements.txt
cp env.example .env && vim .env  # fill in your keys

python scripts/fetch_all.py --dry-run          # see fetched JSON
python scripts/fetch_all.py --blogger swyx     # single blogger
python scripts/fetch_all.py --platform github  # single platform
```

### Adding a blogger (conversational)

Just tell the agent:
> "Track Simon Willison" or "Add @simonw on Twitter and github.com/simonw"

The agent parses the input, adds the entry to `config.json`, and monitors them from the next run.

### Adding a blogger (manual YAML)

Edit `config/bloggers.yaml`:

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
      watch_repos: []        # empty = all public activity
    substack:
      slug: "authorslug"
      enabled: true
    youtube:
      channel_id: "UCxxxxx"  # find from channel page source
      enabled: true
    xiaohongshu:
      uid: "xxxxxxxx"
      enabled: false
```

### Extending (Python scripts)

**New platform**: Create `scripts/fetchers/newplatform_fetcher.py` implementing `async def fetch(self, days_lookback) -> list[dict]`, then register in `fetch_all.py`'s `FETCHER_REGISTRY`.

**New push channel**: Create `scripts/pushers/newchannel_pusher.py` implementing `async def push(self, report) -> bool`, then register in `PUSHER_REGISTRY`.

---

## Agent compatibility

This project ships with a `SKILL.md` following the standard skill specification (v3), compatible with:

- **OpenClaw** (recommended — full agent-native workflow)
- **Claude Code** (claude.ai/code)
- **Claude** (claude.ai Projects)
- Any agent platform supporting SKILL.md

---

## License

MIT · Built with ❤️ by [billyhetech](https://github.com/billyhetech)
