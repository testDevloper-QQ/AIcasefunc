# Agent 侧 AI 插画出图（Cursor / WorkBuddy）

> **默认路径**：由宿主 Agent 用**内置出图能力**生成，**不依赖**用户配置 `OPENAI_API_KEY`。  
> Python 脚本只负责：列出任务 → 落盘 → 解析展示。

## 为什么不用 Python 调外部 API？

| 环境 | 出图方式 |
|------|----------|
| **Cursor Agent** | 对话内 `GenerateImage` / 宿主图像工具 |
| **WorkBuddy Agent** | WorkBuddy 内置图像生成工具 |
| **网页 Web 服务** | 读取已落盘的 PNG（Agent 预生成或批量补齐） |
| **Headless 批量（可选）** | `generate_ai_illustrations.py` + `OPENAI_API_KEY` |

Web 服务**无法**直接调用 Cursor 出图；须 Agent 先把图画进 `assets/illustrations/`。

## Agent 标准流程（推荐后补图）

### 1. 推荐菜谱

```bash
python scripts/recommend_cli.py -i 鸡肉 -s seasonal --pretty
```

记下 `primary.id`（如 `sea-014`）。

### 2. 列出缺失插画任务

```bash
python scripts/illustration_jobs_cli.py --from-recommend -i 鸡肉 -s seasonal --pretty
```

或直接指定菜：

```bash
python scripts/illustration_jobs_cli.py --recipe-id sea-014 --pretty
```

返回 JSON `jobs[]`，每项含：

| 字段 | 说明 |
|------|------|
| `prompt` | 交给宿主出图模型的英文 prompt |
| `relPath` / `absPath` | 落盘目标 |
| `maxCandidates` | **最多 3** 张备选 |
| `kind` | `dish`、`step` 或 `ingredient` |

### 3. Agent 出图（宿主内置）

对 `jobs[]` 每一项：

1. 用 **Cursor GenerateImage** 或 **WorkBuddy 图像工具**，按 `prompt` 生成
2. 同一 job 最多生成 `maxCandidates`（≤3）张备选，选最好的一张
3. **禁止**为省事先调 Python `generate_ai_illustrations.py` 除非用户明确要求 headless

### 4. 落盘注册

`save_illustration.py` 会**自动**按 medium 规格缩放并优化 PNG（Hero 1024 / 步骤 768 / 食材 512 px 长边，见 `illustration-style-bible.md`）。

```bash
python scripts/save_illustration.py --recipe-id sea-014 --kind dish --from "生成的图.png" --generator cursor --pretty

python scripts/save_illustration.py --recipe-id ben-054 --kind step --step-index 1 --from "步骤1.png" --generator cursor --pretty

python scripts/save_illustration.py --recipe-id ben-054 --kind ingredient --art-key chicken --from "鸡线稿.png" --generator cursor --pretty
```

### 5. 验证

- 网页 `Ctrl+F5` 重新推荐
- 或 `python scripts/recommend_cli.py ...` 看 `heroIllustrationUrl` 是否指向 `.png`

## SKILL.md 硬规则（Agent 必遵）

- 主推荐返回后，若 `illustration_jobs_cli` 有缺失 job → **Agent 应主动出图并 save**，再告知用户刷新
- 每张图备选 **≤3**
- Hero / 步骤：叙事水彩手账风；**食材**：线稿 + 淡彩（`build_ingredient_prompt`）
- 禁止几何 SVG 拼盘

## 可选：Headless 批量（维护者）

无 Cursor/WorkBuddy 会话、需 CI 批量时：

```powershell
$env:OPENAI_API_KEY = "..."
python scripts/generate_ai_illustrations.py --top 10 --candidates 1
```

见 [`llm-config.md`](llm-config.md) 图像 API 变量。

## 相关脚本

| 脚本 | 用途 |
|------|------|
| `illustration_jobs_cli.py` | 输出待生成 job JSON |
| `save_illustration.py` | Agent 出图后落盘 + 更新 manifest |
| `illustration_resolver.py` | 运行时查 PNG |
| `generate_ai_illustrations.py` | 可选 headless API 批量 |
