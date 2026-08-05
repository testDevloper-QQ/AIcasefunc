# 叙事插画规范（仅 AI  raster）

> Plan B：**仅**使用 Agent / 宿主出图落盘的 PNG/WebP/JPG。**不存在** SVG 模板、线稿、几何拼盘或任何回退路径。

## 资产路径

| 类型 | 路径 | 解析 |
|------|------|------|
| Hero 成品 | `assets/illustrations/dishes/{recipe_id}.png` | `resolve_dish_illustration()` |
| 步骤叙事 | `assets/illustrations/steps/{recipe_id}-step-{n}.png` | `resolve_step_illustration()` |
| 食材单项 | `assets/illustrations/ingredients/{art_key}.png` | `resolve_ingredient_illustration()` |

无文件 → API 返回空 URL → 网页显示「待出图」。

## 出图工作流

1. `python scripts/illustration_jobs_cli.py --recipe-id {id}`
2. Cursor / WorkBuddy Agent 用宿主 `GenerateImage` 出图（每 job ≤3 备选）
3. `python scripts/save_illustration.py --recipe-id {id} --kind dish|step --from {path}`

详见 [`agent-illustration-guide.md`](agent-illustration-guide.md)。

## 验证

```bash
python scripts/validate_illustration_coverage.py
pytest scripts/tests/ -q
```

## 已移除（勿恢复）

- `assets/line-art/`、`compose_art.py`、`generate_line_art.py`
- `generate_illustration_assets.py`、品类/步骤 SVG 模板
- 索引字段 `line_art`、API 字段 `heroArts` / `sceneUrl` / `ingredientArts`
