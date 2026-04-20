---
name: blogger-radar
description: Monitors creator/blogger profiles across Twitter/X, YouTube, Substack, and GitHub (Xiaohongshu supported for Chinese creators). Fetches recent activity using the agent's built-in tools — no Python, no installs required. Summarizes natively and delivers a structured daily intelligence briefing in-conversation (default) or to Slack, Discord, Telegram, Feishu, WeChat, Notion, or Email. Archives every report locally by date for easy lookup. Use whenever the user mentions: tracking bloggers or influencers, competitor monitoring, creator intelligence, daily content briefing, or "run my blogger radar" / "/blogger-radar". Works with OpenClaw native cron and GitHub Actions.
license: MIT
compatibility: No external dependencies for basic use. curl required for webhook delivery (pre-installed on Mac/Linux; available via Git Bash or WSL on Windows).
metadata:
  author: billyhetech
  version: "3.0.0"
  openclaw: '{"requires":{"env":[]},"primaryEnv":"","emoji":"📡","user-invocable":true}'
---

# Blogger Radar — Daily Intelligence Briefing

> The agent (you) handles all fetching, summarization, and delivery — no Python, no Node.js, no installs needed.
> curl is only needed for external webhooks (Slack, Discord, Telegram, etc.).

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
[ -f ~/.blogger-radar/config.json ] && grep -q '"setupComplete": true' ~/.blogger-radar/config.json \
  && echo "SETUP_COMPLETE" || echo "NEEDS_SETUP"
```

- `SETUP_COMPLETE` → jump to **[Content Delivery Workflow](#content-delivery-workflow)**
- `NEEDS_SETUP` → run **[First-Time Onboarding](#first-time-onboarding)** below

---

## First-Time Onboarding

Walk the user through setup conversationally — zero to first report in under 5 minutes.

### Step 1: Introduce

Tell the user:
> "I'm Blogger Radar. I track creators across Twitter/X, GitHub, Substack, and YouTube, then deliver a daily AI-powered briefing — no Python or API keys needed to get started. Let me ask a few quick questions."

Read `examples/sample-report.md` and show a short excerpt so they can see what the output looks like.

### Step 2: Who to Track

Present three options:

> "I have a curated list of the **Top 30 AI builders** ready to go — hand-picked from multiple 'must-follow' sources. How would you like to start?"
>
> **[A] Use the built-in Top 30** — load all 30 immediately, start monitoring right away
> **[B] Pick from the Top 30** — I'll show you the list category by category, you choose who to include
> **[C] Add your own creators** — enter handles and links manually

The Top 30 spans six categories:
- **General Alpha (5)**: Karpathy, Sam Altman, Yann LeCun, Geoffrey Hinton, John Carmack
- **Technical Builders (8)**: swyx, Simon Willison, Jason Liu, Jerry Liu, Harrison Chase, Jeremy Howard, David Ha, Shreya Shankar
- **AI × Business (5)**: Aaron Levie, Dan Shipper, Ethan Mollick, Peter Yang, Kevin Weil
- **Content / Media (4)**: Matt Wolfe, Matthew Berman, Greg Isenberg, Riley Goodside
- **Indie Hackers (5)**: steipete, Marc Lou, Meng To, Amjad Massad, Pieter Levels
- **Product Leaders (3)**: Guillermo Rauch, Garry Tan, Matt Shumer

**If user picks [A]**: Load all entries from the [Embedded Blogger Registry](#embedded-blogger-registry) section below into config.json. Tell the user "All 30 loaded! You can add or remove anyone later." Move to Step 3.

**If user picks [B]**: Display the registry table category by category. Ask: "Type the names or numbers of anyone you'd like to skip, or press Enter to include everyone." Apply their selections, then move to Step 3.

**If user picks [C]**: Use the free-form input parsing below. After they finish, ask: "Would you like to add any of the Top 30 as well?"

Free-form input parsing:
- `@handle` or `twitter.com/xxx` → Twitter
- `github.com/xxx` → GitHub
- `xxx.substack.com` → Substack
- `youtube.com/@xxx` or `youtube.com/channel/xxx` → YouTube
- Xiaohongshu profile URL → extract UID *(requires RSSHub setup — see Required Credentials)*

### Step 3: Report Language

Ask:
> "Preferred briefing language: **English** (default), **Chinese**, or **Bilingual** (both side by side)?"

Save as `"language": "en"`, `"zh"`, or `"bilingual"`.

### Step 4: Report Preferences

Ask what sections to include (all on by default):
- Key highlights, New tools/products, Content strategy observations
- Engagement signals, Content opportunities, Original post links

### Step 5: Delivery Channel

> "Reports will appear **right here in this chat** by default — zero configuration needed.
> Would you also like to push to an external service?"

- **No / Skip** → in-conversation only, nothing to configure
- **Yes** → show the channel table below and guide them through credentials

| Channel | Best for | Credentials needed |
|---|---|---|
| **Slack** | Team sharing | Incoming Webhook URL |
| **Discord** | Community/personal server | Webhook URL |
| **Telegram** | Personal messaging | Bot token + chat ID |
| **Feishu / Lark** | East Asian enterprise | Webhook URL |
| **WeChat Work** | Chinese enterprise | Webhook URL |
| **Notion** | Searchable knowledge base | Database ID + integration token *(requires Python)* |
| **Email** | Universal | SMTP credentials *(requires Python)* |

Store credentials in `~/.blogger-radar/.env` (never in config.json).

### Step 6: Schedule

Ask:
> "How often? **Daily** (pick a time), **weekly** (pick day + time), or **on-demand only**?"

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
  "in_conversation": true,
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
        "youtube": "<channel_id UC... or omit>",
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
    "cron": "<cron expression>",
    "cronJobId": ""
  },
  "delivery": [
    { "channel": "in_conversation", "enabled": true },
    { "channel": "slack",    "enabled": false },
    { "channel": "discord",  "enabled": false },
    { "channel": "telegram", "enabled": false },
    { "channel": "feishu",   "enabled": false },
    { "channel": "wechat",   "enabled": false },
    { "channel": "notion",   "enabled": false },
    { "channel": "email",    "enabled": false, "address": "" }
  ],
  "archive": {
    "enabled": true,
    "reportsDir": "~/.blogger-radar/reports",
    "cacheDir": "~/.blogger-radar/cache"
  }
}
```

Write `~/.blogger-radar/.env` with credentials for each enabled channel:

```bash
# Slack / Discord / Telegram / Feishu / WeChat Work
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
FEISHU_WEBHOOK_URL=
WECHAT_WEBHOOK_URL=

# Notion (requires Python)
NOTION_TOKEN=
NOTION_DATABASE_ID=

# Email SMTP (requires Python)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Platform fetchers (all optional — see Required Credentials)
TWITTER_BEARER_TOKEN=
GITHUB_TOKEN=
RSSHUB_BASE_URL=
RSSHUB_ACCESS_KEY=
```

### Step 8: First Report

Tell the user:
> "Setup complete! Fetching today's content now — this takes about a minute."

Run the full **Content Delivery Workflow** immediately.

Afterwards ask:
> "That's your first briefing! Too long, too short, or anything to adjust?"

Apply feedback (update config.json or copy prompt files to `~/.blogger-radar/prompts/` for customization).

---

## Content Delivery Workflow

Run this on the cron schedule, or when manually triggered.

### Step 1: Load Config and Credentials

Read `~/.blogger-radar/config.json` directly (using the Read tool or Bash cat).
If `~/.blogger-radar/.env` exists, read it too and hold those values in context.

Parse the config to extract: `language`, `daysLookback`, `bloggers[]`, `delivery[]`, `archive` settings.

Calculate today's date and the cutoff date (today minus `daysLookback` days). Hold these in memory — no bash needed.

### Step 2: Fetch Platform Data (Agent-Native)

For each blogger in `config.bloggers`, fetch each active platform using WebFetch. Collect all results in memory.

**Do not run Python scripts in this step.** The agent fetches everything directly.

---

#### GitHub (no auth required for public repos)

For each blogger with `platforms.github`:
```
WebFetch: https://api.github.com/users/{username}/events/public?per_page=50
Headers: Accept: application/vnd.github+json
```
If `GITHUB_TOKEN` is available: add `Authorization: Bearer {token}` (raises rate limit from 60→5000/hr).

Filter events where `created_at` ≥ cutoff date. Extract:
- `PushEvent`: commit messages from `payload.commits[].message`
- `CreateEvent` (type=tag): release names
- `IssuesEvent`: issue titles

If `watch_repos` is non-empty, filter by `repo.name` suffix.

---

#### Substack (no auth required)

For each blogger with `platforms.substack`:
```
WebFetch: https://{slug}.substack.com/feed
```
Parse RSS/Atom XML. Extract `<item>` elements: `<title>`, `<link>`, `<pubDate>`, `<description>`.
Strip HTML from description, keep first 500 chars. Filter by pubDate ≥ cutoff.

---

#### YouTube (no API key required)

For each blogger with `platforms.youtube` (a `UC...` channel ID):
```
WebFetch: https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}
```
This is a free public Atom feed — no API key, no quota. Parse `<entry>` elements: `<title>`, `<link>` href, `<published>`. Filter by published ≥ cutoff. Respect `maxPostsPerBlogger`.

> **Note:** YouTube channel IDs start with `UC`. To find a channel ID from a handle (@name), visit the channel page and look for `channel_id` in the page source, or use a lookup tool.

---

#### Twitter/X (three strategies, in priority order)

**Strategy 1 — `/x-search` skill** (if xAI API key is configured via `XAI_API_KEY`):
Invoke the `/x-search` skill with query `from:{handle} -is:retweet -is:reply` and the lookback window.

**Strategy 2 — Nitter RSS fallback** (no credentials):
Try each instance in order until one succeeds:
```
WebFetch: https://nitter.net/{handle}/rss
WebFetch: https://nitter.privacydev.net/{handle}/rss
WebFetch: https://nitter.poast.org/{handle}/rss
```
Parse RSS items. Filter by pubDate ≥ cutoff. Skip retweets (titles starting with "RT").
If all instances fail, skip Twitter for this blogger and note it in the report header.

**Strategy 3 — Official API v2** (if `TWITTER_BEARER_TOKEN` in .env):
```
WebFetch: https://api.twitter.com/2/users/by/username/{handle}
  Headers: Authorization: Bearer {TWITTER_BEARER_TOKEN}
→ then: WebFetch: https://api.twitter.com/2/users/{id}/tweets
    ?max_results=10&tweet.fields=created_at,public_metrics,text
    &exclude=retweets,replies
    &start_time={cutoff_iso8601}
  Headers: Authorization: Bearer {TWITTER_BEARER_TOKEN}
```

---

#### Xiaohongshu (requires RSSHub)

If `platforms.xiaohongshu` is set AND `RSSHUB_BASE_URL` is in .env:
```
WebFetch: {RSSHUB_BASE_URL}/xiaohongshu/user/{uid}
```
Parse RSS. If RSSHub is not configured, skip and note "(Xiaohongshu: self-hosted RSSHub required)".

---

#### After fetching all bloggers

Check total post count across all bloggers and platforms.
If count = 0:
> "No new posts from your tracked creators in the last {daysLookback} days. Check back tomorrow!"

Stop. Do not proceed to summarization.

### Step 3: Summarize Each Blogger

Check for a user-customized prompt override:
```bash
[ -f ~/.blogger-radar/prompts/summarize-blogger.md ] && cat ~/.blogger-radar/prompts/summarize-blogger.md
```
If that file exists, use its instructions. Otherwise use the embedded prompt below:

---
**Embedded summarization instructions:**

You are a content intelligence analyst. For each blogger's fetched posts, produce a JSON summary:

```json
{
  "highlights": [
    "One-sentence description of the most notable content or action this period",
    "Second highlight (aim for 3–5 total)"
  ],
  "new_products_or_tools": ["Any tools, repos, products, or models they mentioned or launched"],
  "content_strategy_observations": [
    "Observation about their content format, tone, cadence, or angle (2–3 items)"
  ],
  "engagement_signals": "One sentence on what content seems to be resonating most.",
  "trend_direction": "rising | stable | declining",
  "content_opportunities": [
    "A content angle you could cover, inspired by their gaps or trending topics (2–3 items)"
  ]
}
```

Guidelines:
- **Highlights** must be specific and factual. Bad: "Posted about AI tools". Good: "Published a thread comparing Claude 3.5 vs GPT-4o for coding, with benchmark results"
- Include the post **URL** whenever referencing specific content: `[short description](url)`
- If a platform has no posts this period, skip it silently — don't write "no activity on X"
- Match output language to config `language` field (en / zh / bilingual)
- For bilingual: produce the JSON in English, then add a `"zh"` key with Chinese versions of highlights, observations, and opportunities
- Only use data from the fetched posts — do not invent facts or visit additional URLs

---

### Step 4: Assemble the Report

Check for a user-customized format override:
```bash
[ -f ~/.blogger-radar/prompts/report-format.md ] && cat ~/.blogger-radar/prompts/report-format.md
```
If that file exists, use its template. Otherwise use the embedded format below:

---
**Embedded report format:**

```
# 📡 Blogger Radar — {YYYY-MM-DD} · {Weekday}

Tracking {N} creator(s) · Generated by Blogger Radar
{if any platforms were skipped due to missing credentials, note them here in italics}

---

## {Blogger Name}

*Tags: tag1 · tag2* | *Active on: platform1, platform2* | *Posts analyzed: N*

> {blogger.note if non-empty}

**🔥 Highlights**
- {highlight with URL}
...

**🛠️ New Tools / Products**: tool1, tool2  ← omit entire line if none

**📊 Content Strategy**
- {observation}
...

**💬 Engagement Signals**: {one sentence}

**📈 Trend**: ↑ Rising | → Stable | ↓ Declining

**💡 Content Opportunities**
- {opportunity}
...

---

(repeat for each blogger)

---
*Generated by blogger-radar v3 · {timestamp} UTC · Archived to ~/.blogger-radar/reports/{YYYY}/{MM}/{YYYY-MM-DD}.md*
```

Formatting rules:
1. **Order bloggers**: rising first, then stable, then declining. Alphabetical within each tier.
2. **Omit empty sections**: never write "None" or "N/A" — just skip the section.
3. **Link every highlight** that references specific content.
4. **Keep it scannable**: bullets, not paragraphs. Each bullet max 2 lines.

For **bilingual** reports: interleave English and Chinese section by section within each blogger entry (not all-English then all-Chinese). Section labels in Chinese: 🔥 本周亮点 / 🛠️ 新工具·产品 / 📊 内容策略观察 / 💬 互动信号 / 📈 趋势判断 / 💡 可借鉴选题.

For **Chinese-only** reports: translate the entire report using those same Chinese section labels. Keep platform names, handles, URLs, and model names in English.

Translation rules:
- Keep proper nouns as-is: Twitter/X, GitHub, Substack, YouTube, OpenAI, Claude, GPT-4o
- Tech terms with no standard Chinese equivalent: keep English or write "英文（中文解释）" e.g. "RAG（检索增强生成）"
- Tone: professional but conversational, like a smart analyst briefing a colleague

---

### Step 5: Deliver

**Always first: output the full report in-conversation** (render the markdown directly in the chat).

Then push to each enabled external channel. Save the report to a temp file first:

Use the Write tool to save the assembled report to `/tmp/br-report.txt`.
On Windows (Git Bash): use `/tmp/br-report.txt` — Git Bash maps this correctly.

**Slack** (if `SLACK_WEBHOOK_URL` is set):
```bash
curl -s -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $(cat /tmp/br-report.txt | head -80 | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo '\"See in-chat report\"')}"
```

**Discord** (if `DISCORD_WEBHOOK_URL` is set):
```bash
curl -s -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $(cat /tmp/br-report.txt | head -80 | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo '\"See in-chat report\"')}"
```

**Telegram** (if `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` are set):
```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -F "chat_id=${TELEGRAM_CHAT_ID}" \
  -F "parse_mode=HTML" \
  -F "disable_web_page_preview=true" \
  --data-urlencode "text@/tmp/br-report.txt"
```

**Feishu / Lark** (if `FEISHU_WEBHOOK_URL` is set):
```bash
curl -s -X POST "$FEISHU_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"msg_type\":\"text\",\"content\":{\"text\":$(cat /tmp/br-report.txt | head -100 | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo '\"See in-chat report\"')}}"
```

**WeChat Work** (if `WECHAT_WEBHOOK_URL` is set):
```bash
curl -s -X POST "$WECHAT_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"msgtype\":\"markdown\",\"markdown\":{\"content\":$(cat /tmp/br-report.txt | head -100 | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo '\"See in-chat report\"')}}"
```

**Notion / Email**: These require Python. If Python is available:
```bash
python {baseDir}/scripts/deliver.py \
  --report /tmp/br-report.txt \
  --config ~/.blogger-radar/config.json \
  --env ~/.blogger-radar/.env \
  --channel notion   # or: --channel email
```
If Python is not available, note: "Notion/Email delivery requires Python. Run `pip install httpx python-dotenv` to enable, or use a webhook channel instead."

If any channel push fails, note the failure but do not stop — the in-conversation report is already delivered.

### Step 6: Archive

Create archive directories:
```bash
REPORT_YEAR=$(date -u +%Y)
REPORT_MONTH=$(date -u +%m)
REPORT_DATE=$(date -u +%Y-%m-%d)
mkdir -p ~/.blogger-radar/reports/${REPORT_YEAR}/${REPORT_MONTH}
mkdir -p ~/.blogger-radar/cache
```

**Save the report** using the Write tool:
- Path: `~/.blogger-radar/reports/{YYYY}/{MM}/{YYYY-MM-DD}.md`
- Prepend a comment header: `<!-- blogger-radar v3 · {timestamp} UTC · {N} bloggers · {active platforms} -->`
- Then the full report markdown

**Save raw cache data** (for reprocessing without re-fetching):
- Path: `~/.blogger-radar/cache/{YYYY-MM-DD}.json`
- Content:
```json
{
  "fetched_at": "<ISO timestamp>",
  "config_snapshot": { "language": "...", "daysLookback": 7 },
  "bloggers_fetched": N,
  "results": [ ... same per-blogger fetch results from Step 2 ... ]
}
```

**Update the index** at `~/.blogger-radar/reports/README.md`:

Read it if it exists. Insert a new row at the top of the table (newest first). If it doesn't exist yet, create it:

```markdown
# Blogger Radar — Report Archive

| Date | Bloggers | File |
|---|---|---|
| {YYYY-MM-DD} | {N} creators | [view](reports/{YYYY}/{MM}/{YYYY-MM-DD}.md) |
```

---

## Report Lookup Commands

Use these conversational commands to access archived reports at any time.

### "Show today's report" / "Show the last report"
```bash
ls -t ~/.blogger-radar/reports/*/*.md 2>/dev/null | head -1 | xargs cat
```

### "Show [date]'s report" (e.g. "show last Tuesday's report", "show April 15th")
Resolve the date to YYYY-MM-DD format, then:
```bash
cat ~/.blogger-radar/reports/{YYYY}/{MM}/{YYYY-MM-DD}.md 2>/dev/null \
  || echo "No report found for {date}. Available reports:" \
  && ls ~/.blogger-radar/reports/*/*.md 2>/dev/null | sort -r | head -10
```

### "Show reports from [month]" (e.g. "show April reports")
```bash
ls ~/.blogger-radar/reports/{YYYY}/{MM}/*.md 2>/dev/null | sort -r
```

### "List all reports" / "Show my archive"
```bash
cat ~/.blogger-radar/reports/README.md 2>/dev/null || echo "No reports archived yet."
```

### "How many reports do I have?"
```bash
ls ~/.blogger-radar/reports/*/*.md 2>/dev/null | wc -l
```

### "Reprocess [date]'s data with a new summary style / different language"
Load the cached raw data and re-run Steps 3-6 without fetching live:
```bash
cat ~/.blogger-radar/cache/{YYYY-MM-DD}.json
```
Then proceed from Step 3 using that JSON as the fetch result. This is useful when changing language, format depth, or summarization style for a past day.

### "Clear old cache" (older than 30 days)
```bash
find ~/.blogger-radar/cache -name "*.json" -mtime +30 -delete && echo "Cache cleared."
```

---

## Embedded Blogger Registry — Top 30 AI Builders

*Curated from Miles Deutscher's Top 50 AI Accounts (Feb 2026), Sophia Hodlberg's ULTIMATE AI Builder List, and Zara Zhang's follow-builders project. Principle: follow builders, not influencers.*

When the user selects option [A] or [B] in onboarding Step 2, load these entries into `config.json → bloggers[]`.

**Column key:** `id | Display Name | tags | note | twitter_handle | github_user [watch_repos] | substack_slug | youtube_channel_id`

Use `—` for omitted fields. For YouTube, `@handle` means you need to look up the `UC...` channel ID from the channel page — use the Atom feed URL once you have it: `https://www.youtube.com/feeds/videos.xml?channel_id={UC...}`.

### Category 1: General Alpha — Core Thought Leaders

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| karpathy | Andrej Karpathy | General-Alpha,Education | AI educator; Neural Networks: Zero to Hero series | @karpathy | karpathy [micrograd,minGPT,nanoGPT,llm.c] | — | UCXUPKJO5MZQMU11wm6N7VqQ |
| sama | Sam Altman | General-Alpha,OpenAI | OpenAI CEO — first signal source for industry direction | @sama | — | — | — |
| ylecun | Yann LeCun | General-Alpha,Research | Meta Chief AI Scientist, Turing Award; critiques LLM hype | @ylecun | — | — | — |
| geoffrey-hinton | Geoffrey Hinton | General-Alpha,Research | Nobel laureate, deep learning pioneer | @geoffreyhinton | — | — | — |
| john-carmack | John Carmack | General-Alpha,Technical | DOOM creator, now pursuing AGI solo; extremely high technical density | @ID_AA_Carmack | — | — | — |

### Category 2: Technical Builders — Framework & Toolchain

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| swyx | Shawn Wang | Technical,Podcast | AI Engineer; co-host of Latent Space; coined "AI Engineer" role | @swyx | swyx | swyx | — |
| simon-willison | Simon Willison | Technical,Tools | Creator of Datasette and llm CLI; prolific blogger on AI tooling | @simonw | simonw | simonwillison | — |
| jason-liu | Jason Liu | Technical,Framework | Creator of Instructor (structured LLM outputs); frequent evals content | @jxnlco | jxnl | jxnl | — |
| jerry-liu | Jerry Liu | Technical,Framework | LlamaIndex co-founder; RAG and agentic workflows | @jerryjliu0 | run-llama [llama_index] | — | — |
| harrison-chase | Harrison Chase | Technical,Framework | LangChain founder; agent orchestration | @hwchase17 | hwchase17 [langchain] | — | — |
| jeremy-howard | Jeremy Howard | Technical,Education | fast.ai co-founder; practical deep learning | @jeremyphoward | fastai [fastai,fastcore] | — | — |
| david-ha | David Ha | Technical,Research | Google Brain researcher; creative AI and world models | @hardmaru | hardmaru | — | — |
| shreya-shankar | Shreya Shankar | Technical,Research | AI Engineering researcher; data-centric AI, LLM evaluation | @sh_reya | shreyashankar | — | — |

### Category 3: AI × Business / Product

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| aaron-levie | Aaron Levie | Business,Enterprise | Box CEO; sharp takes on AI transforming enterprise software | @levie | — | — | — |
| dan-shipper | Dan Shipper | Business,Content | Every CEO; AI × knowledge work and writing; personal AI tools | @danshipper | danshipper | every | — |
| ethan-mollick | Ethan Mollick | Business,Education | Wharton professor; One Useful Thing newsletter; 418K+ subs | @emollick | — | emollick | — |
| peter-yang | Peter Yang | Business,Product | AI × product thinking; creator economy; deep framework posts | @petergyang | — | petergyang | — |
| kevin-weil | Kevin Weil | Business,OpenAI | OpenAI Chief Product Officer; product strategy signals | @kevinweil | — | — | — |

### Category 4: AI × Content / Media

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| matt-wolfe | Matt Wolfe | Content,YouTube | Most-viewed AI tools reviewer; rapid-fire new tool coverage | @mreflow | — | — | @mreflow |
| matthew-berman | Matthew Berman | Content,YouTube | Ultra-fast model releases and benchmark reviews; 530K+ subs | @matthew_berman_ | — | — | @MatthewBerman |
| greg-isenberg | Greg Isenberg | Content,Podcast | Startup Ideas podcast; AI business models and vibe coding | @gregisenberg | — | gregisenberg | @GregIsenberg |
| riley-goodside | Riley Goodside | Content,Prompting | Prompt engineering pioneer; Scale AI staff; jailbreak/edge-case explorations | @goodside | — | — | — |

### Category 5: Vibe Coding & Indie Hackers

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| steipete | Peter Steinberger | IndieHacker,Tools | PSPDFKit founder; prolific OpenClaw skill author; building in public | @steipete | steipete | steipete | — |
| marc-lou | Marc Lou | IndieHacker,SaaS | Ship-fast SaaS builder; ShipFast and multiple profitable micro-SaaS | @marc_louvion | marclou | — | — |
| meng-to | Meng To | IndieHacker,Design | Design+Code creator; AI design tools and courses | @MengTo | MengTo | — | — |
| amjad-massad | Amjad Massad | IndieHacker,Platform | Replit CEO; vibe coding infrastructure; agent-run apps | @amasad | amasad | — | — |
| levelsio | Pieter Levels | IndieHacker,SaaS | Indie Hacker godfather; $5M+ ARR solo; nomadlist, photorealistic AI | @levelsio | levelsio | levelsio | — |

### Category 6: Product Leaders

| id | Name | Tags | Note | Twitter | GitHub | Substack | YouTube |
|---|---|---|---|---|---|---|---|
| guillermo-rauch | Guillermo Rauch | Product,Platform | Vercel CEO; Next.js and AI SDK; DX-first thinking | @rauchg | rauchg [vercel,ai] | — | — |
| garry-tan | Garry Tan | Product,VC | YC President; founder stories and early-stage AI startups | @garrytan | — | — | @GarryTan |
| matt-shumer | Matt Shumer | Product,LLM | Hyperspace CEO; frontier LLM applications; frequent model comparisons | @mattshumer_ | mshumer | — | — |

> **Expansion pack** (uncomment in config to enable): Matt Turck `@mattturck`, Min Choi `@minchoi`, Miles Deutscher `@milesdeutscher`, Aiden Bai `@aidenbai`, Josh Woodward `@joshwoodward`

> **YouTube channel IDs**: For entries marked `@handle` in YouTube column, find the `UC...` channel ID by visiting the channel page, viewing source, and searching for `channel_id`. Then update config.json with the actual ID. The Atom feed `https://www.youtube.com/feeds/videos.xml?channel_id=UC...` requires the full ID.

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

Save the returned job ID to `config.json` under `schedule.cronJobId`.

Always specify `--channel` and `--to` explicitly — never use `--channel last`.

### Verify

```bash
openclaw cron list
openclaw cron run <jobId>
```

Confirm delivery was received before finishing setup.

---

## Required Credentials

**Zero credentials needed for basic operation.** GitHub public API, Substack RSS, and YouTube Atom feed all work without any API keys.

| Variable(s) | Purpose | Required? |
|---|---|---|
| `GITHUB_TOKEN` | Raises GitHub rate limit 60→5000 req/hr | Optional |
| `TWITTER_BEARER_TOKEN` | Official Twitter API v2 (500K reads/month free tier) | Optional |
| `XAI_API_KEY` | `/x-search` skill — highest quality Twitter search | Optional |
| `RSSHUB_BASE_URL` | Xiaohongshu fetching (self-host RSSHub) | Only for Xiaohongshu |
| `SLACK_WEBHOOK_URL` | Slack delivery | Only for Slack |
| `DISCORD_WEBHOOK_URL` | Discord delivery | Only for Discord |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | Telegram delivery | Only for Telegram |
| `FEISHU_WEBHOOK_URL` | Feishu/Lark delivery | Only for Feishu |
| `WECHAT_WEBHOOK_URL` | WeChat Work delivery | Only for WeChat Work |
| `NOTION_TOKEN` + `NOTION_DATABASE_ID` | Notion delivery *(requires Python)* | Only for Notion |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | Email delivery *(requires Python)* | Only for Email |

Store all in `~/.blogger-radar/.env` (never committed to git).

---

## Configuration Management

Handle settings changes conversationally:

- **Add blogger**: "Track Simon Willison" → add to `bloggers[]` in config.json, parse handle/URL for platforms
- **Remove blogger**: "Stop tracking Matt Wolfe" → remove from `bloggers[]`
- **Change schedule**: update `schedule` + cron job
- **Change language**: update `"language"` in config.json
- **Show settings**: read config.json and display clearly
- **View archive**: "show my report archive" → `cat ~/.blogger-radar/reports/README.md`
- **Customize output style**: copy the relevant prompt to `~/.blogger-radar/prompts/` and edit it
  ```bash
  mkdir -p ~/.blogger-radar/prompts
  # Then write your customized version of summarize-blogger.md or report-format.md there
  ```
  To reset a customization, delete the override file. The skill's embedded default is restored automatically.
- **Clear old cache**: "clear cache older than 30 days" → `find ~/.blogger-radar/cache -name "*.json" -mtime +30 -delete`

---

## File Map

```
~/.blogger-radar/              ← user's private data (created on first run)
├── config.json                ← settings and blogger list
├── .env                       ← credentials (optional; only for external delivery)
├── prompts/                   ← optional overrides (copy defaults here to customize)
│   ├── summarize-blogger.md   ← overrides embedded summarization prompt
│   └── report-format.md       ← overrides embedded report format
├── reports/                   ← archived reports (auto-created by Step 6)
│   ├── README.md              ← index of all reports, newest first
│   └── YYYY/MM/YYYY-MM-DD.md  ← one file per day
└── cache/                     ← raw fetch data for reprocessing
    └── YYYY-MM-DD.json        ← per-day raw fetch result

blogger-radar/                 ← skill source directory (read-only at runtime)
├── SKILL.md                   ← this file — all runtime instructions, self-contained
├── examples/
│   └── sample-report.md       ← example output shown to user in onboarding Step 1
├── prompts/                   ← default prompt templates (embedded in SKILL.md above)
│   ├── summarize-blogger.md
│   ├── report-format.md
│   └── translate.md
├── config/
│   └── bloggers.example.yaml  ← full YAML reference (data is embedded in SKILL.md)
└── references/
    ├── platforms.md           ← platform-specific fetch details and rate limits
    └── deploy.md              ← GitHub Actions / system cron / Vercel deployment guide
```

---

## Appendix: Legacy Python Scripts (Optional)

The Python scripts in `scripts/` remain fully functional for scenarios where the agent is not present:

- **Notion and Email delivery** — no clean curl equivalent for Notion's block API or SMTP
- **GitHub Actions** — agent not present; scripts run the full pipeline headlessly
- **Advanced debugging** — `--dry-run` and `--blogger` flags for targeted testing

**Requirements:** Python 3.11+, then:
```bash
pip install httpx python-dotenv lxml
```

**Usage:**
```bash
python {baseDir}/scripts/fetch_all.py --config ~/.blogger-radar/config.json
python {baseDir}/scripts/deliver.py --report /tmp/br-report.txt \
  --config ~/.blogger-radar/config.json --env ~/.blogger-radar/.env
```

**Testing flags:**
```bash
python scripts/fetch_all.py --dry-run                  # see fetched JSON without delivering
python scripts/fetch_all.py --blogger swyx             # single blogger
python scripts/fetch_all.py --platform github          # single platform
python scripts/deliver.py --report /tmp/br-report.txt --dry-run
```

See `references/deploy.md` for GitHub Actions and Vercel deployment configuration.

> The agent-native workflow above (Steps 1–6) supersedes these scripts for all standard Claude Code / OpenClaw use cases.
