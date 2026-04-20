# 📡 博主雷达 (Blogger Radar)

> 每天自动抓取你对标博主的最新动态，Claude AI 分析总结，默认直接在对话中推送。
> **零 Python 依赖，零安装，开箱即用。**

**由 [`billyhetech`](https://github.com/billyhetech) 构建** · AI 应用架构师 · Build in Public

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill_v3-8B5CF6?logo=anthropic&logoColor=white)](https://github.com/topics/openclaw-skill)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-自动运行-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.md) · [中文](#中文文档)

---

## 中文文档

### 它能做什么

博主雷达自动监控你配置的对标博主列表，从多个平台抓取近期内容，生成结构化情报日报——默认直接在对话中展示，也可推送到 Slack、Discord、Telegram、飞书、企业微信、Notion 或邮件。

所有抓取和总结均由 Agent 原生完成，无需安装 Python，无需申请 API Key 即可上手。

每份日报包含：
- **本周亮点** — 具体的重要帖子和动作，附原文链接
- **新工具 & 产品** — 博主提及或发布的新事物
- **内容策略观察** — 内容形式、风格、发布节奏分析
- **互动信号** — 哪类内容最受欢迎
- **趋势判断** — 上升 / 稳定 / 下滑
- **可借鉴选题** — 可以跟进或覆盖的内容角度

### 支持平台

| 平台 | 抓取方式 | 是否需要 Key |
|---|---|---|
| GitHub | 公开 Events API v3 | 不需要（可选 Token，提升限额 60→5000/hr） |
| Substack | RSS Feed | 不需要 |
| YouTube | 免费 Atom Feed（无配额限制） | 不需要 |
| Twitter / X | `/x-search` skill · Nitter RSS 备用 · 官方 API v2 | 不需要（可选，提升质量） |
| 小红书 | RSSHub 桥接 | 需自建 RSSHub — *中文创作者专属* |

### 推送渠道

| 渠道 | 方式 |
|---|---|
| **对话内推送** | 默认 — 零配置，立即可用 |
| **Slack** | Incoming Webhook |
| **Discord** | Webhook |
| **Telegram** | Bot API |
| **飞书 / Lark** | Webhook |
| **企业微信** | 机器人 Webhook |
| **Notion** | 每天创建新 Page *（需要 Python）* |
| **邮件** | SMTP *（需要 Python）* |

### 内置精选 Top 30 博主

博主雷达内置了一份精心策划的 30 位 AI 建造者名单，初次运行即可一键加载：

| 分类 | 博主 |
|---|---|
| 核心思想领袖 | Karpathy、Sam Altman、Yann LeCun、Geoffrey Hinton、John Carmack |
| 技术构建者 | swyx、Simon Willison、Jason Liu、Jerry Liu、Harrison Chase、Jeremy Howard、David Ha、Shreya Shankar |
| AI × 商业产品 | Aaron Levie、Dan Shipper、Ethan Mollick、Peter Yang、Kevin Weil |
| 内容创作者 | Matt Wolfe、Matthew Berman、Greg Isenberg、Riley Goodside |
| 独立开发者 | steipete、Marc Lou、Meng To、Amjad Massad、Pieter Levels |
| 产品领导者 | Guillermo Rauch、Garry Tan、Matt Shumer |

### 快速开始（Agent / OpenClaw）

推荐通过 Claude Code Skill 启动：

```
/blogger-radar
```

Agent 引导你在 2 分钟内完成配置：
1. 选择直接加载内置 Top 30（一键完成）或手动添加博主
2. 选择报告语言（中文 / 英文 / 双语）
3. 设置推送方式：默认对话内推送，外部渠道按需开启
4. 立即生成第一份日报

无需 Python，无需编辑 YAML，无需配置密钥即可基础使用。

### 本地档案存储

每份日报自动保存至：
```
~/.blogger-radar/reports/YYYY/MM/YYYY-MM-DD.md
```

原始抓取数据缓存，支持重新处理：
```
~/.blogger-radar/cache/YYYY-MM-DD.json
```

用自然语言查询历史报告：
- "显示上周二的报告"
- "查看四月份的所有报告"
- "用中文重新处理 4 月 15 日的数据"

### 项目结构

```
SKILL.md                       ← 自包含的 Skill 规范（所有运行时指令）
~/.blogger-radar/
├── config.json                ← 设置和博主列表（由 Agent 创建）
├── .env                       ← 凭证（可选）
├── reports/YYYY/MM/*.md       ← 按天存档的日报
└── cache/YYYY-MM-DD.json      ← 原始抓取数据

scripts/                       ← 旧版 Python 脚本（可选，非必需）
├── fetch_all.py               ← 用于 GitHub Actions / 无 Agent 环境
└── deliver.py                 ← 用于 Notion / 邮件渠道
```

### 手动配置（GitHub Actions / 无头模式）

适用于无 Claude Agent 的部署场景（如 GitHub Actions）：

**第一步：配置对标博主**

```bash
cp config/bloggers.example.yaml config/bloggers.yaml
# 编辑 config/bloggers.yaml，填入你想监控的博主
```

**第二步：配置推送渠道**

```bash
cp config/push.example.yaml config/push.yaml
# 设置 report.language: "zh" 或 "en"（默认英文）
# 按需开启渠道
```

**第三步：配置 GitHub Secrets**

进入仓库 → Settings → Secrets and variables → Actions：

| Secret | 是否必填 | 说明 |
|---|---|---|
| `NOTION_TOKEN` | 开启 Notion 时 | Integration Token |
| `NOTION_DATABASE_ID` | 开启 Notion 时 | 目标数据库 ID |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` | 开启邮件时 | SMTP 凭证 |
| `WECHAT_WEBHOOK_URL` | 开启企业微信时 | 机器人 Webhook |
| `SLACK_WEBHOOK_URL` | 开启 Slack 时 | Incoming Webhook |
| `DISCORD_WEBHOOK_URL` | 开启 Discord 时 | 频道 Webhook |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | 开启 Telegram 时 | Bot 凭证 |
| `TWITTER_BEARER_TOKEN` | 可选 | 官方 API（否则降级到 Nitter RSS） |
| `GITHUB_TOKEN` | 可选 | 提升 API 请求限额 |
| `RSSHUB_BASE_URL` | 可选 | 自建 RSSHub（抓取小红书用） |

> Agent 模式下无需 `ANTHROPIC_API_KEY`——Agent（Claude）本身就是摘要引擎。

**第四步：启用 GitHub Actions**

```bash
cp assets/github-actions-workflow.yml .github/workflows/blogger-radar.yml
git add . && git commit -m "ci: 启用博主雷达自动化" && git push
```

工作流每天 UTC 00:00（北京时间 08:00）自动触发，也可在 Actions 页手动运行。

**第五步：本地测试**

```bash
pip install -r requirements.txt
cp env.example .env && vim .env  # 填入各平台 Key

python scripts/fetch_all.py --dry-run          # 只抓取，不推送
python scripts/fetch_all.py --blogger swyx     # 只处理指定博主
python scripts/fetch_all.py --platform github  # 只抓取指定平台
```

### 添加新博主（对话方式）

直接告诉 Agent：
> "追踪 Simon Willison" 或 "添加 @simonw，Twitter 和 github.com/simonw"

Agent 自动解析输入，更新 `config.json`，下次运行即生效。

### 添加新博主（手动 YAML）

编辑 `config/bloggers.yaml`：

```yaml
- id: blogger-slug             # 唯一标识，英文小写
  name: "博主显示名"
  tags: [AI, RAG]
  note: "监控这个人的原因"
  platforms:
    twitter:
      handle: "@handle"
      enabled: true
    github:
      username: "handle"
      enabled: true
      watch_repos: []           # 空列表=监控全部公开活动
    substack:
      slug: "authorslug"
      enabled: true
    youtube:
      channel_id: "UCxxxxx"    # 从频道页面源码中找 UC 开头的 ID
      enabled: true
    xiaohongshu:
      uid: "xxxxxxxx"
      enabled: false
```

### 小红书注意事项

> 小红书仅适用于追踪**中文内容创作者**，英文 AI 博主可跳过此项。

小红书无公开 API，反爬机制较强。本项目通过 **RSSHub** 桥接，建议自建实例：

```bash
# Vercel 一键部署（推荐）
# Fork https://github.com/DIYgod/RSSHub → 部署到 Vercel

# 或 Docker 本地运行
docker run -d -p 1200:1200 diygod/rsshub
```

部署后设置环境变量 `RSSHUB_BASE_URL`，并在博主配置中开启小红书平台。

### 扩展开发（Python 脚本）

**新增平台**：在 `scripts/fetchers/` 新建 fetcher，实现 `async def fetch(self, days_lookback) -> list[dict]`，在 `fetch_all.py` 的 `FETCHER_REGISTRY` 中注册。

**新增推送渠道**：在 `scripts/pushers/` 新建 pusher，实现 `async def push(self, report) -> bool`，在 `PUSHER_REGISTRY` 中注册。

---

## 智能体平台兼容性

项目内置符合标准规范的 `SKILL.md`（v3），可直接在以下平台作为 Skill 使用：

- **OpenClaw**（推荐——完整 Agent 原生工作流）
- **Claude Code**（claude.ai/code）
- **Claude**（claude.ai Projects）
- 任何支持 SKILL.md 规范的智能体平台

---

## License

MIT · Built with ❤️ by [billyhetech](https://github.com/billyhetech)
