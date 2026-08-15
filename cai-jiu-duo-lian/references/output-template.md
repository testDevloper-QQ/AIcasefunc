# 输出模板

## 标准格式

```
🍳 推荐：[菜名]
📖 出处：《[书名]》· [场景标签]
⏱ [烹饪时间] · 💰 [预计花费] · 🔥 [烹饪方式] · 👤 [N] 人份

[Hero：整道菜成品叙事插画说明 / heroIllustrationUrl]

🥬 食材（[N] 人份，中国计量）
· [食材名] [份量] — 手绘（如：水芹叶茎、白虾、糖罐…）
…

👩‍🍳 做法
① [动作叙事插画：腌制 / 煮粥 / 翻炒…]
   步骤文字（荧光笔底纹体感）
② …

💡 唠唠叨叨
- [关键提示]

🔄 替代方案
- …
```

## 输出质量检查（必做）

| 检查项 | 标准 |
|--------|------|
| 烹饪时间 | ≤ 60 分钟 |
| 中国计量 | 无华氏、盎司、cup |
| 膳食份量 | 见 `dietary-guidelines-cn.md` |
| **食材对应** | 用户所选食材均在主推荐中出现（同义词算） |
| Hero | **菜品叙事插画**（专属或品类模板），非空盘拼 icon |
| 食材 | 每项有 `artUrl`（`/skill-assets/` URL） |
| 步骤配图 | 每步有 `stepIllustrationUrl` 叙事插画 |
| 步骤排版 | 见 `step-layout-guide.md` |

## API 字段（POST /api/recommend → primary）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 菜名 |
| `source.book` | string | 出处 |
| `cookTimeDisplay` | string | 中文时长 |
| `method` | string | 烹饪方式 |
| `servings` | number | 人份 |
| `cost` | string | 花费 |
| `heroIllustrationUrl` | string | **主** Hero 叙事插画 URL |
| `heroIllustrationSource` | string? | `dish` \| `category` |
| `heroCompositeUrl` | string? | 兼容，同 heroIllustrationUrl |
| `lineArtUrl` / `heroImageUrl` | string? | 兼容 |
| `ingredients[]` | array | `{ name, amount, artUrl }` |
| `steps[]` | array | 见下表 |
| `qualityNotes` | array? | QA 提示 |
| `disclaimer` | string? | 唠唠叨叨 / 免责 |
| `why` | string | 推荐理由 |
| `usedFallback` | boolean | 是否 AI/模板生成 |

## step 对象

| 字段 | 说明 |
|------|------|
| `sceneId` | 叙事场景 ID（如 `pot_porridge_simmer`） |
| `stepIllustrationUrl` | **主** 步骤叙事插画 URL |
| `stepArtUrl` | 兼容，同 stepIllustrationUrl |
| `scene` | legacy 容器名（oven/pot/wok…） |
| `sceneUrl` | legacy 容器 SVG（降级） |
| `ingredientArts` | legacy 食材列表（降级） |

## 维护

字段变更时同步：`illustration_resolver.py`、`recipe_format.py`、`recommend_engine.py`、`web/app.js`、[`extension-checklist.md`](extension-checklist.md) §E。

## WorkBuddy / 对话宿主（非 Web）

- **WorkBuddy 对话**：文案 + `present_files`（默认 `--markdown` = `--image-mode present`）
- **WorkBuddy HTML 预览**：`--export-html`（base64 自包含，防跨端口破损图）
- **Cursor 等**：`--markdown --image-mode path` 或 `http`
- 详见 [`workbuddy-output-guide.md`](workbuddy-output-guide.md)
- 生成器：`python scripts/recommend_cli.py … --markdown` 或 `--export-html`（参数须与用户输入一致）
