# Skill 能力清单（v1.2）

> 菜就多练 · 场景驱动菜谱推荐 · 2026-08-04 沉淀

## 核心能力

| 能力 | 说明 | 实现 |
|------|------|------|
| 场景驱动推荐 | 6 类饮食偏好路由索引 | `SKILL.md` + `scene-router.md` + `data/recipe-index/` |
| 三种入口 | 场景 / 食材 / 指定需求 | 对话 + 网页表单 |
| 默认快乐餐 | 用户未选场景 → `happy` | `recommend_engine.py` |
| 自定义食材 | 示例外食材输入框 | 网页 + `customIngredients` API |
| LLM 家常菜谱 | 索引无匹配时联网搜索 + 大模型 | `llm_recipe_search.py` + `OPENAI_API_KEY` |
| 时长过滤 | 仅推荐 ≤ 60 分钟 | `recipe_format.is_quick_recipe` |
| 家庭份量换算 | 批量配方 → 家庭克数 | `recipe_format.normalize_ingredients` |
| 膳食指南 QA | 输出前份量校验 | `dietary-guidelines-cn.md` + `validate_home_output` |
| 中国计量 | 华氏/盎司/cup 自动转中文单位 | `measurement-cn.md` + `localize_text/amount` |
| 手绘视觉 | 出餐图 + 食材线稿 + 步骤容器场景 | `assets/line-art/` + `web/icons/step-scenes/` |

## 网页能力（v2）

| 能力 | 说明 |
|------|------|
| 在线推荐 | `POST /api/recommend`，页面内直接出菜 |
| PWA | 可添加到手机桌面 |
| Git Skill | `web/config.json` 拉取远程仓库 |
| 推荐卡片 | 手账风 Hero：大标题 + 出餐线稿 + 信息徽章 |
| 食材展示 | 网格线稿 + 中文份量 |
| 步骤展示 | 容器场景 SVG + 食材叠加 + 步骤序号 |

## 脚本与测试

| 脚本 | 用途 |
|------|------|
| `recommend_cli.py` | Agent 侧 CLI 推荐（无需 Web） |
| `verify_install.py` | 安装验证 + 打印四种场景示例 |
| `ensure_web_server.py` | 检测/后台启动 Web 服务 |
| `web_server.py` | 静态页 + API |
| `recommend_engine.py` | 索引匹配推荐 |
| `recipe_format.py` | 计量/份量/步骤格式化 |
| `skill_loader.py` | local / git Skill 来源 |
| `deploy_to_github.py` | 部署远程（含打包校验） |
| `test_git_skill.py` | Git 链路验证 |
| `pytest scripts/tests/` | 10+ 单元测试 |

## 明确不做（v1）

- 拍照识材、小红书补充、LLM 生成菜谱、存储/收藏/分享

## 版本记录

| 版本 | 日期 | 要点 |
|------|------|------|
| 1.0.0 | 2026-08-04 | 索引 + Skill + 静态表单 |
| 1.1.0 | 2026-08-04 | 在线 API、Git 部署、膳食指南份量 |
| 1.2.0 | 2026-08-04 | 中国计量、Hero 出餐图、步骤容器配图、默认快乐餐 |
| 1.2.1 | 2026-08-04 | Agent CLI、ensure_web_server、跨平台 Python 启动、远程 config 默认 local |
| 1.2.2 | 2026-08-04 | 安装成功四种场景输入示例、verify_install.py |
