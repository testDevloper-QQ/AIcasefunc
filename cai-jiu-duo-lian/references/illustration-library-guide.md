# 插画素材库 — 按书籍预生成、共享复用

## 设计目标

用户访问网页前，先把参考资料中的插画**批量预生成**并落盘；访问时只做查表插入，避免「待出图」。

| 层级 | 路径 | 复用规则 |
|------|------|----------|
| **成品 Hero** | `dishes/{recipe_id}.png` 或 `dishes/shared/{菜名}.png` | **同名菜共用**一张 shared 图 |
| **步骤叙事** | `steps/{recipe_id}-step-{n}.png` | 每道菜独立（步骤文本不同） |
| **食材/调料** | `ingredients/{artKey}.png` | **全库共用**（独立素材表） |

落盘规格（medium，v1.10.3+）：Hero 1024 / 步骤 768 / 食材 512 px 长边；见 [`illustration-style-bible.md`](illustration-style-bible.md)。

## 目录

```
data/illustration-library/
  books.yaml           # 书籍索引（首期：抗炎食谱100例）
  ingredients.yaml     # 食材/调料素材表（artKey、别名、是否已有图）
  coverage/            # 按书覆盖率 JSON 报告
assets/illustrations/
  dishes/shared/       # 同名菜共享成品图
  ingredients/         # 共享食材线稿
  steps/               # 每菜步骤图
```

## 维护流程（以《抗炎食谱100例》为例）

### 1. 生成食材素材表

```bash
python scripts/audit_illustration_library.py --book 抗炎食谱100例 --bootstrap-ingredients
```

### 2. 审计缺失

```bash
python scripts/audit_illustration_library.py --book 抗炎食谱100例 --save-report
```

### 3. 导出预生成任务（去重：食材 key、同名成品只出一次）

```bash
python scripts/illustration_jobs_cli.py --book 抗炎食谱100例 --pretty > jobs.json
```

### 4. Agent 批量出图并落盘

- **成品**：`save_illustration.py --kind dish --shared-dish-name 菜名`（写入 id 路径 + shared 路径）
- **食材**：`--kind ingredient --art-key salt`（全库共用）
- **步骤**：`--kind step --step-index N`（**仅烹饪步骤**，跳过营养/冗余句；索引与网页展示一致）

**步骤过滤（v1.10+）**：`filter_cooking_steps()` 统一用于网页展示、出图任务与覆盖率审计——不展示/不出图：
- 营养说明（卡路里、钠、脂肪、维生素等）
- 无实际操作冗余句（「即可享用」「趁热享用」等）
- 占位符（`* * *`）

### 5. 用户访问

`illustration_resolver.py` 查磁盘 PNG → 有则展示，无则「待出图」。

## 扩展新书

在 `books.yaml` 追加条目，重复步骤 1–4 即可。
