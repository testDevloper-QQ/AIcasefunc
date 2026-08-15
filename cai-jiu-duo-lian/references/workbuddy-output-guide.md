# WorkBuddy / 多宿主对话输出规范

> Web 页用 `web/app.js` 渲染。对话宿主能力不同：**WorkBuddy 不渲染** `![](本地路径.png)`，须用 **`present_files`** 展示图片卡片。

## 宿主能力（先认宿主，再选通道）

| 宿主 | 可靠出图通道 | 说明 |
|------|--------------|------|
| **WorkBuddy 对话** | `present_files`（按序传 PNG 绝对路径） | Markdown `![](本地路径)` **无效** |
| **WorkBuddy HTML 预览** | **自包含 HTML（base64 内嵌）** | 预览面板跨端口会拦 `http://127.0.0.1:8765/...` |
| **Cursor** | `![](绝对路径)` 或 `![](http://127.0.0.1:8765/skill-assets/…)` | 视客户端；可用 `--image-mode path` / `http` |
| **网页表单（同端口）** | `/skill-assets/` + Web 服务 | 打开 `http://127.0.0.1:8765/` 即可，**勿**改成默认 base64 |
| **其他 AI 办公应用** | 待抽象（见文末「通用能力」） | 清单层可复用；呈现层按宿主接 |

**素材库预出图 / 落盘复用不变**；变的是「怎么给用户看图」，不是放弃 Plan B。

## WorkBuddy Step 5（必遵）

1. 跑 `--markdown`（默认 `--image-mode present`）得到：**正文文案** + **`<!-- PRESENT_FILES … -->` 块**。
2. 将文案作为用户可见回复（菜名 / 食材 / 步骤文字）。
3. 解析块内 JSON，**按 `paths` 顺序**调用 **`present_files`** 展示图片卡片（Hero → 食材 → 步骤；备选菜同样接在后面）。
4. **禁止**只把出图结果丢侧边栏附件、不做 `present_files`。
5. **禁止**指望正文里的 `![](E:/….png)` 在 WorkBuddy 里内联显示。
6. **`alternates[]`**：每道须完整文案 + 同一 `paths` 清单中的配图，不能只列菜名。

### CLI

**硬规则**：参数 = Step 3 用户输入 = Step 4 / 4.6 历次 recommend；禁止套用文档示例食材。

```bash
# WorkBuddy（默认 present）
python scripts/recommend_cli.py \
  -i <用户食材> \
  -c <自定义食材，可选> \
  -s <用户场景> \
  --servings <用户份量> \
  --text "<补充说明，可选>" \
  --markdown
```

Cursor 等仍要 Markdown 内联时：

```bash
… --markdown --image-mode path
# 或 Web 已启动：
… --markdown --image-mode http
```

从已有 JSON：

```bash
python scripts/format_chat_output_cli.py --from-json <第二次recommend的JSON>
```

### Agent 动作（WorkBuddy）

1. 把 `PRESENT_FILES` 块**上方**的 Markdown 贴进回复正文。  
2. 读取块内 `"paths": [ ... ]`，调用：

```text
present_files(paths=[...按数组顺序...])
```

3. 一块清单可一次提交；若宿主限制单次数量，按 `items[].role` 分段，但**顺序不变**。

## WorkBuddy HTML 预览（`html_embedded`）

**根因**：HTML 预览面板端口 ≠ `8765` 时，页面里的 `http://127.0.0.1:8765/skill-assets/...` 会被拦截 → 破损图。

**做法**：仅导出**本次推荐**（主推 + 备选）为单文件 HTML，图片 **base64 内嵌**；不改线上 `web/app.js` 默认路径。

```bash
# 与 recommend 相同用户参数
python scripts/recommend_cli.py \
  -i <用户食材> -s <场景> --servings <份量> \
  --export-html

# 或
python scripts/export_html_cli.py -i <食材> -s <场景> --out path/to/preview.html

# 体积偏大时跳过食材小图
python scripts/recommend_cli.py -i <食材> --export-html --export-html-no-ingredient-art
```

CLI 打印 JSON：`htmlPath` / `bytes` / `embeddedImages` / `channel: html_embedded`。

Agent：把 `htmlPath` 交给 WorkBuddy 打开/预览（或 `present_files` 该 HTML）。**禁止**把 16MB 级导出 HTML 提交进 Git（已 gitignore `exports/`）。

优先顺序：能同端口打开 `http://127.0.0.1:8765/` → 不必导出；必须进独立预览面板 → `--export-html`。

### 对话 Markdown 结构示意

```markdown
## 🍳 推荐：香烤全鸡
📖 出处：…
⏱ …

*成品配图 → present_files（香烤全鸡 成品）*

### 🥬 食材（2 人份）

- **鸡** 500克 *(配图 → present_files)*

### 👩‍🍳 做法

*步骤1配图 → present_files*
**①** 预热烤箱至 180℃ …

<!-- PRESENT_FILES
{
  "tool": "present_files",
  "paths": ["E:/.../dishes/….png", "E:/.../ingredients/….png", "E:/.../steps/….png"],
  "items": [ … ]
}
PRESENT_FILES -->
```

## 与网页的差异

| 能力 | Web 表单 | WorkBuddy 对话 | WorkBuddy HTML 预览 | Cursor |
|------|----------|----------------|---------------------|--------|
| 图片 | `/skill-assets/` | `present_files` | **base64 自包含 HTML** | Markdown `![](…)` |
| CLI | `POST /api/recommend` | `--markdown` | `--export-html` | `--markdown --image-mode path\|http` |

## Agent 自检（输出前）

- [ ] `--markdown` / `--export-html` 参数与用户本次输入一致  
- [ ] WorkBuddy 对话：已调用 `present_files`，顺序 = Hero → 食材 → 步骤（含备选）  
- [ ] WorkBuddy HTML 预览：用 `--export-html`，未引用跨端口 `8765` 图床  
- [ ] 未依赖 WorkBuddy 渲染 `![](本地路径)`  
- [ ] `alternates` 文案完整  
- [ ] 未把裸 `/skill-assets/` 当聊天图片地址  
- [ ] 未把 `exports/*.html` 提交进 Git  

## 通用能力（后续，不止 WorkBuddy）

目标：同一套「菜谱结果 + 有序配图路径」，适配多种 AI 办公宿主。

| 层 | 职责 |
|----|------|
| **内容层（已有）** | `recommend` JSON + `assets/illustrations/` 落盘 |
| **清单层** | `collect_recommend_present_files` / `PRESENT_FILES` 块（有序 path + role） |
| **呈现层（按宿主）** | `present_files` · `html_embedded` · markdown path/http · 同端口 web_open |

配置意向：`chatImageChannel: present_files | html_embedded | markdown_path | markdown_http | web_open`。**清单格式保持稳定以便复用。**
