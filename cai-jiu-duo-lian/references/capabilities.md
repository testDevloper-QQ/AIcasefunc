# Skill 能力清单（v1.7.0）

> 菜就多练 · 场景驱动菜谱推荐

## 核心能力

| 能力 | 说明 | 实现 |
|------|------|------|
| 场景驱动推荐 | 6 类饮食偏好路由索引 | `scene-router.md` + `data/recipe-index/` |
| 食材严格匹配 | 所选食材须全部出现在推荐菜（含同义词） | `recommend-engine-guide.md` |
| LLM 家常菜谱 | 索引无匹配 → 联网 + 大模型 | `llm_recipe_search.py` |
| 中国计量 + 膳食 QA | ≤60min、克/毫升、份量核验 | `measurement-cn.md`, `recipe_format.py` |
| 手账叙事插画（Plan B） | Hero 菜品 + 步骤叙事 + 食材单项 | `illustration-style-bible.md`, `illustration_resolver.py` |
| Agent CLI | 无需 Web 的 JSON 推荐 | `recommend_cli.py` |
| 网页 PWA | 表单推荐 + 手账风卡片 | `web_server.py`, `web/app.js` |

## 网页视觉（v1.6）

| 能力 | 规范 |
|------|------|
| Hero | `heroIllustrationUrl` 菜品/品类叙事插画 |
| 食材区 | 虚线框 +「食材」标签 + `/skill-assets/` 手绘 |
| 做法区 | `stepIllustrationUrl` 步骤叙事 + 荧光笔 + 唠唠叨叨 |
| 字体 | 站酷快乐体 + 马善政 |

## 脚本与验证

| 脚本 | 用途 |
|------|------|
| `recommend_cli.py` | Agent CLI（UTF-8 输出） |
| `illustration_resolver.py` | Hero / 步骤 / 食材插画查表 |
| `generate_ai_illustrations.py` | AI 批量出 Hero + 步骤 PNG（≤3 备选/图） |
| `validate_illustration_coverage.py` | Plan B 插画覆盖率 |
| `validate_illustration_coverage.py` | PNG 插画覆盖率统计 |
| `validate_index.py` | YAML 索引结构 |
| `verify_install.py` | 安装 + 四种场景示例 |
| `pytest scripts/tests/` | 34+ 单元测试 |

## 规范文档

见 [`doc-maintenance.md`](doc-maintenance.md)；扩展变更见 [`extension-checklist.md`](extension-checklist.md)。

## 明确不做（v1）

- 拍照识材、小红书、用户收藏/分享

## 版本记录

| 版本 | 日期 | 要点 |
|------|------|------|
| 1.0.0 | 2026-08-04 | 索引 + Skill + 静态表单 |
| 1.2.0 | 2026-08-04 | 中国计量、Hero、步骤容器 |
| 1.2.1 | 2026-08-04 | Agent CLI、ensure_web_server |
| 1.3.0 | 2026-08-04 | 食材严格匹配、LLM fallback |
| 1.4.x | 2026-08-04 | 做法手账排版、step-layout |
| 1.5.x | 2026-08-04 | compose 合成（**v1.6 起废弃主路径**）、规范体系 |
| 1.6.0 | 2026-08-04 | **Plan B 插画库**、叙事 Hero/步骤、文档全面对齐 |
| 1.7.0 | 2026-08-04 | **AI 出图 pipeline**、PNG 优先、每图 ≤3 备选 |
