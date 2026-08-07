# 叙事插画风格圣经（Plan B · 仅 raster）

> 与 [`line-art-guide.md`](line-art-guide.md) 一致：**仅** AI/Agent 出图 PNG，无 SVG、无几何拼盘、无回退。

## 三层配图

| 层级 | 资产 | 无图时 |
|------|------|--------|
| **Hero 成品** | `dishes/{recipe_id}.png` | 网页「插画待生成」 |
| **步骤叙事** | `steps/{recipe_id}-step-{n}.png` | 网页「步骤插画待生成」 |
| **食材单项** | `ingredients/{art_key}.png` | 网页「待出图」 |

## Medium 规格（默认，v1.10.3+）

落盘时由 `illustration_medium.py` / `save_illustration.py` **自动**缩放与 PNG 优化；无需 Agent 手动处理。

| 类型 | 长边上限 | 网页展示参考 | 说明 |
|------|---------|-------------|------|
| **成品 Hero** | **1024 px** | ~280×245 px | Retina 下仍清晰 |
| **步骤** | **768 px** | 左栏 ~135–180 px 高 | 动作叙事小图 |
| **食材** | **512 px** | 72×72 px 网格 | 单项线稿 |

- 源图大于上限 → 等比缩小（LANCZOS）；**不大于则保持原尺寸**，仅 PNG 优化
- 编码：`optimize=True`，`compress_level=9`
- 批量转换已有资产：`python scripts/optimize_illustrations.py --pretty`
- 部署默认 **`--profile medium`**（含 medium PNG，不含维护脚本）；见 `deploy_to_github.py`

## 风格

- 水彩 / 手账 scrapbook 风，暖黄奶油纸底
- 描边柔和，食物可识别，**禁止**抽象几何占位
- 步骤图体现**动作**（预热、搅拌、涂刷、出炉），非容器 icon

## 出图

见 [`agent-illustration-guide.md`](agent-illustration-guide.md)。
