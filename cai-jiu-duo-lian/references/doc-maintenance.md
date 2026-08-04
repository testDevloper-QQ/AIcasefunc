# 用户文档维护说明

本 Skill 的**用户侧文档**与**内部文档**分离，功能变更时须同步更新对应文件。

## 用户侧（随 Skill / 远程 Git 部署）

| 文件 | 何时更新 |
|------|----------|
| `README.md` | 安装方式、网页用法、配置、限制变更 |
| `SKILL.md` | Agent 工作流、硬规则、QA 检查项变更 |
| `references/output-template.md` | 输出格式、QA 清单变更 |
| `references/measurement-cn.md` | 中国计量换算规则变更 |
| `references/getting-started.md` | 安装成功示例、四种场景变更 |
| `references/capabilities.md` | 能力清单与版本记录变更 |
| `references/dietary-guidelines-cn.md` | 份量换算依据变更 |
| `references/scene-router.md` | 场景路由规则变更 |
| `references/style-guide.md` | 视觉/话术规范变更 |
| `web/index.html`、`web/app.js` | 表单字段、交互文案变更 |

## 内部（仅本地，不推远程）

| 文件 | 说明 |
|------|------|
| `skill生成需求背景.md` | 需求追溯与实现状态；**不影响用户使用**，已在 `.gitignore` 与 `deploy_to_github.py` 排除 |

## 设计规格（仓库级）

| 文件 | 说明 |
|------|------|
| `docs/superpowers/specs/2026-08-04-我的菜谱-design.md` | 产品设计规格，重大变更时同步 |

## 部署检查

运行 `python scripts/deploy_to_github.py` 前确认：

- [ ] `README.md` 已反映最新用户可见行为
- [ ] `skill生成需求背景.md` 未被复制到远程（脚本已自动排除）
- [ ] `references/dietary-guidelines-cn.md` 与 `recipe_format.py` 一致
- [ ] `references/measurement-cn.md` 与 `recipe_format.py` 计量规则一致
