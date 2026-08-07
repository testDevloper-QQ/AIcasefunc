# WorkBuddy / Cursor 对话输出规范

> Web 页用 `web/app.js` 渲染；**WorkBuddy 无 `/skill-assets/` 服务**，须把 PNG **内联嵌入**模型回复正文，**禁止**只放侧边栏附件。

## 三个常见错误（WorkBuddy）

| 错误 | 表现 | 正确做法 |
|------|------|----------|
| 成品图只在侧边栏 | 正文食材上方空白 | 正文中 `![菜名 成品](绝对路径.png)` |
| 步骤无插图 | 做法只有文字 | 每步上方 `![步骤N](绝对路径.png)` |
| 备选菜只有菜名 | 后 2 道无食材/步骤/图 | 备选也跑完整模板（见下） |

## Step 5 硬规则（WorkBuddy）

1. **禁止**仅将插画作为「附件/侧边栏图片」而不写入回复 Markdown。
2. **必须**在回复正文用 `![描述](图片地址)` 嵌入：
   - 食材清单**上方**：成品 Hero
   - 每个食材行（可选小图）：`ingredients[].artUrl`
   - 每个步骤**文字上方**：`steps[].stepIllustrationUrl`
3. **图片地址**（二选一）：
   - **推荐**：Skill 内 PNG **绝对路径**（`path` 模式）
   - 或启动 Web 后 **HTTP URL**（`http` 模式，`http://127.0.0.1:8765/skill-assets/...`）
4. **`/skill-assets/...` 相对 URL 不能直接用于 WorkBuddy 对话**（除非 Web 已启动且用 http 模式）。
5. **备选菜 `alternates[]`**：每道须与主推荐相同结构（Hero + 食材 + 步骤 + 内联图），不能只列菜名。

## 推荐 CLI（自动生成 WorkBuddy Markdown）

与 Step 4 相同参数，输出可直接粘贴/作为最终回复的正文：

```bash
python scripts/format_chat_output_cli.py -i 鸡,酸奶 -s happy --servings 二人家庭
```

从已有 JSON：

```bash
python scripts/recommend_cli.py -i 鸡,酸奶 -s happy --pretty > /tmp/rec.json
python scripts/format_chat_output_cli.py --from-json /tmp/rec.json
```

Web 服务已启动时用 HTTP 图片：

```bash
python scripts/format_chat_output_cli.py -i 鸡,酸奶 --image-mode http
```

## Markdown 结构示例

```markdown
## 🍳 推荐：香烤全鸡
📖 出处：《抗炎食谱100例》· …
⏱ 50分钟 · …

![香烤全鸡 成品](E:/.../assets/illustrations/dishes/ben-054.png)

### 🥬 食材（2 人份）

![鸡](E:/.../ingredients/chicken.png)
- **鸡** 500克

### 👩‍🍳 做法

![步骤1](E:/.../steps/ben-054-step-1.png)
**①** 预热烤箱至 180℃ …

---

## 🍳 备选 1：…
（同样完整结构）
```

## 与网页的差异

| 能力 | Web 表单 | WorkBuddy 对话 |
|------|----------|----------------|
| 图片解析 | `/skill-assets/` + 本地服务 | **绝对路径** 或 **http://127.0.0.1:8765/...** |
| 布局 | CSS 手账卡片 | Agent 输出 Markdown |
| 备选菜 | `alternates` 卡片 | 须 `format_chat_output_cli` 或同等内联格式 |

## Agent 自检（输出前）

- [ ] 成品图在**正文**食材区上方，不在仅侧边栏
- [ ] 每一步做法前有步骤 PNG（或明确「待生成」）
- [ ] `alternates` 每道含 Hero + 食材 + 步骤
- [ ] 未使用裸 `/skill-assets/`（WorkBuddy 无法加载）
