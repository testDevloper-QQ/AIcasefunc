# 手绘风视觉规范

> 参考用户提供的出餐图、步骤容器图样，统一为 **暖黄手账 + 线稿 + 淡水彩** 风格。禁止用 emoji 替代功能图标。

## 三层配图（必保留）

| 层级 | 位置 | 要求 | 资源 |
|------|------|------|------|
| **Hero 出餐图** | 推荐卡片顶部右侧 | 整菜或主食材 **手绘线稿**，暖黄画框，标注「手绘出餐示意」 | 索引 `line_art` → `/skill-assets/assets/line-art/` |
| **食材线稿** | 食材清单网格 | 每项配食材 SVG 线稿 + 中文份量 | `assets/line-art/{name}.svg`，`recipe_format.enrich_ingredients` |
| **步骤容器场景** | 做法每步左侧 | **容器场景**（烤/锅/炒/碗/砧/盘）+ 涉及食材线稿叠加 | `web/icons/step-scenes/` + 食材 art |

## 风格要点

- 描边 `#5C4F42` / `#4A4035`，填色 `#FFF8E7` 或淡水彩半透明
- 背景暖黄 `#FFF8E7`，强调 `#E8A838`
- 标题用手写体（站酷快乐体）
- **不要**真实照片默认占位；**不要** emoji 图标

## 资源优先级

1. `assets/line-art/` 已有 SVG（`scripts/generate_line_art.py` 可批量生成）
2. 索引字段 `line_art` 指向菜品/主材线稿
3. 联网公开图（仅对话输出可选，网页优先线稿）
4. 无图时用容器场景 + 食材 fallback，**不阻塞推荐**

## 网页实现对照

| 需求 | 实现文件 |
|------|----------|
| Hero 大图 | `web/app.js` → `renderRecipeCard` → `heroImageUrl` / `lineArtUrl` |
| 食材网格线稿 | `renderIngredientGrid` → `ingredient.artUrl` |
| 步骤容器+叠加 | `renderStepItem` → `sceneUrl` + `ingredientArts` |
| 后端格式化 | `scripts/recipe_format.py` → `format_steps`, `enrich_ingredients` |

## 对话 / Agent 输出

无网页时，须在文字中描述等价视觉（见 `output-template.md`）：

- Hero：菜名 + 出处徽章 + 「出餐手绘线稿」说明
- 食材：名称 + 克/毫升 + 线稿名称
- 步骤：容器类型 + 涉及食材 + 中文步骤

## 维护

- 新增常见食材：运行 `python scripts/generate_line_art.py`，并在 `recipe_format.INGREDIENT_ART` 补映射
- 变更视觉规范时同步：`style-guide.md`、`output-template.md`、本文件
