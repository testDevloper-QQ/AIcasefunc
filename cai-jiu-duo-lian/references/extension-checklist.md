# 扩展与变更检查清单

> **任何新场景、新食材、新 UI、新 API 字段** 均按本清单执行。Agent 开发中若规范未覆盖，按各 guide 末尾流程 dokument 后同步本文。

## A. 新增饮食场景（如第 7 类场景）

- [ ] `data/recipe-index/{scene-id}.yaml` 索引
- [ ] `references/scene-router.md` 路由表
- [ ] `web/index.html` 场景 chip + `web/icons/scenes/{scene-id}.svg`
- [ ] `web/app.js` → `SCENES` / `SCENE_LABELS`
- [ ] `SKILL.md` When to use + getting-started 示例
- [ ] `recommend_engine.py` / `llm_recipe_search.py` 场景 label
- [ ] `pytest` 至少 1 个「场景 + 食材」回归
- [ ] `capabilities.md` 版本记录

## B. 新增索引菜谱

- [ ] YAML 完整：`id, name, scene, tags, cook_time, ingredients, steps, source`
- [ ] `cook_time` ≤ 60min
- [ ] 食材名为 **中文**
- [ ] `python scripts/validate_index.py`
- [ ] `python scripts/validate_illustration_coverage.py`
- [ ] `python scripts/validate_illustration_coverage.py`
- [ ] 可选：`assets/illustrations/dishes/{id}.svg` 专属 Hero

## C. 新增食材 / 自定义食材

- [ ] `recipe_format.py` → `INGREDIENT_ART`
- [ ] 若需推荐匹配：`INGREDIENT_SYNONYMS`
- [ ] `references/ingredient-art-guide.md` 资源表
- [ ] `test_ingredient_art.py` 或 coverage 通过

## D. 手绘 / UI 变更（Plan B）

| 层级 | 规范文件 | 代码 |
|------|----------|------|
| 风格圣经 | `illustration-style-bible.md` | 视觉基调 |
| 总览 | `line-art-guide.md` | `illustration_resolver.py` |
| Hero 成品 | `illustration-style-bible.md` | `resolve_dish_illustration`, `renderHeroArts` |
| 做法步骤 | `step-layout-guide.md` | `resolve_step_illustration`, `renderStepItem` |
| 食材清单 | `ingredient-art-guide.md` | `resolve_ingredient_illustration`, `.ing-*` |
| 语气/配色 | `style-guide.md` | `styles.css`, fonts |
| 资产生成 | — | `illustration_jobs_cli.py` + Agent 出图 |

变更后：

- [ ] `web/app.js` + `web/styles.css` 同步
- [ ] `mountResultWithArtReady` 预加载 `/skill-assets/` 图
- [ ] Ctrl+F5 强刷验证
- [ ] **勿** 恢复 SVG / line-art / compose 几何拼盘路径

## E. 输出 / API 字段变更

- [ ] `references/output-template.md` 字段表
- [ ] `illustration_resolver.py` / `recipe_format.py` / `recommend_engine.py`
- [ ] `web/app.js` 渲染
- [ ] `SKILL.md` Step 5 + Step 4.5 QA

当前 API 关键字段（v1.6）：

| 字段 | 说明 |
|------|------|
| `primary.heroIllustrationUrl` | 菜品叙事插画 URL |
| `primary.heroIllustrationSource` | `dish` \| `category` |
| `primary.heroIllustrationUrl` | Hero PNG URL |
| `primary.ingredients[].artUrl` | `/skill-assets/` 食材手绘 |
| `primary.steps[].stepIllustrationUrl` | 步骤叙事插画 URL |
| `primary.steps[].sceneId` | 如 `pot_porridge_simmer` |
| `why` / `usedFallback` | 推荐理由 / 是否 AI 生成 |

## F. 文档同步矩阵

| 变更类型 | 必同步文件 |
|----------|------------|
| 视觉/插画 | `illustration-style-bible.md`, `line-art-guide.md`, `ingredient-art-guide.md`, `step-layout-guide.md`, `style-guide.md` |
| 推荐逻辑 | `recommend-engine-guide.md`, `SKILL.md` Hard rules, `capabilities.md` |
| 计量/份量 | `measurement-cn.md`, `dietary-guidelines-cn.md`, `output-template.md` |
| 安装/用法 | `README.md`, `getting-started.md` |
| 维护流程 | `doc-maintenance.md`, 本文件 |

## G. 发布前验证（一键）

```bash
python scripts/validate_index.py
python scripts/validate_line_art_coverage.py
python scripts/validate_illustration_coverage.py
python -m pytest scripts/tests/ -q
python scripts/verify_install.py
```

Windows CLI 抽检：

```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts/recommend_cli.py -i 鸡肉 -s seasonal --pretty
```

## H. 规范未覆盖时的 Agent 流程

1. 实现功能并本地验证
2. 判断属于 A–G 哪一类，补 checklist 项
3. 在对应 `references/*-guide.md` 增加条目
4. 更新 `capabilities.md` + `SKILL.md` version
5. 跑 G 节命令全部通过后交付
