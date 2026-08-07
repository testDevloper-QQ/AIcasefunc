---
name: cai-jiu-duo-lian
description: |
  菜就多练：场景驱动菜谱推荐。用户不知道吃什么、想按食材/场景/口味找菜时使用。
  从预建索引推荐可执行菜谱；中国计量、膳食指南份量、≤60分钟、默认快乐餐。
  支持网页在线推荐与 Git 远程 Skill。暖黄手账风 + 叙事插画（Plan B）。
argument-hint: "[场景或食材，如：轻食 鸡蛋 番茄]"
version: "1.10.4"
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

**表单式引导（推荐）**：用户未一次性说清条件时，用 **AskQuestion** 复现网页 5 个区块（场景 / 食材 / 口味 / 份量 / 补充说明），详见 [`references/agent-form-askquestion.md`](references/agent-form-askquestion.md)。安装成功后可先展示下方示例，再问「要不要像网页一样点选？」。

## When to use

- 不知道吃什么、想快速出菜
- 有现有食材想找做法（含自定义食材）
- 按场景：便当 / 轻食 / 时令 / 地方味 / 调理 / 快乐餐

触发示例：

- 「轻食，有黄瓜和鸡蛋，一人食」
- 「有番茄和鸡蛋，来道快手的」（未选场景 → 快乐餐）
- 「想做川渝口味的下饭菜，二人」（需说明或选地方味）

## Read these references when needed

- [`references/workbuddy-output-guide.md`](references/workbuddy-output-guide.md) — **WorkBuddy 内联出图（必遵，非侧边栏）**
- [`references/capabilities.md`](references/capabilities.md) — 能力清单与版本
- [`references/agent-illustration-guide.md`](references/agent-illustration-guide.md) — **Agent 内置出图（Cursor/WorkBuddy，必遵）**
- [`references/illustration-style-bible.md`](references/illustration-style-bible.md) — 手账叙事插画风格（Plan B）
- [`references/line-art-guide.md`](references/line-art-guide.md) — 三层配图总览与解析机制
- [`references/ingredient-art-guide.md`](references/ingredient-art-guide.md) — 食材单项手绘
- [`references/step-layout-guide.md`](references/step-layout-guide.md) — 做法步骤排版
- [`references/scene-router.md`](references/scene-router.md) — 场景路由
- [`references/recommend-engine-guide.md`](references/recommend-engine-guide.md) — 食材匹配与推荐规则
- [`references/measurement-cn.md`](references/measurement-cn.md) — **中国计量规范（必遵）**
- [`references/dietary-guidelines-cn.md`](references/dietary-guidelines-cn.md) — 份量换算与 QA
- [`references/output-template.md`](references/output-template.md) — 输出格式与 QA 清单
- [`references/extension-checklist.md`](references/extension-checklist.md) — **扩展与发布前检查清单（必遵）**
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

### Step 3: 收集条件（AskQuestion 或自然语言）

**优先**用 AskQuestion 对齐网页表单（见 [`agent-form-askquestion.md`](references/agent-form-askquestion.md)）：

| 轮次 | 网页区块 | 说明 |
|------|----------|------|
| Q1 | 今天想吃什么？ | 场景，单选，可不选（默认快乐餐） |
| Q2 | 冰箱里有什么？ | 食材，**多选至少 1 项**；含「自定义」时须再拿具体名称 → `-c` |
| Q3 | 口味偏好 | 可选 |
| Q4 | 几人吃？ | 可选 |
| Q5 | 还有别的要求？ | 可选，映射 `--text` |

**规则**：

- 用户首句已说明的项（如「轻食，有鸡蛋番茄」）→ **跳过**对应 AskQuestion，勿重复问。
- 信息不足（尤其缺食材）→ **必问** Q2；可连问 Q1–Q5。
- Skill 刚安装且用户只说「帮我推荐」→ 展示 getting-started 示例后，提议跑 AskQuestion 表单引导。
- 全部收集完 → 映射 `recommend_cli.py` 参数，进入 Step 4。

传统澄清（不用 AskQuestion 时）：最多自由追问 2 问（几人食？禁忌？），已足够则直接 Step 4。

### Step 4: Recommend

**Agent / WorkBuddy 调用（推荐，无需 Web 服务）：**

在 Skill 根目录执行：

```bash
python scripts/recommend_cli.py --ingredients 鸡蛋,番茄 --scene happy --servings 一人食 --pretty
```

返回 JSON，含 `primary`、`alternates`、`why`。远程安装后同样可用；Python 须在 PATH 中，或设置 `CAIJIU_PYTHON`。

1. 查索引（scene、tags、食材）
2. **仅推荐 ≤ 60 分钟**（备料+烹饪）
3. **中国计量**：华氏/盎司/cup/茶匙/汤匙 须转为 ℃/克/毫升（见 measurement-cn.md）
4. **步骤展示**：仅保留有实际操作的做法步骤；**禁止**营养说明（卡路里/维生素等）与「即可享用」类冗余句
5. **参考书籍优先**：用户 free_text 提到书名/参考资料时，优先推荐 `source.book` 匹配的菜谱（含翻译引进西书）；**不因书籍来源降权**
6. **厨房语境**：步骤文案、插画 prompt 保持中文家庭厨房（℃/克/毫升），与书籍国籍无关
7. **家庭份量**：批量配方按 dietary-guidelines-cn.md 换算
8. 1 道主推荐 + 0–2 备选

### Step 4.5: 输出质量检查（必做）

- 时间 ≤ 60 分钟
- 单位为中国习惯（无华氏、盎司、cup、teaspoon/tablespoon 残留）
- 做法步骤无营养表、无「即可享用」等空步骤
- **不输出**唠唠叨叨 / qualityNotes 区块
- 份量符合膳食指南单餐区间
- 批量配方已换算并标注
- **插画**：Hero 为菜品叙事插画；每步为动作叙事插画；食材均有 `artUrl`（见 illustration-style-bible.md）

### Step 4.6: Agent 侧补全插画（Cursor / WorkBuddy，必做）

**目标**：向用户返回带 **成品图 + 食材图 + 步骤图** 的完整菜谱。插画 URL 只来自 `assets/illustrations/` 已有 PNG；Web 服务不能实时出图，须 Agent 先落盘。

**须用宿主 Agent 内置出图**，不要用 Python 调用户 `OPENAI_API_KEY`（除非用户明确要求 headless 批量）。

#### 4.6.1 首次 recommend（Step 4 已执行）

```bash
python scripts/recommend_cli.py -i 鸡蛋,番茄 -s happy --servings 一人食 --pretty
```

记下 `primary.id`（如 `ben-054`）。此时 JSON 可能已有部分 `heroIllustrationUrl` / `artUrl` / `stepIllustrationUrl`（素材库预载命中），**也可能为空**——**不要**用这次结果做 Step 5 最终输出（若仍有缺失）。

#### 4.6.2 列出缺失任务（参数须与 Step 4 一致）

```bash
python scripts/illustration_jobs_cli.py --from-recommend -i 鸡蛋,番茄 -s happy --pretty
# 或已知 recipe-id：
python scripts/illustration_jobs_cli.py --recipe-id ben-054 --pretty
```

- `jobCount === 0`：素材库已齐全 → **跳过 4.6.3–4.6.4**，直接用 Step 4 的 JSON 进入 Step 5。
- `jobCount > 0`：继续 4.6.3；**已存在的 PNG 不会重复生成**（食材 artKey、同名成品会去重）。

#### 4.6.3 出图并落盘（仅当 jobCount > 0）

对 `jobs[]` 每一项（建议顺序：**食材 → 成品 → 步骤 1、2、3…**）：

1. **Cursor**：GenerateImage / 宿主图像工具，按 `prompt` 出图  
   **WorkBuddy**：内置图像生成工具  
   每张图最多 **3** 张备选，选最好的一张
2. 落盘：

```bash
# 食材（全库复用 artKey）
python scripts/save_illustration.py --kind ingredient --art-key salt --from 路径.png --generator cursor

# 成品（同名菜可共用 shared）
python scripts/save_illustration.py --recipe-id ben-054 --kind dish --from 路径.png --generator cursor

# 步骤（每菜独立，step-index 从 1 起）
python scripts/save_illustration.py --recipe-id ben-054 --kind step --step-index 1 --from 路径.png --generator cursor
```

**全部 job 落盘完成前，不得进入 Step 5 向用户展示「待出图」占位。**

#### 4.6.4 必须再 recommend 一次（jobCount > 0 时硬规则）

补图落盘后，**必须用与 Step 4 相同参数再跑 recommend**，让 `illustration_resolver` 重新挂载 URL：

```bash
python scripts/recommend_cli.py -i 鸡蛋,番茄 -s happy --servings 一人食 --pretty
```

- **Step 5 只使用这一次**（第二次）返回的 JSON。
- 确认 `primary.heroIllustrationUrl`、每条 `ingredients[].artUrl`、每条 `steps[].stepIllustrationUrl` 均已指向 `/skill-assets/.../*.png`。
- **网页用户**：告知刷新页面（`Ctrl+F5`）或重新提交表单；Web 与 CLI 共用同一 resolver，落盘即生效。

| 阶段 | 做什么 | 能否作为最终输出 |
|------|--------|------------------|
| 第一次 recommend | 定菜 + 查已有素材 | ❌ 若有缺失 |
| illustration_jobs | 列缺失 job | — |
| GenerateImage + save | 写 PNG 进 assets | — |
| **第二次 recommend** | 重新解析 URL | ✅ **必须** |

详见 [`references/agent-illustration-guide.md`](references/agent-illustration-guide.md)。

### Step 5: Output

严格按 [`references/output-template.md`](references/output-template.md)。

#### WorkBuddy / Cursor 对话（必遵，与 Web 不同）

见 [`references/workbuddy-output-guide.md`](references/workbuddy-output-guide.md)：

1. **禁止**只把 PNG 附在侧边栏；**必须**在回复正文用 `![描述](路径)` **内联嵌入**。
2. **成品图**放在食材清单**上方**；**每步做法**在步骤文字**上方**放步骤图。
3. **`/skill-assets/` 相对 URL 在 WorkBuddy 无效** → 用 PNG **绝对路径**，或 `--image-mode http`（须先启动 Web）。
4. **`alternates[]` 备选 2 道菜**：每道须完整输出 Hero + 食材 + 步骤（不能只写菜名）。

**推荐**：Step 4.6 完成后执行（参数与 recommend 一致）：

```bash
python scripts/format_chat_output_cli.py -i 鸡,酸奶 -s happy --servings 二人家庭
```

将 CLI 输出的 Markdown **作为最终用户可见回复**（或同等结构手写）。

**对话输出视觉要求**（与网页一致的精神）：

1. **Hero**：菜名醒目；出处/时长/方式/份量/花费；**整道菜成品叙事插画**（非空盘拼 icon）
2. **食材区**（见 ingredient-art-guide.md）：「食材（N 人份）」标签 + 每项 **独立手绘** + 份量
3. **步骤区**（见 step-layout-guide.md）：
   - 区块标题「**做法**」（黑色不规则标签）
   - 每步 **左图右文**：左侧 **动作叙事小插画**（腌制/煮粥/翻炒…）；右侧 **①②③ 圈号** + 手写体步骤 + **淡黄荧光笔底纹**
   - 插图高度随步骤文字长度伸缩（短/中/长三档）
   - **不含**营养说明步骤、冗余「即可享用」步骤、唠唠叨叨区块

插画解析：`illustration_resolver.py` → `assets/illustrations/`。详见 [`line-art-guide.md`](references/line-art-guide.md)。

## 网页表单（含自定义食材）

- 「冰箱里有什么？」：点选示例 **或** 在 **自定义食材** 面板输入，至少 1 项
- 启动：`python scripts/ensure_web_server.py` → `http://127.0.0.1:8765/`

## Hard rules

- **中国计量**：禁止输出未换算的英美单位（见 measurement-cn.md）
- **不捏造**、**不反向推荐**、**份量匹配**、**时长 ≤ 60min**
- **食材对应**：用户选了食材时，推荐菜必须包含这些食材（含同义词）；索引无匹配时走 **网络搜索 + 大模型** 生成家常菜谱
- **Agent 表单**：信息不足时用 AskQuestion 对齐网页 5 区块，见 `agent-form-askquestion.md`
- **插画（Plan B）**：Hero / 步骤走 PNG 资产库；落盘自动 **medium** 规格（Hero 1024 / 步骤 768 / 食材 512 px 长边）；**Agent 用宿主内置出图**，见 `agent-illustration-guide.md`
- **扩展变更**：新场景/新食材/新 UI 须走 [`extension-checklist.md`](references/extension-checklist.md)，并跑 `validate_illustration_coverage.py`
- **素材库预生成**：按书籍维护插画，见 [`illustration-library-guide.md`](references/illustration-library-guide.md)
- **v1 不含**：拍照识材、小红书

## 网页服务

**Agent 侧不依赖 Web 服务**；用户要可视化表单时再启动。

```bash
python scripts/ensure_web_server.py
python scripts/ensure_web_server.py --foreground
python scripts/ensure_web_server.py --foreground --lan
```

默认绑定 `127.0.0.1:8765`；`--lan` 或 `CAIJIU_WEB_HOST=0.0.0.0` 允许局域网访问。

- 表单 → `POST /api/recommend` → 手账风推荐卡片（叙事插画）
- Skill 来源：`web/config.json`
- 详见 [`README.md`](README.md)

## Tone

参考 style-guide.md：清新、治愈、有书卷气；避免网红腔。
