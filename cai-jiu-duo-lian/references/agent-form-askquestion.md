# Agent 表单引导 — AskQuestion（对齐网页）

> 网页表单见 `web/index.html`。Agent 侧用 **AskQuestion** 复现相同 5 个区块，让用户像点选网页一样勾选，再映射到 `recommend_cli.py` 参数。

## 何时启用

| 情况 | 行为 |
|------|------|
| Skill **刚安装**，用户说「帮我推荐」但未给食材 | **必跑** 5 轮 AskQuestion（或合并后至少问食材） |
| 用户已自然语言说清场景+食材 | **跳过**已明确的项，只补问缺失项 |
| 用户说「像网页那样选」 | **必跑**完整 5 轮 |

安装成功后：先展示 [`getting-started.md`](getting-started.md) 四种示例，再询问「要不要像网页表单一样点选？」——用户同意则按下方顺序调用 AskQuestion。

## 五轮 AskQuestion（与网页一一对应）

### Q1 · 今天想吃什么？（场景，单选，可选）

对应网页 `#scene-chips`。未选 → CLI 不传 `-s` 或 `-s happy`（默认快乐餐）。

```json
{
  "title": "菜就多练 · 选场景",
  "questions": [{
    "id": "scene",
    "prompt": "今天想吃什么风格？（可不选，默认快乐餐）",
    "options": [
      { "id": "skip", "label": "不选 / 默认快乐餐（解馋、快手）" },
      { "id": "bento", "label": "便当 — 带饭、备餐、上班族" },
      { "id": "light-meal", "label": "轻食 — 沙拉、清爽、少负担" },
      { "id": "seasonal", "label": "时令 — 节气、应季、鲜味" },
      { "id": "regional", "label": "地方味 — 家乡菜、地域风味" },
      { "id": "health", "label": "调理 — 营养、养生、轻调" },
      { "id": "happy", "label": "快乐餐 — 解馋、小吃、轰趴" }
    ]
  }]
}
```

映射：`skip` → 不传 `-s`；其余 → `-s {id}`。

---

### Q2 · 冰箱里有什么？（食材，多选，**至少 1 项**）

对应网页 `#ingredient-groups` 全部 chip。与网页 chip 列表保持一致。

```json
{
  "title": "菜就多练 · 选食材",
  "questions": [{
    "id": "ingredients",
    "prompt": "冰箱里有哪些？（可多选，至少选 1 项；选「自定义」后在对话里补充）",
    "allow_multiple": true,
    "options": [
      { "id": "番茄", "label": "番茄" },
      { "id": "黄瓜", "label": "黄瓜" },
      { "id": "菠菜", "label": "菠菜" },
      { "id": "土豆", "label": "土豆" },
      { "id": "西兰花", "label": "西兰花" },
      { "id": "胡萝卜", "label": "胡萝卜" },
      { "id": "蘑菇", "label": "蘑菇" },
      { "id": "鸡蛋", "label": "鸡蛋" },
      { "id": "鸡肉", "label": "鸡肉" },
      { "id": "牛肉", "label": "牛肉" },
      { "id": "猪肉", "label": "猪肉" },
      { "id": "虾仁", "label": "虾仁" },
      { "id": "米饭", "label": "米饭" },
      { "id": "面条", "label": "面条" },
      { "id": "藜麦", "label": "藜麦" },
      { "id": "吐司", "label": "吐司" },
      { "id": "豆腐", "label": "豆腐" },
      { "id": "奶酪", "label": "奶酪" },
      { "id": "柠檬", "label": "柠檬" },
      { "id": "鳄梨", "label": "鳄梨" },
      { "id": "custom", "label": "以上没有 — 我来自定义输入（折耳根、豆花等）" }
    ]
  }]
}
```

- 选中项（除 `custom`）→ `-i 番茄,鸡蛋,...`
- 若含 `custom`：在 **Q2 之后**请用户文字补充，或等 AskQuestion 返回 Other 后写入 `-c 折耳根,豆花`
- **禁止**在仅选 `custom` 且无文字输入时进入 Step 4

---

### Q3 · 口味偏好（可选）

对应网页 `#taste`。

```json
{
  "title": "菜就多练 · 口味",
  "questions": [{
    "id": "taste",
    "prompt": "口味偏好？（可选）",
    "options": [
      { "id": "skip", "label": "不指定" },
      { "id": "清淡", "label": "清淡" },
      { "id": "麻辣", "label": "麻辣" },
      { "id": "酸爽", "label": "酸爽" },
      { "id": "汤面", "label": "汤面 / 暖锅" },
      { "id": "甜点", "label": "甜点" },
      { "id": "other", "label": "其他（请在下一步说明）" }
    ]
  }]
}
```

映射：`skip` → 不传 `--taste`；`other` → 用户补充后 `--taste "..."`；其余 → `--taste {label}`。

---

### Q4 · 几人吃？（可选）

对应网页 `#servings`。

```json
{
  "title": "菜就多练 · 份量",
  "questions": [{
    "id": "servings",
    "prompt": "几人吃？（可选，会按膳食指南换算份量）",
    "options": [
      { "id": "skip", "label": "不指定" },
      { "id": "一人食", "label": "一人食" },
      { "id": "二人家庭", "label": "二人家庭" },
      { "id": "多人家庭", "label": "多人家庭" }
    ]
  }]
}
```

映射：`skip` → 不传 `--servings`；其余 → `--servings {id}`。

---

### Q5 · 还有别的要求？（可选）

对应网页 `#free-text`。

```json
{
  "title": "菜就多练 · 补充说明",
  "questions": [{
    "id": "extra",
    "prompt": "还有别的要求吗？（可选，可多选）",
    "allow_multiple": true,
    "options": [
      { "id": "skip", "label": "没有额外要求" },
      { "id": "赶时间", "label": "赶时间 / 要快手" },
      { "id": "无烤箱", "label": "没有烤箱" },
      { "id": "少洗碗", "label": "想少洗碗" },
      { "id": "带饭", "label": "明天带饭 / 便当" },
      { "id": "书名", "label": "指定参考书（请在对话里写书名）" },
      { "id": "other", "label": "其他（请用文字说明）" }
    ]
  }]
}
```

映射：将选中项（除 `skip`）拼成一句中文 → `--text "赶时间，没有烤箱"`；含 `书名` / `other` 时合并用户原文。

---

## 参数汇总 → recommend_cli

AskQuestion 全部完成后，组装 CLI（与网页 `POST /api/recommend` 字段一致）：

```bash
python scripts/recommend_cli.py \
  -i 番茄,鸡蛋 \
  -c 折耳根 \
  -s light-meal \
  --taste 清淡 \
  --servings 一人食 \
  --text "赶时间" \
  --pretty
```

| 网页字段 | CLI 参数 |
|----------|----------|
| `scene` | `-s` / `--scene` |
| `ingredients[]` | `-i` / `--ingredients` |
| 自定义食材 | `-c` / `--custom` |
| `taste` | `--taste` |
| `servings` | `--servings` |
| `free-text` | `--text` |

## Agent 硬规则

1. **顺序**：Q1→Q5；已能从用户首句解析的题 **跳过**，不要重复问。
2. **食材**：Q2 至少 1 项（chip 或 `-c` 自定义），与网页校验一致。
3. **自定义食材**：选 `custom` 或 AskQuestion 的 Other 后，**必须**拿到具体名称再 recommend。
4. **不要**把 5 轮合成 1 个 AskQuestion（选项过多难选）；保持与网页相同的 5 个区块心智。
5. 表单收集完成后 → 进入 SKILL.md **Step 4 → 4.6 → 5** 完整链路（含补图后再 recommend）。

## 维护

`web/index.html` 增删 scene / chip / servings 选项时，**同步更新本文** Q1–Q5 的 options 列表。
