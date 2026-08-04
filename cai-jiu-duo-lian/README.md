# 菜就多练 — 用户使用指南

> 先定场景，再出好菜

## 简介

「菜就多练」是一个 **场景驱动** 的菜谱推荐 Cursor Agent Skill。从预建索引（约 145 道菜，6 大场景）推荐可执行菜谱，帮助上班族、一人食等人群减少「今天吃什么」的决策成本。

## 安装

### 方式一：项目 Skill（推荐）

将整个 Skill 文件夹复制到项目的 `.cursor/skills/` 目录，或在 Cursor 设置中添加 Skill 路径。

### 方式二：个人 Skill

复制到 `~/.cursor/skills/cai-jiu-duo-lian/`（保留 `SKILL.md` 及子目录结构）。

### 方式三：远程 Git 引用

在 `web/config.json` 中配置 `skillSource: "git"` 与仓库地址（见下文「Skill 来源配置」）。

安装后重启 Cursor 或重新加载 Skill，然后验证：

```bash
python scripts/verify_install.py
```

验证通过后会显示 **四种使用场景** 的输入示例。

### 四种使用场景 — 输入示例

| 场景 | 说明 | 对话示例 | CLI 示例 |
|------|------|----------|----------|
| **1. 场景驱动** | 先定饮食偏好 | `轻食，一人食，想吃点清爽的` | `python scripts/recommend_cli.py -s light-meal -i 黄瓜,鸡蛋 --servings 一人食 --pretty` |
| **2. 食材驱动** | 按现有食材找做法 | `有鸡蛋、番茄、黄瓜，能做什么` | `python scripts/recommend_cli.py -i 鸡蛋,番茄,黄瓜 --pretty` |
| **3. 指定需求** | 便当、带饭、指定用途 | `想做一份便当，明天带饭，有鸡胸肉和米饭` | `python scripts/recommend_cli.py -s bento -i 米饭,鸡胸肉 --text 明天带饭 --pretty` |
| **4. 默认快乐餐** | 不选场景，快速解馋 | `有鸡蛋和番茄，来道快手的` | `python scripts/recommend_cli.py -i 鸡蛋,番茄 --pretty` |

> 未选场景时默认「快乐餐」。家乡菜请说明「地方味」或 CLI 加 `-s regional`。详见 `references/getting-started.md`。

## 对话用法

在 Cursor 对话中直接描述需求，Agent 会自动触发 Skill。

### 三种入口（对话内）

> 完整四种场景示例见上文「安装成功 — 四种使用场景」表格。

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
有折耳根和豆花，想吃点家乡味（需点选或说明「地方味」场景）
```

```
不想选场景，有鸡蛋和番茄，来道快手的
```

> **未选场景时**，Skill 与网页均默认按 **「快乐餐」** 推荐。若要家乡菜，请说明或选择 **「地方味」**。

Agent 会先查 `data/recipe-index/`，未命中再读 `参考书籍/` 原文（若本地有）。

## 网页用法（推荐：在线服务）

### 启动服务

**Windows（自动检测 Python）：**

```powershell
cd "我的菜谱skill"
.\scripts\start_web.ps1          # 本机
.\scripts\start_web.ps1 -Lan     # 局域网 + 手机
```

**macOS / Linux：**

```bash
cd "我的菜谱skill"
chmod +x scripts/start_web.sh
./scripts/start_web.sh --lan
```

**跨平台（Agent 可调用，未运行则自动后台启动）：**

```bash
python scripts/ensure_web_server.py
python scripts/ensure_web_server.py --foreground --lan
```

> Python 路径：优先 `PATH` 中的 `python` / `python3`；也可设置环境变量 `CAIJIU_PYTHON` 指向本机解释器。

**大模型联网家常菜谱**（索引无匹配时）：设置 `OPENAI_API_KEY` 后启动服务，详见 `references/llm-config.md`。

```powershell
$env:OPENAI_API_KEY = "你的密钥"
py -3 scripts/ensure_web_server.py --foreground
```

终端会显示本机地址；加 `-Lan` / `--lan` 时显示 **手机局域网地址**（如 `http://192.168.x.x:8765/`）。

### 使用步骤

1. 浏览器打开 `http://127.0.0.1:8765/`
2. **今天想吃什么？**（可选）：便当 / 轻食 / 时令 / 地方味 / 调理 / 快乐餐；不选则默认 **快乐餐**
3. **冰箱里有什么？**：点选示例食材，或在输入框 **自定义食材**（如折耳根、豆花），至少 1 个
4. 可选填写口味、份量、补充说明
5. 点击「开始推荐」→ 页面直接显示 **手账风推荐卡片**（Hero 出餐线稿、食材网格、容器步骤图）

> 不要直接双击 `index.html`（`file://` 无法调用 API）。若页面报错，运行 `python scripts/ensure_web_server.py` 确保服务已启动。

### Agent / WorkBuddy 调用（无需 Web）

远程安装 Skill 后，Agent 应优先用 CLI 推荐，不依赖 Web 服务：

```bash
python scripts/recommend_cli.py -i 鸡蛋,番茄 -s happy --servings 一人食 --pretty
```

### 推荐规则摘要

| 规则 | 说明 |
|------|------|
| 默认场景 | 未选饮食偏好 → **快乐餐** |
| 地方味 | 仅当用户点选「地方味」时优先匹配地域菜 |
| 烹饪时长 | 仅推荐 **≤ 60 分钟** 的菜 |
| 中国计量 | 华氏/盎司/cup 自动转为 **℃ / 克 / 毫升**（见 `references/measurement-cn.md`） |
| 食材份量 | 按 **《中国居民膳食指南（2022）》** 单餐建议换算与核验（见 `references/dietary-guidelines-cn.md`） |
| 批量配方 | 原文「100 公斤」等商用批量会自动换算为家庭份量 |

### Skill 来源配置

编辑 `web/config.json`：

**本地 Skill（默认）：**

```json
{
  "skillSource": "local",
  "localSkillPath": ".."
}
```

**远程 Git 热更新（可选，维护者用）：**

```json
{
  "skillSource": "git",
  "gitRepoUrl": "https://github.com/testDevloper-QQ/AIcasefunc.git",
  "gitBranch": "main",
  "gitSkillSubPath": "cai-jiu-duo-lian"
}
```

> 从 Git **远程安装**的 Skill 包默认 `skillSource: local`，已含完整索引，Agent 可直接调用 `recommend_cli.py`，无需再拉 Git。

验证 Git 链路：

```powershell
python scripts/test_git_skill.py
```

部署到 GitHub（维护者）：

```powershell
python scripts/deploy_to_github.py
```

> 部署脚本会自动排除 `参考书籍/`、`skill生成需求背景.md` 等不影响用户使用的内部文件。

### 安装到手机桌面（PWA）

1. 手机浏览器打开局域网地址
2. 菜单 → 「添加到主屏幕」/「安装应用」
3. 桌面出现「菜就多练」图标，可独立打开

## 输出内容

每道推荐菜包含：

- **Hero 卡片**：菜名、出处、时长/方式/份量/花费徽章、**出餐手绘线稿**
- **食材清单**：按人份，**中国计量**（克/毫升/个），已做家庭份量换算，配食材线稿
- **做法步骤**：**容器场景图**（烤/锅/炒/碗/砧/盘）+ 涉及食材线稿 + 中文步骤
- 可选：0–2 道备选

## 知识库说明

| 类型 | 路径 |
|------|------|
| 索引（优先检索） | `data/recipe-index/*.yaml` |
| 书籍原文（补读） | `参考书籍/`（本地，不随 Git 远程部署） |
| 能力清单 | `references/capabilities.md` |
| 场景路由 | `references/scene-router.md` |
| 输出模板与 QA | `references/output-template.md` |
| 中国计量 | `references/measurement-cn.md` |
| 份量依据 | `references/dietary-guidelines-cn.md` |

当前索引约 **145 道**代表菜，覆盖 6 大场景。

## 目录结构

```
我的菜谱skill/
├── SKILL.md                      # Skill 主逻辑
├── README.md                     # 本指南（用户文档）
├── references/                   # 路由、风格、输出模板、膳食指南
├── data/recipe-index/            # 预建菜谱索引
├── assets/line-art/              # 食材线稿
├── web/                          # 网页 + PWA + config.json
├── scripts/                      # 推荐引擎、Web 服务、部署与测试
└── 参考书籍/                     # 本地书籍（可选，不推远程）
```

## 维护工具

```powershell
# 校验所有索引文件
python scripts/validate_index.py

# 运行单元测试
python -m pytest scripts/tests/ -q

# 从《抗炎食谱100例》重建部分索引（可选）
python scripts/build_index.py
```

## 限制（v1）

- ✅ 场景驱动推荐、在线网页推荐、自定义食材、Hero 出餐图、容器步骤配图、中国计量、膳食指南份量核验
- ✅ Git 远程 Skill 拉取
- ❌ 拍照识材（v2）
- ❌ 小红书补充（v2）
- ❌ 存储 / 收藏 / 分享
- ⚠️ 调理场景仅供参考，非医疗/营养专业建议

## 风格

- 整体：清新、治愈、极简、自然
- 网页：暖黄色（#FFF8E7）
- 话术：有书卷气，避免网红腔

---

设计规格见 `docs/superpowers/specs/2026-08-04-我的菜谱-design.md`（仓库根目录，若存在）。
