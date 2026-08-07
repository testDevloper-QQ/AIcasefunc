# 文档维护对照

| 文档 | 用途 |
|------|------|
| [`illustration-style-bible.md`](illustration-style-bible.md) | 三层 PNG 插画风格 |
| [`line-art-guide.md`](line-art-guide.md) | 路径解析与出图工作流（仅 raster） |
| [`ingredient-art-guide.md`](ingredient-art-guide.md) | 食材 key → PNG |
| [`step-layout-guide.md`](step-layout-guide.md) | 做法步骤排版 |
| [`agent-illustration-guide.md`](agent-illustration-guide.md) | Agent 宿主出图 |

## 代码 ↔ 文档

| 模块 | 文档 |
|------|------|
| `illustration_resolver.py` | `line-art-guide.md`, `illustration-style-bible.md` |
| `illustration_jobs_cli.py` | `agent-illustration-guide.md` |
| `recipe_format.py` | `ingredient-art-guide.md`, `measurement-cn.md` |

## 校验

```bash
python scripts/validate_illustration_coverage.py
python -m pytest scripts/tests/ -q
```
