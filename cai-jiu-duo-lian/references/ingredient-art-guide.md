# 食材插画规范

> 每项食材独立 PNG，路径 `assets/illustrations/ingredients/{art_key}.png`。

## 数据流

```
索引/LLM 食材 name
  → guess_ingredient_art_key(name)     # recipe_format.py → INGREDIENT_ART
  → resolve_ingredient_illustration()
  → ingredients/{key}.png  （存在则 artUrl，否则空）
  → 网页 renderIngredientGrid → 「待出图」或 72×72 手绘
```

## 映射

完整关键词 → `art_key` 见 `scripts/recipe_format.py` → `INGREDIENT_ART`。

## 新增食材 key

1. 在 `INGREDIENT_ART` 增加中文关键词 → key
2. Agent 出图落盘 `assets/illustrations/ingredients/{key}.png`
3. `pytest scripts/tests/test_ingredient_art.py -q`

## 已移除

- `assets/line-art/`、`generate_line_art.py`
- 任何 SVG / 几何占位回退
