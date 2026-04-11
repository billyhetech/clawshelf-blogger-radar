# Prompt: Translation Guidelines

Use this prompt when the user's `language` config is `"zh"` or `"bilingual"`.

## For language: "zh" (Chinese only)

Translate the entire report into natural, fluent Simplified Chinese.

Rules:
- Keep proper nouns in their original form: Twitter/X, GitHub, Substack, YouTube, Xiaohongshu
- Keep URLs as-is — do not translate link text that is already a URL
- Tech terms with no standard Chinese equivalent should be kept in English or written as
  "英文原词（中文解释）", e.g. "RAG（检索增强生成）"
- Section headers should use the Chinese labels from `report-format.md`
- Maintain the same structure and bullet layout as the English version
- Tone: professional but conversational, like a smart analyst briefing a colleague

## For language: "bilingual" (English + Chinese side by side)

Rules:
- Follow the interleaving pattern described in `report-format.md`
- For each section within a blogger entry:
  1. Output the English version
  2. Immediately follow with the Chinese version of the same section
  3. Then move to the next section
- The report header and footer appear once, in English only
- URLs appear in both the English and Chinese versions (copy them, don't omit)
- Chinese translations should be natural, not mechanical — prioritize meaning over literal accuracy

## What NOT to translate

- Blogger names and handles (e.g. "@swyx", "Simon Willison")
- Platform names (Twitter/X, GitHub, Substack, Xiaohongshu, YouTube)
- Code snippets, repo names, model names (GPT-4o, Claude 3.5, LlamaIndex)
- URLs and links
- Emojis and section icons
