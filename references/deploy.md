# references/deploy.md
# Deployment Guide: OpenClaw / GitHub Actions / Vercel Cron

## Table of Contents
1. [OpenClaw Native Cron (recommended)](#openclaw-native-cron)
2. [GitHub Actions](#github-actions)
3. [Local Testing](#local-testing)
4. [Vercel Cron (migration path)](#vercel-cron)
5. [Secrets Reference](#secrets-reference)

---

## OpenClaw Native Cron

> If you are using OpenClaw, this is the simplest deployment option — no repository required.
> The agent (Claude) handles all summarization; scripts only fetch data and push reports.

### Architecture

```
openclaw cron
    └─ triggers agent
         ├─ python fetch_all.py        → /tmp/br-fetch-result.json
         ├─ agent reads fetch result
         │   + prompts/summarize-blogger.md
         │   + prompts/report-format.md
         │   → writes /tmp/br-report.txt
         └─ python deliver.py --report /tmp/br-report.txt
              → pushes to configured channels
```

No `ANTHROPIC_API_KEY` needed — the agent IS the LLM.

### Step 1: Identify your channel and target ID

| Channel | Target format | How to find it |
|---|---|---|
| Telegram | Numeric chat ID (e.g. `123456789`; groups use `-100xxx`) | `openclaw logs --follow`, send a test message, read `from.id` |
| Telegram forum | `{group_id}:topic:{topic_id}` | Same as above, include the topic thread ID |
| Feishu | User `ou_xxx` or group `oc_xxx` | `openclaw pairing list feishu` or check gateway logs |
| Discord | `channel:<channel_id>` (channel) or `user:<user_id>` (DM) | Enable Developer Mode → right-click to copy ID |
| Slack | `channel:<channel_id>` (e.g. `channel:C1234567890`) | Right-click channel name → copy link → extract ID |
| WhatsApp | Phone number with country code (e.g. `+15551234567`) | User provides directly |

### Step 2: Create the cron job

```bash
openclaw cron add \
  --name "Blogger Radar Daily" \
  --cron "0 0 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Run blogger-radar skill: fetch all platforms, summarize, push report" \
  --announce \
  --channel <channel_name> \
  --to "<target_id>" \
  --exact
```

Common cron expressions (UTC):
- Daily 08:00 Beijing: `"0 0 * * *"`
- Daily 22:00 Beijing: `"0 14 * * *"`
- Weekly Monday 09:00 Beijing: `"0 1 * * 1"`
- Daily 08:00 London (GMT): `"0 8 * * *"`
- Daily 08:00 New York (EST): `"0 13 * * *"`

> **Important:** Always specify both `--channel` and `--to` explicitly. Do not use `--channel last` — it fails when multiple channels are configured.

### Step 3: Verify immediately

```bash
openclaw cron list                          # confirm the job was created
openclaw cron run <jobId>                   # trigger a test run immediately
openclaw cron runs --id <jobId> --limit 1   # inspect the run result
```

Confirm you received the briefing in your channel before relying on the schedule.

### Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Channel is required when multiple channels are configured` | Used `--channel last` | Specify exact channel name |
| `Delivering to X requires target` | Missing `--to` | Add the target ID |
| `No agent` | Multiple agent instances | Add `--agent <agent-id>` |

---

## GitHub Actions

> **Note:** In GitHub Actions mode, the agent (Claude) is not present, so AI summarization
> is not available. Reports contain raw fetched content only (post titles, links, dates).
> Full AI summaries require running in OpenClaw / Claude Code agent mode.

### Step 1: Set up your repository

```bash
# Clone or fork this project to your GitHub account
git clone https://github.com/yourname/blogger-radar
cd blogger-radar

# Copy config templates
cp config/bloggers.example.yaml config/bloggers.yaml
cp config/push.example.yaml config/push.yaml

# Edit your blogger list and delivery channels
nano config/bloggers.yaml
nano config/push.yaml

# Copy the workflow file
mkdir -p .github/workflows
cp assets/github-actions-workflow.yml .github/workflows/blogger-radar.yml

git add . && git commit -m "feat: setup blogger-radar" && git push
```

### Step 2: Configure secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret.

**Required per enabled delivery channel:**

| Secret | Channel | Description |
|---|---|---|
| `NOTION_TOKEN` | Notion | Integration token |
| `NOTION_DATABASE_ID` | Notion | Target database ID |
| `SMTP_HOST` | Email | SMTP server address |
| `SMTP_USER` | Email | Sender email address |
| `SMTP_PASS` | Email | App password |
| `SLACK_WEBHOOK_URL` | Slack | Incoming Webhook URL |
| `DISCORD_WEBHOOK_URL` | Discord | Webhook URL |
| `TELEGRAM_BOT_TOKEN` | Telegram | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram | Target chat/channel ID |
| `FEISHU_WEBHOOK_URL` | Feishu | Custom bot webhook URL |
| `WECHAT_WEBHOOK_URL` | WeChat Work | Group robot webhook URL |

**Optional (for fetching):**

| Secret | Description |
|---|---|
| `TWITTER_BEARER_TOKEN` | Twitter API Bearer Token |
| `YOUTUBE_API_KEY` | YouTube Data API key |
| `GITHUB_TOKEN` | Raises rate limit from 60 to 5000 req/hr |
| `RSSHUB_BASE_URL` | Self-hosted RSSHub URL |

### Step 3: Trigger a test run

Repo → Actions → Blogger Radar Daily Briefing → Run workflow.

---

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Copy the env template and fill in your keys
cp env.example .env
# Edit .env with your credentials

# Load env vars (bash)
export $(grep -v '^#' .env | xargs)

# Fetch only (writes to /tmp/br-fetch-result.json)
python scripts/fetch_all.py --dry-run

# Test a single blogger
python scripts/fetch_all.py --blogger swyx --dry-run

# Test a single platform
python scripts/fetch_all.py --platform github --dry-run

# After running the agent to produce /tmp/br-report.txt:
# Test delivery dry run (shows which channels would receive the report)
python scripts/deliver.py --report /tmp/br-report.txt --dry-run

# Push to a single channel for testing
python scripts/deliver.py --report /tmp/br-report.txt --channel slack
```

---

## Vercel Cron

> Useful when migrating to a Next.js/Vercel project or for finer scheduling control.
> Same limitation as GitHub Actions: no AI summarization without an agent present.

### vercel.json

```json
{
  "crons": [
    {
      "path": "/api/blogger-radar",
      "schedule": "0 0 * * *"
    }
  ]
}
```

### pages/api/blogger-radar.ts

```typescript
import type { NextApiRequest, NextApiResponse } from 'next'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  try {
    await execAsync('python scripts/fetch_all.py')
    // Note: AI summarization not available here — deliver raw fetch output
    await execAsync('python scripts/deliver.py --report /tmp/br-fetch-result.json')
    return res.status(200).json({ success: true })
  } catch (error) {
    return res.status(500).json({ error: String(error) })
  }
}
```

---

## Secrets Reference

```bash
# .env — local development only, NEVER commit to git

# === Notion ===
NOTION_TOKEN=secret_xxxxx
NOTION_DATABASE_ID=xxxxx-xxxxx-xxxxx

# === Email (Gmail example) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your_app_password     # Gmail: Account Security → App Passwords

# === Slack ===
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# === Discord ===
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# === Telegram ===
TELEGRAM_BOT_TOKEN=123456789:ABCDefgh...
TELEGRAM_CHAT_ID=123456789

# === Feishu / Lark ===
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/...

# === WeChat Work ===
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx

# === Twitter/X (optional) ===
TWITTER_BEARER_TOKEN=AAAAAxxxxx

# === YouTube (optional) ===
YOUTUBE_API_KEY=AIzaxxxxx

# === GitHub (optional, raises rate limit) ===
GITHUB_TOKEN=ghp_xxxxx

# === Xiaohongshu via RSSHub (optional) ===
RSSHUB_BASE_URL=https://your-rsshub.vercel.app
RSSHUB_ACCESS_KEY=your_key
```
