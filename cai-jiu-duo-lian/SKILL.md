---
name: cai-jiu-duo-lian
description: |
  菜就多练：场景驱动菜谱推荐。用户不知道吃什么、想按食材/场景/口味找菜时使用。
  从本地7本饮食书籍索引推荐，先定场景再出好菜。默认中文、一人食友好、暖黄治愈风。
argument-hint: "[场景或食材，如：轻食 鸡蛋 番茄]"
version: "1.0.0"
user-invocable: true
---

# 菜就多练

先定场景，再出好菜。从本地饮食资料索引推荐可执行菜谱，不做泛化「今天吃啥」。

## When to use

- 不知道吃什么、想快速出菜
- 有现有食材想找做法
- 按场景：便当 / 轻食 / 时令 / 地方味 / 调理 / 快乐餐

触发示例：

- 「轻食，有黄瓜和鸡蛋，一人食」
- 「今天立春吃什么」
- 「想做川渝口味的下饭菜，二人」
- 「上班族带饭，烤箱快速出餐」

## Read these references when needed

- [`references/scene-router.md`](references/scene-router.md) — 场景路由与反向过滤
- [`references/style-guide.md`](references/style-guide.md) — 语气与禁止事项
- [`references/output-template.md`](references/output-template.md) — 输出格式
- [`references/knowledge-sources.md`](references/knowledge-sources.md) — 书籍路径与读取顺序

## Core workflow

### Step 1: Detect mode

| 模式 | 触发 |
|------|------|
| `ingredient` | 用户列出多个食材 |
| `specific` | 指定菜名、技法或器具（烤箱、便当） |
| `craving` | 仅描述场景、心情、时令、场合 |

### Step 2: Route scene → 选书与索引

读 [`references/scene-router.md`](references/scene-router.md)，映射到 `data/recipe-index/` 中对应 yaml：

- `bento.yaml` — 便当、带饭、烤箱懒人
- `light-meal.yaml` — 轻食、沙拉、抗炎
- `seasonal.yaml` — 时令、节气
- `regional.yaml` — 地方菜、地域风味
- `health.yaml` — 备孕、孕期、日常调理（加免责声明）
- `happy.yaml` — 快乐餐、小吃、甜点、饮品

索引未命中 → 按 `knowledge-sources.md` 顺序读原文：`.md` → `.pdf` → `.docx` → `.epub`

### Step 3: Clarify（最多 2 问）

1. 几人食？（一人食 / 二人家庭 / 多人家庭）
2. 有无禁忌或硬性约束？

规则：用户已回答或表单 Prompt 已含信息 → 不再重复问；请求极具体 → 直接推荐。

### Step 4: Recommend

1. 先查 `data/recipe-index/*.yaml`（按 scene、tags、食材名过滤）
2. 命中后校验：不捏造、份量匹配、方向与用户场景一致
3. 优先 1 道强推荐；接近时可附 0–2 备选
4. 按用户份量缩放食材

### Step 5: Output

严格按 [`references/output-template.md`](references/output-template.md) 输出。

图片策略：

1. 优先索引中 `line_art` 路径（`assets/line-art/`）
2. 有网络时可按菜名搜公开图片
3. 失败则无图，不阻塞推荐

## Structured guidance（对话内引导）

若用户未提供足够信息，用简短卡片引导（一次只问一类）：

**今天想吃什么？（可选）**：便当 · 轻食 · 时令 · 地方味 · 调理 · 快乐餐

**食材（至少 1 个）**：请用户点选或打字

可选：口味、份量

## Hard rules

- **不捏造菜品**：须能在索引 `source` 或本地书籍原文中找到依据
- **不反向推荐**：轻食场景不重油炸；health 场景不加酒精/高风险食材
- **份量匹配**：不一人食推 2 人量
- **非专业建议**：health 场景末尾加「仅供参考，非医疗建议」
- **v1 不含**：拍照识材、小红书补充（v2）

## Tone

参考 [`references/style-guide.md`](references/style-guide.md)：清新、治愈、有书卷气；像会做饭的朋友，避免网红腔。

## Optional web form

用户可使用 `web/index.html` 静态表单生成结构化 Prompt，复制到对话中使用。
