# 推荐引擎规范

> 防止「选了鸡肉却推虾仁」类问题。实现：`scripts/recommend_engine.py` + `recipe_format.py`。

## 核心规则（Hard Rules）

| 规则 | 行为 |
|------|------|
| **食材必选匹配** | 用户提供了食材时，主推荐 **必须包含全部所选食材**（含同义词） |
| **零匹配排除** | 菜谱 haystack 不含任一用户食材 → `score = -100`，不得进入 top |
| **场景加权** | 命中用户场景 +15；有食材但未命中场景 -5 |
| **时长过滤** | 仅 `≤ 60min` 进入候选池（`is_quick_recipe`） |
| **索引无匹配** | 走 `home_cooking_fallback` → 优先 LLM（`OPENAI_API_KEY`）→ 离线模板 |
| **默认场景** | 未选场景 → `happy`（快乐餐） |

## 匹配范围（haystack）

菜谱名称 + tags + 食材名 + **步骤全文**：

```python
# recommend_engine._recipe_haystack
name + tags + ingredients[].name + steps[].text
```

## 同义词扩展

`INGREDIENT_SYNONYMS`（`recipe_format.py`）示例：

| 用户输入 | 可匹配索引表述 |
|----------|----------------|
| 鸡肉 | 鸡肉、鸡胸肉、鸡翅、鸡丝、清远鸡… |
| 虾 | 虾、虾仁、白虾、明虾 |
| 番茄 | 番茄、西红柿 |
| 豆角 | 豆角、四季豆 |

匹配函数：`ingredient_matches_in_text(hay, user_ingredient)`  
注意：**不用裸「鸡」** 匹配，避免误命中「鸡蛋」。

## 评分公式（简）

```
base = match_count × 20
+ 全部匹配 bonus 25
+ 场景命中 15（或未命中 -5）
+ 时长 bonus 1~2
```

## 场景 + 食材冲突处理

- 例：时令 + 鸡肉 → 优先 `scene` 含 seasonal 且含鸡肉同义词的菜（如丝瓜风鸡粥）
- 若无场景内匹配：仍返回含鸡肉的菜，但 `why` 说明场景；**不得**返回不含鸡肉的菜

## Web / CLI 配置

| 项 | 推荐值 | 说明 |
|----|--------|------|
| `web/config.json` → `skillSource` | `local` | 开发时用本地最新引擎，避免 Git 缓存旧逻辑 |
| CLI Windows | `PYTHONIOENCODING=utf-8` | 避免 `--pretty` 输出 UnicodeEncodeError |

## 新增场景时（见 extension-checklist）

1. `data/recipe-index/{scene}.yaml` 或扩展现有索引
2. `scene-router.md` 补路由表
3. `web/index.html` 场景 chip（若新 UI 场景）
4. 确认新索引菜品的 **食材均有线稿映射**
5. 增加 `test_ingredient_match.py` 或场景专项测试

## 相关测试

```bash
pytest scripts/tests/test_ingredient_match.py -q
pytest scripts/tests/test_recommend_cli.py -q
```
