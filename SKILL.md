---
name: blogger-radar
description: Monitors creator/blogger profiles across Twitter/X, YouTube, Substack, and GitHub (Xiaohongshu supported for Chinese creators). Fetches recent activity, uses the agent to summarize and extract insights, then delivers a structured daily intelligence briefing to Notion, Email, Slack, Discord, Telegram, Feishu, WeChat, or any OpenClaw channel — no LLM API key required. Use this skill whenever the user mentions: tracking bloggers or influencers, competitor monitoring, creator intelligence, daily content briefing, or wants to set up an automated creator-monitoring workflow. Also triggers for "run my blogger radar" or "/blogger-radar". Works with OpenClaw native cron and GitHub Actions.
license: MIT
compatibility: Python 3.11+; OpenClaw native cron or GitHub Actions
metadata:
  author: billyhetech
  version: "2.0.0"
  openclaw: '{"requires":{"env":[]},"primaryEnv":"","emoji":"📡","user-invocable":true}'
---

# Blogger Radar — Daily Intelligence Briefing

> The agent (you) handles all summarization — no `ANTHROPIC_API_KEY` needed.
> Scripts only fetch data and push the final report.

---

## Platform Detection

```bash
which openclaw 2>/dev/null && echo "PLATFORM=openclaw" || echo "PLATFORM=other"
```

- **OpenClaw**: Persistent agent with built-in channels. Use `openclaw cron add` for scheduling.
- **Other** (Claude Code, GitHub Actions): Use system cron or GitHub Actions. See `references/deploy.md`.

---

## First Run — Check Config

```bash
cat ~/.blogger-radar/config.json 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('SETUP_COMPLETE' if d.get('setupComplete') else 'NEEDS_SETUP')" \
  2>/dev/null || echo "NEEDS_SETUP"
```

- `SETUP_COMPLETE` → jump to **[Content Delivery Workflow](#content-delivery-workflow)**
- `NEEDS_SETUP` → run **[First-Time Onboarding](#first-time-onboarding)** below

---

## First-Time Onboarding

Walk the user through setup conversationally — the goal is zero to first report in under 5 minutes.

### Step 1: Introduce

Tell the user:
> "I'm Blogger Radar. I track creators across Twitter/X, GitHub, Substack, and YouTube, then deliver a daily AI-powered briefing. Let me ask a few quick questions — this takes about 2 minutes."

Read `examples/sample-report.md` and show a short excerpt so they can see what the output looks like.

### Step 2: Who to Track

Ask:
> "Which creators do you want to track? Give me their names and any handles or profile links."

Parse free-form input and map to platforms:
- `@handle` or `twitter.com/xxx` → Twitter
- `github.com/xxx` → GitHub
- `xxx.substack.com` → Substack
- `youtube.com/@xxx` → YouTube
- Xiaohongshu profile URL → extract UID *(Chinese creators only — requires RSSHub setup)*

Keep asking until they say done. Aim for 3–10 bloggers to start.

### Step 3: Report Language

Ask:
> "Preferred briefing language: English (default), Chinese, or Bilingual (both)?"

Save as `"language": "en"`, `"zh"`, or `"bilingual"`.

### Step 4: Report Preferences

Ask what to include (all on by default):
- Key highlights, New tools/products, Content strategy observations
- Engagement signals, Content opportunities, Original post links

### Step 5: Delivery Channel

Present options in this priority order:

| Option | Best for | Credentials needed |
|---|---|---|
| **Notion** | Searchable knowledge base | Database ID + integration token |
| **Email** | Universal, zero friction | SMTP credentials |
| **Slack** | Team sharing | Incoming Webhook URL |
| **Discord** | Community/personal server | Webhook URL |
| **Telegram** | Personal messaging | Bot token + chat ID |
| **Feishu / Lark** | East Asian enterprise | Webhook URL |
| **WeChat Work** | Chinese enterprise | Webhook URL |
| **In-chat only** | No external push needed | Nothing |

If on OpenClaw, also offer "deliver to this chat" — the simplest option.

For each chosen channel, guide the user through credentials step by step.
Store credentials in `~/.blogger-radar/.env` (not in config.json).

### Step 6: Schedule

Ask:
> "How often? Daily (pick a time), weekly (pick day + time), or on-demand only?"

Convert to a cron expression and store in config.

- **OpenClaw + scheduled**: run OpenClaw Cron Setup (see below) automatically
- **Non-OpenClaw + scheduled**: configure system crontab (see `references/deploy.md`)
- **On-demand**: skip cron setup; tell them: "Just say 'run my blogger radar' whenever you want one."

### Step 7: Save Config

```bash
mkdir -p ~/.blogger-radar
```

Write `~/.blogger-radar/config.json`:

```json
{
  "platform": "<openclaw | other>",
  "setupComplete": true,
  "language": "<en | zh | bilingual>",
  "bloggers": [
    {
      "id": "<slug>",
      "name": "<Display Name>",
      "tags": [],
      "note": "",
      "platforms": {
        "twitter": "<@handle or omit>",
        "github": "<username or omit>",
        "substack": "<slug or omit>",
        "youtube": "<channel_id or omit>",
        "xiaohongshu": "<uid or omit>"
      }
    }
  ],
  "report": {
    "daysLookback": 7,
    "maxPostsPerBlogger": 10,
    "includeHighlights": true,
    "includeTools": true,
    "includeStrategy": true,
    "includeEngagement": true,
    "includeOpportunities": true,
    "includeLinks": true
  },
  "schedule": {
    "frequency": "<daily | weekly | on-demand>",
    "time": "<HH:MM>",
    "timezone": "<IANA timezone>",
    "cron": "<cron expression>"
  },
  "delivery": [
    { "channel": "notion",   "enabled": false },
    { "channel": "email",    "enabled": false, "address": "" },
    { "channel": "slack",    "enabled": false },
    { "channel": "discord",  "enabled": false },
    { "channel": "telegram", "enabled": false },
    { "channel": "feishu",   "enabled": false },
    { "channel": "wechat",   "enabled": false }
  ],
  "cronJobId": ""
}
```

Write `~/.blogger-radar/.env` with credentials for each enabled channel:

```bash
# Notion
NOTION_TOKEN=
NOTION_DATABASE_ID=

# Email (SMTP)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Slack / Discord / Telegram / Feishu / WeChat Work
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
FEISHU_WEBHOOK_URL=
WECHAT_WEBHOOK_URL=

# Platform fetchers (all optional)
TWITTER_BEARER_TOKEN=
YOUTUBE_API_KEY=
GITHUB_TOKEN=
RSSHUB_BASE_URL=
RSSHUB_ACCESS_KEY=
```

### Step 8: First Report

Tell the user:
> "Setup complete! Fetching today's content now — this takes about a minute."

Then run the full **Content Delivery Workflow** immediately.

Afterwards ask:
> "That's your first briefing! Too long, too short, or anything to adjust?"

Apply feedback (update config.json or copy prompt files to `~/.blogger-radar/prompts/` for customization).

---

## Content Delivery Workflow

Run this on the cron schedule, or when manually triggered.

### Step 1: Load Config and Credentials

```bash
cat ~/.blogger-radar/config.json
export $(grep -v '^#' ~/.blogger-radar/.env | xargs) 2>/dev/null
```

### Step 2: Fetch Platform Data

```bash
python {baseDir}/scripts/fetch_all.py --config ~/.blogger-radar/config.json
```

Output at `/tmp/br-fetch-result.json`:
```json
{
  "fetched_at": "2025-04-07T00:00:00Z",
  "blogger_count": 3,
  "language": "en",
  "results": [
    {
      "blogger": { "id": "swyx", "name": "swyx", "tags": [], "note": "" },
      "posts_by_platform": {
        "twitter": [ { "date": "...", "title": "...", "body": "...", "url": "..." } ],
        "github":  [ ... ]
      },
      "fetched_at": "2025-04-07T00:00:00Z"
    }
  ]
}
```

Non-fatal fetch errors for individual platforms are expected — continue with whatever data was returned.

### Step 3: Check for Content

Read `/tmp/br-fetch-result.json`. If `blogger_count` is 0 or `results` is empty:
> "No new posts from your tracked creators this week. Check back tomorrow!"

Then stop.

### Step 4: Summarize Each Blogger

Read `{baseDir}/prompts/summarize-blogger.md` — it tells you exactly what to extract and how.

For each entry in `results`:
1. Take their `posts_by_platform` data
2. Follow `prompts/summarize-blogger.md` to produce a summary
3. Keep each summary in memory for the next step

The key discipline here: only use what's in the fetched data. Don't invent facts, don't visit URLs, don't search the web. Every referenced post should include its URL from the JSON.

### Step 5: Assemble the Report

Read `{baseDir}/prompts/report-format.md` — it defines the exact markdown template and ordering rules.

If `language` is `"zh"` or `"bilingual"`, also read `{baseDir}/prompts/translate.md`.

Check for user-customized prompt overrides:
```bash
ls ~/.blogger-radar/prompts/ 2>/dev/null
```
If a file exists there (e.g. `~/.blogger-radar/prompts/summarize-blogger.md`), use it instead of the default.

### Step 6: Deliver

Save the report:
```bash
cat > /tmp/br-report.txt << 'REPORT'
{your assembled report}
REPORT
```

Push to all enabled channels:
```bash
python {baseDir}/scripts/deliver.py \
  --report /tmp/br-report.txt \
  --config ~/.blogger-radar/config.json \
  --env ~/.blogger-radar/.env
```

If a channel fails, show the report inline as fallback.

If on **OpenClaw with in-chat delivery**, just output the report directly — OpenClaw delivers it to the user's channel.

---

## OpenClaw Cron Setup

### Channel and target ID reference

| Channel | Target format | How to find |
|---|---|---|
| Telegram | Numeric chat ID (`123456789`; groups use `-100xxx`) | `openclaw logs --follow`, send test message, read `from.id` |
| Feishu | `ou_xxx` (user) or `oc_xxx` (group) | `openclaw pairing list feishu` |
| Discord | `channel:<channel_id>` | Developer Mode → right-click → copy ID |
| Slack | `channel:<channel_id>` | Right-click channel → copy link → extract ID |
| WhatsApp | Phone with country code (`+15551234567`) | User provides |

### Create the job

```bash
openclaw cron add \
  --name "Blogger Radar" \
  --cron "<cron expression>" \
  --tz "<user timezone>" \
  --session isolated \
  --message "Run blogger-radar skill: fetch data, summarize, deliver report" \
  --announce \
  --channel <channel_name> \
  --to "<target_id>" \
  --exact
```

Save the returned job ID to `config.json` under `"cronJobId"`.

Always specify `--channel` and `--to` explicitly — never use `--channel last`.

### Verify

```bash
openclaw cron list
openclaw cron run <jobId>
```

Confirm delivery was received before finishing setup.

---

## Required Credentials (by channel)

Store all in `~/.blogger-radar/.env`.

| Variable(s) | Channel |
|---|---|
| `NOTION_TOKEN` + `NOTION_DATABASE_ID` | Notion |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | Email |
| `SLACK_WEBHOOK_URL` | Slack |
| `DISCORD_WEBHOOK_URL` | Discord |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | Telegram |
| `FEISHU_WEBHOOK_URL` | Feishu |
| `WECHAT_WEBHOOK_URL` | WeChat Work |
| `TWITTER_BEARER_TOKEN` | Optional — improves Twitter fetching |
| `YOUTUBE_API_KEY` | Optional — required for YouTube |
| `GITHUB_TOKEN` | Optional — raises API rate limit from 60→5000/hr |
| `RSSHUB_BASE_URL` | Optional — only needed for Xiaohongshu (Chinese creators) |

> GitHub Actions mode: the agent is absent, so AI summarization is unavailable. Raw fetched content is pushed instead. See `references/deploy.md`.

---

## Configuration Management

Handle settings changes conversationally:

- **Add blogger**: `"Track Simon Willison"` → add to `bloggers[]` in config.json
- **Remove blogger**: `"Stop tracking Matt Wolfe"` → remove from `bloggers[]`
- **Change schedule**: update `schedule` + cron job
- **Change language**: update `"language"` in config.json
- **Show settings**: read config.json and display clearly
- **Customize output style**: copy the relevant file to `~/.blogger-radar/prompts/` and edit it
  ```bash
  cp {baseDir}/prompts/summarize-blogger.md ~/.blogger-radar/prompts/
  ```
  To reset, delete the override. The skill's default is restored automatically.

---

## File Map

```
blogger-radar/
├── SKILL.md
├── prompts/
│   ├── summarize-blogger.md   ← per-blogger analysis instructions (Step 4)
│   ├── report-format.md       ← report template + ordering rules (Step 5)
│   └── translate.md           ← zh/bilingual output rules (Step 5, if needed)
├── scripts/
│   ├── fetch_all.py           ← fetches all platforms → /tmp/br-fetch-result.json
│   ├── deliver.py             ← pushes report to configured channels
│   ├── fetchers/              ← one fetcher per platform
│   └── pushers/               ← notion, email, slack, discord, telegram, feishu, wechat
├── examples/
│   └── sample-report.md       ← real example output (show to user in Step 1)
└── references/
    ├── platforms.md           ← platform-specific fetch details
    └── deploy.md              ← GitHub Actions / system cron / Vercel deployment
```
