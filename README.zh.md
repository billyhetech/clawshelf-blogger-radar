# 📡 博主雷达 (Blogger Radar)

> 每天早上 8 点，自动抓取你对标博主的最新动态，Claude AI 分析总结，推送到 Notion / 邮件 / 企业微信。

**由 [`billyhetech`](https://github.com/billyhetech) 构建** · AI 应用架构师 · Build in Public

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-自动运行-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Claude API](https://img.shields.io/badge/驱动引擎-Claude_API-D97706?logo=anthropic&logoColor=white)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.md) · [中文](#中文文档)

---

## 中文文档

### 它能做什么

博主雷达自动监控你配置的对标博主列表，从多个平台抓取其过去 7 天的内容，并在每天早上 8 点（北京时间）生成结构化日报推送给你。

每份日报包含：
- **本周亮点** — 关键内容主题和值得注意的帖子
- **新工具 & 产品** — 博主提及的新事物
- **内容策略观察** — 他们的内容打法分析
- **💡 可借鉴选题方向** — 基于竞品空白挖掘的选题机会（专为 billyhetech 定制）

### 支持平台

| 平台 | 抓取方式 | 是否需要 Key |
|---|---|---|
| Twitter / X | 官方 API v2 · Nitter RSS 备用 | Bearer Token（可选） |
| YouTube | Data API v3 | API Key（可选） |
| Substack | RSS Feed | 无需 |
| GitHub | REST API v3 | Token（可选，提升限额） |
| Xiaohongshu | RSSHub 桥接 | 自建 RSSHub（可选）— *中文创作者专属* |

### 推送渠道

| 渠道 | 方式 |
|---|---|
| **Notion** | 每天创建新 Page |
| **邮件** | SMTP（Gmail / Resend / 任意服务商） |
| **企业微信** | 机器人 Webhook |

### 系统架构

```
run_radar.py
├── fetchers/          ← 每个平台一个 fetcher
│   ├── twitter_fetcher.py
│   ├── xiaohongshu_fetcher.py
│   ├── youtube_fetcher.py
│   ├── substack_fetcher.py
│   └── github_fetcher.py
├── summarizer.py      ← 调用 Claude API 分析
└── pushers/           ← 每个推送渠道一个 pusher
    ├── notion_pusher.py
    ├── email_pusher.py
    └── wechat_pusher.py
```

### 快速开始

**第一步：配置对标博主**

```bash
cp config/bloggers.example.yaml config/bloggers.yaml
# 编辑 config/bloggers.yaml，填入你想监控的博主
```

**第二步：配置推送渠道 & 语言偏好**

```bash
cp config/push.example.yaml config/push.yaml
# 设置 report.language: "zh" 或 "en"（默认英文）
# 按需开启 Notion、Email、WeChat 渠道
```

**第三步：配置 GitHub Secrets**

进入仓库 → Settings → Secrets and variables → Actions，添加以下密钥：

| Secret | 是否必填 | 说明 |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ 必填 | Claude API Key |
| `NOTION_TOKEN` | 开启 Notion 时 | Integration Token |
| `NOTION_DATABASE_ID` | 开启 Notion 时 | 目标数据库 ID |
| `SMTP_HOST` | 开启邮件时 | 如 smtp.gmail.com |
| `SMTP_USER` | 开启邮件时 | 发件邮箱 |
| `SMTP_PASS` | 开启邮件时 | 应用专用密码 |
| `WECHAT_WEBHOOK_URL` | 开启微信时 | 企业微信机器人 Webhook |
| `TWITTER_BEARER_TOKEN` | 可选 | 官方 API（否则降级到 Nitter） |
| `YOUTUBE_API_KEY` | 可选 | YouTube Data API v3 |
| `GITHUB_TOKEN` | 可选 | 提升 API 请求限额 |
| `RSSHUB_BASE_URL` | 可选 | 自建 RSSHub（抓取小红书用） |

**第四步：启用 GitHub Actions**

```bash
cp assets/github-actions-workflow.yml .github/workflows/blogger-radar.yml
git add . && git commit -m "ci: 启用博主雷达自动化" && git push
```

工作流每天 UTC 00:00（北京时间 08:00）自动触发，也可在 Actions 页手动运行。

**第五步：本地测试**

```bash
pip install -r requirements.txt
cp env.example .env     # 填入各平台 Key
export $(cat .env | xargs)

python scripts/run_radar.py --dry-run          # 只生成报告，不推送
python scripts/run_radar.py --blogger swyx     # 只处理指定博主
python scripts/run_radar.py --platform github  # 只抓取指定平台
```

### 添加新博主

编辑 `config/bloggers.yaml`，添加一条记录：

```yaml
- id: blogger-slug           # 唯一标识，用英文小写
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
      watch_repos: ["repo-name"]   # 空列表=监控全部活动
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

### 扩展开发

**新增平台**：在 `scripts/fetchers/` 新建 fetcher 文件，实现 `async def fetch(self, days_lookback) -> list[dict]`，在 `run_radar.py` 的 `FETCHER_REGISTRY` 中注册。

**新增推送渠道**：在 `scripts/pushers/` 新建 pusher 文件，实现 `async def push(self, report) -> bool`，在 `PUSHER_REGISTRY` 中注册。

### 小红书注意事项

> 小红书平台仅适用于追踪**中文内容创作者**。如果你主要追踪英文 AI 创作者，可跳过此部分。

小红书没有公开 API，反爬机制较强。本项目通过 **RSSHub** 桥接，建议自建实例：

```bash
# Vercel 一键部署（推荐）
# Fork https://github.com/DIYgod/RSSHub → 部署到 Vercel

# 或 Docker 本地测试
docker run -d -p 1200:1200 diygod/rsshub
```

部署后设置 `RSSHUB_BASE_URL` 环境变量，并在博主配置中开启小红书。

---

## 智能体平台兼容性

项目内置符合标准规范的 `SKILL.md`，可直接在以下平台作为 Skill 使用：

- **Claude**（claude.ai Projects）
- **OpenClaw**
- **OpenCode**
- 任何支持 SKILL.md 规范的智能体平台

---

## License

MIT · Built with ❤️ by [billyhetech](https://github.com/billyhetech)
