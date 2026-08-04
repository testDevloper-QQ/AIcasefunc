# 菜就多练 — 用户使用指南

> 先定场景，再出好菜

## 简介

「菜就多练」是一个 **场景驱动** 的菜谱推荐 Cursor Agent Skill。从本地 7 本饮食参考资料的预建索引中推荐可执行菜谱，帮助上班族、一人食等人群减少「今天吃什么」的决策成本。

## 安装

### 方式一：项目 Skill（推荐）

将整个 `我的菜谱skill` 文件夹复制到项目的 `.cursor/skills/` 目录下，或在 Cursor 设置中添加 Skill 路径。

### 方式二：个人 Skill

复制到 `~/.cursor/skills/cai-jiu-duo-lian/`（保留 `SKILL.md` 及子目录结构）。

安装后重启 Cursor 或重新加载 Skill 即可使用。

## 对话用法

在 Cursor 对话中直接描述需求，Agent 会自动触发 Skill。

### 三种入口

| 模式 | 示例 |
|------|------|
| 场景驱动 | 「轻食，一人食，想吃点清爽的」 |
| 食材驱动 | 「有鸡蛋、番茄、黄瓜，能做什么」 |
| 指定需求 | 「想做一份便当，明天带饭」 |

### 示例 Prompt

```
轻食，有黄瓜和鸡蛋，一人食
```

```
今天立春吃什么？想要应季一点的
```

```
川渝口味下饭菜，二人家庭
```

Agent 会先查本地索引 `data/recipe-index/`，未命中再读 `参考书籍/` 原文。

## 网页用法（推荐：在线服务）

### 启动服务

```powershell
cd "我的菜谱skill"
python scripts/web_server.py
```

终端会显示本机地址与 **手机局域网地址**（如 `http://192.168.x.x:8765/`）。

### 使用步骤

1. 浏览器打开 `http://127.0.0.1:8765/`
2. 可选选择饮食偏好，**至少选 1 个食材**
3. 点击「开始推荐」→ 页面直接显示菜谱（含步骤、食材、出处、线稿图）
4. 手机：同一 WiFi 下访问局域网地址 → 浏览器「添加到主屏幕」

> 不要直接双击 `index.html`（`file://` 无法调用 API）。

### Skill 来源配置

编辑 `web/config.json`：

```json
{
  "skillSource": "local",
  "localSkillPath": ".."
}
```

使用远程 Git 仓库（稍后指定地址时填写）：

```json
{
  "skillSource": "git",
  "gitRepoUrl": "https://github.com/your/repo.git",
  "gitBranch": "main",
  "gitSkillSubPath": "path/to/skill"
}
```

### 安装到手机桌面（PWA）

1. 手机浏览器打开局域网地址
2. 菜单 → 「添加到主屏幕」/「安装应用」
3. 桌面出现「菜就多练」图标，可独立打开

## 知识库说明

| 类型 | 路径 |
|------|------|
| 索引（优先检索） | `data/recipe-index/*.yaml` |
| 书籍原文（补读） | `参考书籍/` |
| 索引说明 | `references/knowledge-sources.md` |

读取顺序：`.md` → `.pdf` → `.docx` → `.epub`

当前索引约 **145 道**代表菜，覆盖 6 大场景。

## 目录结构

```
我的菜谱skill/
├── SKILL.md                 # Skill 主逻辑
├── README.md                # 本指南
├── references/              # 路由、风格、输出模板
├── data/recipe-index/       # 预建菜谱索引
├── assets/line-art/         # 食材线稿
├── web/                     # 静态表单 PWA
├── scripts/                 # 索引校验与构建工具
└── 参考书籍/                # 本地 7 本书
```

## 维护工具

```powershell
# 校验所有索引文件
python scripts/validate_index.py

# 运行单元测试
python -m pytest scripts/tests/test_validate_index.py -v

# 从《抗炎食谱100例》重建部分索引（可选）
python scripts/build_index.py
```

## 限制（v1）

- ✅ 场景驱动推荐、对话引导、静态表单、食材线稿
- ❌ 拍照识材（v2）
- ❌ 小红书补充（v2）
- ❌ 存储 / 收藏 / 分享
- ⚠️ 调理场景仅供参考，非医疗/营养专业建议

## 风格

- 整体：清新、治愈、极简、自然
- 网页：暖黄色（#FFF8E7）
- 话术：有书卷气，避免网红腔

---

有问题或建议，请查看 `docs/superpowers/specs/2026-08-04-我的菜谱-design.md` 设计规格。
