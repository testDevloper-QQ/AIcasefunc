---
name: cai-jiu-duo-lian
description: |
  菜就多练：场景驱动菜谱推荐。用户不知道吃什么、想按食材/场景/口味找菜时使用。
  从预建索引推荐可执行菜谱；中国计量、膳食指南份量、≤60分钟、默认快乐餐。
  支持网页在线推荐与 Git 远程 Skill。暖黄手绘线稿风。
argument-hint: "[场景或食材，如：轻食 鸡蛋 番茄]"
version: "1.3.0"
user-invocable: true
---

# 菜就多练

先定场景，再出好菜。从饮食资料索引推荐可执行菜谱，不做泛化「今天吃啥」。

能力清单见 [`references/capabilities.md`](references/capabilities.md)。

## 安装成功后（必做）

用户安装 Skill 成功后，**须返回四种使用场景的输入示例**（见 [`references/getting-started.md`](references/getting-started.md)）：

| 场景 | 对话示例 |
|------|----------|
| **1. 场景驱动** | `轻食，一人食，想吃点清爽的` |
| **2. 食材驱动** | `有鸡蛋、番茄、黄瓜，能做什么` |
| **2b. 自定义食材** | `有折耳根和豆花，想吃点家乡味`（网页表单可只输入自定义食材） |
| **3. 指定需求** | `想做一份便当，明天带饭，有鸡胸肉和米饭` |
| **4. 默认快乐餐** | `有鸡蛋和番茄，来道快手的` |

验证安装：`python scripts/verify_install.py`（会打印完整示例含 CLI 命令）。

## When to use

- 不知道吃什么、想快速出菜
- 有现有食材想找做法（含自定义食材）
- 按场景：便当 / 轻食 / 时令 / 地方味 / 调理 / 快乐餐

触发示例：

- 「轻食，有黄瓜和鸡蛋，一人食」
- 「有番茄和鸡蛋，来道快手的」（未选场景 → 快乐餐）
- 「想做川渝口味的下饭菜，二人」（需说明或选地方味）

## Read these references when needed

- [`references/getting-started.md`](references/getting-started.md) — **安装成功后的四种输入示例**
- [`references/capabilities.md`](references/capabilities.md) — 能力清单与版本
- [`references/scene-router.md`](references/scene-router.md) — 场景路由
- [`references/measurement-cn.md`](references/measurement-cn.md) — **中国计量规范（必遵）**
- [`references/dietary-guidelines-cn.md`](references/dietary-guidelines-cn.md) — 份量换算与 QA
- [`references/output-template.md`](references/output-template.md) — 输出格式与 QA 清单
- [`references/line-art-guide.md`](references/line-art-guide.md) — **手绘风配图规范（Hero/食材/步骤，必遵）**
- [`references/style-guide.md`](references/style-guide.md) — 语气与网页视觉
- [`references/doc-maintenance.md`](references/doc-maintenance.md) — 文档维护分工
- [`references/knowledge-sources.md`](references/knowledge-sources.md) — 书籍路径

## Core workflow

### Step 1: Detect mode

| 模式 | 触发 |
|------|------|
| `ingredient` | 用户列出多个食材 |
| `specific` | 指定菜名、技法或器具 |
| `craving` | 仅描述场景、心情、时令 |

**默认场景**：用户未指定饮食偏好 → **快乐餐**（`happy`）；仅当用户点选或明说「地方味」时优先 `regional`。

### Step 2: Route scene → 索引

映射到 `data/recipe-index/*.yaml`（见 scene-router.md）。未命中再读 `参考书籍/` 原文。

### Step 3: Clarify（最多 2 问）

几人食？有无禁忌？已足够则直接推荐。

### Step 4: Recommend

**Agent / WorkBuddy 调用（推荐，无需 Web 服务）：**

在 Skill 根目录执行：

```bash
python scripts/recommend_cli.py --ingredients 鸡蛋,番茄 --scene happy --servings 一人食 --pretty
```

返回 JSON，含 `primary`、`alternates`、`why`。远程安装后同样可用；Python 须在 PATH 中，或设置 `CAIJIU_PYTHON`。

1. 查索引（scene、tags、食材）
2. **仅推荐 ≤ 60 分钟**（备料+烹饪）
3. **中国计量**：华氏/盎司/cup 须转为 ℃/克/毫升（见 measurement-cn.md）
4. **家庭份量**：批量配方按 dietary-guidelines-cn.md 换算
5. 1 道主推荐 + 0–2 备选

### Step 4.5: 输出质量检查（必做）

- 时间 ≤ 60 分钟
- 单位为中国习惯（无华氏、盎司、cup 残留）
- 份量符合膳食指南单餐区间
- 批量配方已换算并标注
- 含出餐示意与步骤配图描述（对话）或等价视觉（网页）

### Step 5: Output

严格按 [`references/output-template.md`](references/output-template.md)。

**对话输出视觉要求**（与网页一致的精神）：

1. **Hero**：菜名醒目；出处/时长/方式/份量/花费；**出餐手绘线稿**（`line_art` 或主食材线稿）
2. **食材区**：每项「名称 + 中文份量 + 食材线稿」
3. **步骤区**：每步「容器场景（烤/锅/炒/碗/砧/盘）+ 涉及食材线稿 + 中文步骤」

图片优先级：`assets/line-art/` → 联网公开图 → 无图（不阻塞）。详见 [`line-art-guide.md`](references/line-art-guide.md)。

## 网页表单（含自定义食材）

- 「冰箱里有什么？」：点选示例 **或** 在 **自定义食材** 面板输入（折耳根、豆花等），至少 1 项
- 启动：`python scripts/ensure_web_server.py` → `http://127.0.0.1:8765/`

## Hard rules

- **中国计量**：禁止输出未换算的英美单位（见 measurement-cn.md）
- **不捏造**、**不反向推荐**、**份量匹配**、**时长 ≤ 60min**
- **食材对应**：用户选了食材时，推荐菜必须包含这些食材；索引无匹配时走 **AI 家常菜**（`home_cooking_fallback.py`），禁止推食材无关的菜
- **health 场景**加「仅供参考，非医疗建议」
- **v1 不含**：拍照识材、小红书、LLM 编造菜谱

## 网页服务

**Agent 侧不依赖 Web 服务**；用户要可视化表单时再启动。

```bash
# 自动确保服务运行（未启动则后台拉起）
python scripts/ensure_web_server.py

# 前台启动（本机）
python scripts/ensure_web_server.py --foreground

# 局域网 / 手机访问
python scripts/ensure_web_server.py --foreground --lan
# Windows: .\scripts\start_web.ps1 -Lan
```

默认绑定 `127.0.0.1:8765`；`--lan` 或 `CAIJIU_WEB_HOST=0.0.0.0` 允许局域网访问。

- 表单 → `POST /api/recommend` → 手账风推荐卡片
- Skill 来源：`web/config.json`（远程安装默认 `local`）
- 详见 [`README.md`](README.md)

## Tone

参考 style-guide.md：清新、治愈、有书卷气；避免网红腔。
