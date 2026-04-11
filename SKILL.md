---
name: blogger-radar
description: >
  Monitors configured creator/blogger profiles across Twitter/X, Xiaohongshu,
  YouTube, Substack, and GitHub. Fetches their recent activity, uses the agent
  to summarize content and extract insights, then delivers a structured daily
  briefing to Notion, Email, Slack, Discord, Telegram, Feishu, WeChat, or any
  OpenClaw channel — no LLM API key required. Trigger whenever the user mentions:
  monitoring bloggers, tracking influencers, competitor analysis, daily briefing,
  creator tracking, content intelligence, or wants to set up an automated content
  intelligence workflow. Works with OpenClaw native cron and GitHub Actions.
license: MIT
compatibility: Python 3.11+; OpenClaw native cron or GitHub Actions
metadata:
  author: billyhetech
  version: "2.0.0"
  openclaw: '{"requires":{"env":[]},"primaryEnv":"","emoji":"📡","user-invocable":true}'
---

# Blogger Radar — Daily Intelligence Briefing Skill

> **No LLM API key required.** The agent itself handles summarization.
> Raw data is fetched by a script; you (the agent) do the analysis using the prompts in `prompts/`.

---

## Platform Detection

Before doing anything, detect which platform you're running on:

```bash
which openclaw 2>/dev/null && echo "PLATFORM=openclaw" || echo "PLATFORM=other"
```

- **OpenClaw** (`PLATFORM=openclaw`): Persistent agent with built-in channels. Use `openclaw cron add` for scheduling. Deliver to the user's active channel.
- **Other** (Claude Code, GitHub Actions, etc.): Use system cron or GitHub Actions. See `references/deploy.md`.

---

## First Run — Check for Existing Config

**Before anything else**, check if setup has already been completed:

```bash
cat ~/.blogger-radar/config.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('SETUP_COMPLETE') if d.get('setupComplete') else print('NEEDS_SETUP'" 2>/dev/null || echo "NEEDS_SETUP"
```

- If `SETUP_COMPLETE` → jump to **[Content Delivery Workflow](#content-delivery-workflow)**
- If `NEEDS_SETUP` → run the **[First-Time Onboarding](#first-time-onboarding)** below

---

## First-Time Onboarding

Walk the user through setup conversationally. Save their answers progressively.
The goal is to get them from zero to their first report in under 5 minutes.

### Step 1: Introduction

Tell the user:

> "I'm Blogger Radar. I monitor the creators you care about — across Twitter/X, GitHub, Substack, YouTube, and Xiaohongshu — and deliver a daily AI-powered intelligence briefing.
>
> Let me ask you a few quick questions to get set up. This takes about 2 minutes."

Read `examples/sample-report.md` and show a short excerpt so they can see what the output looks like.

### Step 2: Who to Track

Ask:
> "Which creators do you want to track? Give me their names plus any handles or profile links you have.
> For example: 'swyx (@swyx on Twitter, github.com/swyxio)' or 'Simon Willison (simonw on GitHub)'."

Accept free-form input. Parse out the handles/URLs and map them to platforms:
- `twitter.com/xxx` or `@xxx` → Twitter handle
- `github.com/xxx` → GitHub username
- `xxx.substack.com` → Substack slug
- `youtube.com/@xxx` or channel URL → YouTube channel ID
- Xiaohongshu profile URL → extract UID

Ask if they want to add more. Keep going until they say they're done.
Aim for 3–10 bloggers to start.

### Step 3: Report Language

Ask:
> "What language do you prefer for your briefing?"

- **English** (default) — summaries and report in English
- **Chinese** — summaries and report in Chinese
- **Bilingual** — English and Chinese side by side

Save as `"language": "en"`, `"zh"`, or `"bilingual"`.

### Step 4: Report Preferences

Ask:
> "What do you want included in each blogger's section?"

Present as a checklist (all on by default):
- ✅ Key highlights (what they did/published this week)
- ✅ New tools or products they mentioned
- ✅ Content strategy observations
- ✅ Engagement signals
- ✅ Content opportunities (gaps you could cover)
- ✅ Original post links

Let them toggle any off. Save as boolean fields in `report` config.

### Step 5: Delivery Channel

Ask:
> "Where do you want your briefing delivered?"

Present options in priority order for English-speaking users:

| Option | Best for | Setup needed |
|---|---|---|
| **Notion** | Searchable personal knowledge base | Database ID + token |
| **Email** | Universal, zero friction | SMTP credentials |
| **Slack** | Team sharing | Webhook URL |
| **Discord** | Community/personal server | Webhook URL |
| **Telegram** | Personal messaging | Bot token + chat ID |
| **Feishu / Lark** | East Asian corporate teams | Webhook URL |
| **WeChat Work** | Chinese enterprise teams | Webhook URL |
| **In-chat only** | No external push needed | Nothing |

**If OpenClaw:** Also offer "deliver to this chat" — the simplest option. Detect the current channel and offer to reuse it.

For each chosen channel, guide the user through the required credentials step by step.
Store credentials in `~/.blogger-radar/.env` (not in config.json).

### Step 6: Schedule

Ask:
> "How often do you want your briefing?"

- **Daily** — pick a time (e.g. "8am Beijing time")
- **Weekly** — pick a day + time
- **On-demand only** — just run `/blogger-radar` whenever you want one

Convert their answer to a cron expression. Store in config.

**If OpenClaw + not on-demand:**
Set up the cron job automatically (see OpenClaw Cron Setup below).
Ask the user which channel/target to deliver to.

**If not OpenClaw + Telegram or Email:**
Set up system crontab (see `references/deploy.md`).

**If on-demand:**
Skip cron setup entirely. Tell them: "No problem — just say 'run my blogger radar' whenever you want a briefing."

### Step 7: Save Config

Write `~/.blogger-radar/config.json`:

```bash
mkdir -p ~/.blogger-radar
cat > ~/.blogger-radar/config.json << 'EOF'
{
  "platform": "<openclaw or other>",
  "setupComplete": true,
  "language": "<en | zh | bilingual>",
  "bloggers": [
    {
      "id": "<slug>",
      "name": "<Display Name>",
      "tags": [],
      "platforms": {
        "twitter": "<@handle or empty>",
        "github": "<username or empty>",
        "substack": "<slug or empty>",
        "youtube": "<channel_id or empty>",
        "xiaohongshu": "<uid or empty>"
      }
    }
  ],
  "report": {
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
    "cron": "<cron expression or empty>",
    "weeklyDay": "<day of week, only if weekly>"
  },
  "delivery": [
    { "channel": "notion", "enabled": <true|false> },
    { "channel": "email", "enabled": <true|false>, "address": "<email>" },
    { "channel": "slack", "enabled": <true|false> },
    { "channel": "discord", "enabled": <true|false> },
    { "channel": "telegram", "enabled": <true|false> },
    { "channel": "feishu", "enabled": <true|false> },
    { "channel": "wechat", "enabled": <true|false> }
  ],
  "cronJobId": ""
}
EOF
```

Then write credentials to `~/.blogger-radar/.env` (one per enabled channel):

```bash
cat > ~/.blogger-radar/.env << 'EOF'
# Notion
NOTION_TOKEN=
NOTION_DATABASE_ID=

# Email (SMTP)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Slack
SLACK_WEBHOOK_URL=

# Discord
DISCORD_WEBHOOK_URL=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Feishu / Lark
FEISHU_WEBHOOK_URL=

# WeChat Work
WECHAT_WEBHOOK_URL=

# Platform fetchers (optional)
TWITTER_BEARER_TOKEN=
YOUTUBE_API_KEY=
GITHUB_TOKEN=
RSSHUB_BASE_URL=
RSSHUB_ACCESS_KEY=
EOF
```

Prompt the user to fill in the values for their chosen channels. Open the file for editing if possible.

### Step 8: Generate First Report

**Do NOT skip this step.** Generate the first report immediately so the user sees what they're getting.

Tell the user:
> "Setup complete! Let me fetch today's content and show you your first briefing right now. This takes about a minute."

Then run the full Content Delivery Workflow (next section) immediately.

After delivering it, ask:
> "That's your first Blogger Radar briefing! How does it look? Too long? Too short? Anything you'd like me to focus on more?"

Apply any feedback (update config.json or prompt files under `~/.blogger-radar/prompts/` as needed).

---

## Content Delivery Workflow

Run this on cron schedule or when manually triggered.

### Step 1: Load Config

```bash
cat ~/.blogger-radar/config.json
```

Load `.env` credentials:
```bash
export $(grep -v '^#' ~/.blogger-radar/.env | xargs) 2>/dev/null
```

### Step 2: Fetch All Platform Data

```bash
cd {baseDir}/scripts && python fetch_all.py --config ~/.blogger-radar/config.json
```

This outputs `/tmp/br-fetch-result.json` with structure:
```json
{
  "fetched_at": "2025-04-07T00:00:00Z",
  "language": "en",
  "bloggers": [
    {
      "blogger": { "id": "swyx", "name": "swyx", ... },
      "posts_by_platform": {
        "twitter": [ { "date": "...", "title": "...", "body": "...", "url": "..." } ],
        "github": [ ... ]
      }
    }
  ],
  "stats": { "total_bloggers": 3, "total_posts": 42 },
  "errors": []
}
```

If the script fails entirely, check the user's internet connection and try again.
Non-fatal errors in `errors[]` are expected (e.g. a platform returning no results) — proceed anyway.

### Step 3: Check for Content

Read `/tmp/br-fetch-result.json`. If `stats.total_posts` is 0, tell the user:
> "No new posts from your tracked creators this week. Check back tomorrow!"
Then stop.

### Step 4: Summarize Each Blogger

Read `{baseDir}/prompts/summarize-blogger.md` for instructions.

For each blogger in the results:
1. Extract their `posts_by_platform` data
2. Follow the instructions in `prompts/summarize-blogger.md` to produce a summary JSON
3. Keep each blogger's summary in memory

**ABSOLUTE RULES:**
- Never invent content. Only use what's in the fetched data.
- Every referenced post must include its URL from the JSON.
- Do not visit any URLs, search the web, or call any APIs.

### Step 5: Assemble the Report

Read `{baseDir}/prompts/report-format.md` for the report structure.

Build the complete report as markdown text following those instructions.

If `language` is `"zh"` or `"bilingual"`, read `{baseDir}/prompts/translate.md` and apply.

Check `~/.blogger-radar/prompts/` for any user-customized prompt overrides:
```bash
ls ~/.blogger-radar/prompts/ 2>/dev/null
```
If a file exists there (e.g. `~/.blogger-radar/prompts/summarize-blogger.md`), use it instead of the default.

### Step 6: Deliver

Save the report to a temp file:
```bash
cat > /tmp/br-report.txt << 'REPORT'
{your assembled report here}
REPORT
```

Then push to all enabled channels:
```bash
cd {baseDir}/scripts && python deliver.py \
  --report /tmp/br-report.txt \
  --config ~/.blogger-radar/config.json \
  --env ~/.blogger-radar/.env
```

If `deliver.py` fails for a channel, show the report inline as fallback.

**If running on OpenClaw** and the user chose "in-chat" delivery:
Just output the report text directly — OpenClaw will deliver it to the user's channel.

---

## OpenClaw Cron Setup

After the user confirms their schedule and delivery channel, set up the cron job:

### Step 1: Get the channel + target ID

| Channel | Target format | How to find |
|---|---|---|
| Telegram | Numeric chat ID (e.g. `123456789`) | `openclaw logs --follow`, send test message, read `from.id` |
| Feishu | `ou_xxx` (user) or `oc_xxx` (group) | `openclaw pairing list feishu` |
| Discord | `channel:<channel_id>` | Developer Mode → right-click → copy ID |
| Slack | `channel:<channel_id>` | Right-click channel → copy link → extract ID |
| WhatsApp | Phone with country code (e.g. `+15551234567`) | User provides |

### Step 2: Create the cron job

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

### Step 3: Verify

```bash
openclaw cron list
openclaw cron run <jobId>
```

Confirm delivery was received before finishing setup.

> **Important:** Always specify `--channel` + `--to` explicitly. Never use `--channel last`.

---

## File Map

```
blogger-radar/
├── SKILL.md                        ← You are here
├── prompts/
│   ├── summarize-blogger.md        ← How to analyze one blogger (read in Step 4)
│   ├── report-format.md            ← How to assemble the report (read in Step 5)
│   └── translate.md                ← Chinese/bilingual output rules (read if zh/bilingual)
├── scripts/
│   ├── fetch_all.py                ← Fetch all platform data → /tmp/br-fetch-result.json
│   ├── deliver.py                  ← Push report to configured channels
│   └── fetchers/
│       ├── twitter_fetcher.py
│       ├── xiaohongshu_fetcher.py
│       ├── youtube_fetcher.py
│       ├── substack_fetcher.py
│       └── github_fetcher.py
│   └── pushers/
│       ├── notion_pusher.py
│       ├── email_pusher.py
│       ├── slack_pusher.py
│       ├── discord_pusher.py
│       ├── telegram_pusher.py
│       ├── feishu_pusher.py
│       └── wechat_pusher.py
├── examples/
│   └── sample-report.md            ← What a real report looks like
├── references/
│   ├── platforms.md                ← Platform-specific fetch strategies
│   └── deploy.md                   ← GitHub Actions / Vercel / OpenClaw deployment
└── assets/
    └── github-actions-workflow.yml ← GitHub Actions template
```

---

## Required Secrets (by channel)

Store all secrets in `~/.blogger-radar/.env`.

| Secret | When needed |
|---|---|
| `NOTION_TOKEN` + `NOTION_DATABASE_ID` | If Notion push enabled |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | If Email push enabled |
| `SLACK_WEBHOOK_URL` | If Slack push enabled |
| `DISCORD_WEBHOOK_URL` | If Discord push enabled |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | If Telegram push enabled |
| `FEISHU_WEBHOOK_URL` | If Feishu push enabled |
| `WECHAT_WEBHOOK_URL` | If WeChat Work push enabled |
| `TWITTER_BEARER_TOKEN` | Optional — improves Twitter fetching |
| `YOUTUBE_API_KEY` | Optional — required for YouTube fetching |
| `GITHUB_TOKEN` | Optional — raises rate limit from 60 to 5000 req/hr |
| `RSSHUB_BASE_URL` | Optional — required for Xiaohongshu fetching |

> **No ANTHROPIC_API_KEY needed.** The agent (you) handles all LLM work directly.
>
> Exception: GitHub Actions mode. Without an agent present, GitHub Actions can only push
> raw fetched content (no AI summary). See `references/deploy.md` for details.

---

## Configuration Management

When the user says something like a settings change, handle it conversationally.

### Add / remove a blogger
> "Track Simon Willison" → add to `bloggers[]` in config.json
> "Stop tracking Matt Wolfe" → remove from `bloggers[]`

### Change schedule
> "Switch to weekly on Mondays" → update `schedule` + update cron job
> "Change delivery time to 9pm" → update `schedule.time` + cron

### Change language
> "Switch to Chinese" → update `language: "zh"` in config.json

### Customize output style
Copy the relevant prompt file to `~/.blogger-radar/prompts/` and edit it:
```bash
cp {baseDir}/prompts/summarize-blogger.md ~/.blogger-radar/prompts/summarize-blogger.md
```
Edit the copy to match the user's preferences. Changes apply on next run.
To reset: delete the file from `~/.blogger-radar/prompts/`.

### Show current config
> "Show my settings" → read and display config.json in a friendly format
> "Who am I tracking?" → list bloggers from config.json
> "Show my schedule" → display schedule + cronJobId

---

## Agent Guidance: Common Tasks

### "Add a new blogger"
→ Ask for their name + handle/URL, detect platforms, add to `bloggers[]` in config.json

### "Run my blogger radar now"
→ Run the Content Delivery Workflow immediately (skip cron check)

### "The Xiaohongshu feed isn't working"
→ Check `references/platforms.md` → Xiaohongshu section → use manual mode as fallback

### "Add a Slack push channel"
→ Ask for the Slack webhook URL, add to `.env`, update `delivery` in config.json

### "Make the summaries shorter"
→ Copy `prompts/summarize-blogger.md` to `~/.blogger-radar/prompts/`, edit the guidelines section

### "Set up automatic daily delivery"
→ If no cron exists: run OpenClaw Cron Setup → or configure system crontab (see `references/deploy.md`)

### "What does the output look like?"
→ Show `examples/sample-report.md`
