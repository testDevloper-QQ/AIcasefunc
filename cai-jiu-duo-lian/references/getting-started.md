# 安装成功 — 输入示例

> Skill 安装验证通过后，**请将下方四种使用场景的示例返回给用户**，便于开箱即用。

## 四种使用场景

| 场景 | 说明 | 对话输入示例 | CLI 示例（WorkBuddy / Agent） |
|------|------|-------------|------------------------------|
| **1. 场景驱动** | 先定饮食偏好，再出菜 | `轻食，一人食，想吃点清爽的` | `python scripts/recommend_cli.py -s light-meal -i 黄瓜,鸡蛋 --servings 一人食 --pretty` |
| **2. 食材驱动** | 按冰箱现有食材找做法 | `有鸡蛋、番茄、黄瓜，能做什么` | `python scripts/recommend_cli.py -i 鸡蛋,番茄,黄瓜 --pretty` |
| **2b. 自定义食材** | 示例里没有的家乡食材 | `有折耳根和豆花，想吃点家乡味` | `python scripts/recommend_cli.py -s regional -c 折耳根,豆花 --pretty` |
| **3. 指定需求** | 指定便当、菜名或用途 | `想做一份便当，明天带饭，有鸡胸肉和米饭` | `python scripts/recommend_cli.py -s bento -i 米饭,鸡胸肉 --text 明天带饭 --pretty` |
| **4. 默认快乐餐** | 不选场景，快速解馋 | `有鸡蛋和番茄，来道快手的` | `python scripts/recommend_cli.py -i 鸡蛋,番茄 --pretty` |

> **未选场景时**默认按「快乐餐」推荐。若要家乡菜，请在对话中说明「地方味」，或 CLI 加 `-s regional`。

## 安装验证

```bash
python scripts/verify_install.py
```

验证通过后会打印上述示例；Agent 安装 Skill 成功后也应主动展示。

## 网页表单要点

- **自定义食材输入框**：在「冰箱里有什么？」下方独立面板，可只输入折耳根、豆花等（不必点选示例）
- **手绘风推荐卡片**：Hero 叙事插画 + 食材手绘网格 + 步骤叙事小图（见 `references/illustration-style-bible.md`）

## Agent 表单引导（AskQuestion）

网页有 **5 个表单区块**；Agent 侧用 **AskQuestion** 逐轮复现（场景 → 食材多选 → 口味 → 份量 → 补充说明），选项与 `web/index.html` 保持一致。

完整 JSON 模板与 CLI 映射见 [`agent-form-askquestion.md`](agent-form-askquestion.md)。

安装成功后建议话术：

1. 展示上方四种场景示例  
2. 问：「要不要像网页一样点选场景和食材？」  
3. 用户同意 → 按 Q1–Q5 调用 AskQuestion → `recommend_cli.py` → Step 4.6 补图

```bash
python scripts/ensure_web_server.py
# 浏览器打开 http://127.0.0.1:8765/
```

## 场景 ID 对照

| 展示名 | CLI `-s` 参数 |
|--------|---------------|
| 便当 | `bento` |
| 轻食 | `light-meal` |
| 时令 | `seasonal` |
| 地方味 | `regional` |
| 调理 | `health` |
| 快乐餐 | `happy`（默认） |
