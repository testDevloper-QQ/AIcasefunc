# 大模型 + 网络搜索配置

索引无匹配食材组合时，Skill 会：

1. **DuckDuckGo** 搜索 `{食材} 家常做法 简单 高频`
2. 将摘要交给 **OpenAI 兼容 API** 结构化输出菜谱
3. 未配置 API 或搜索失败 → 降级离线模板

## 环境变量（文本 LLM，可选）

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | API 密钥（必填才启用 LLM 菜谱） | `sk-...` |
| `OPENAI_BASE_URL` | 兼容接口地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 文本模型 | `gpt-4o-mini` |

## AI 手账插画（默认：Agent 内置出图）

**不需要**用户配置图像 API。Cursor / WorkBuddy Agent 用宿主内置出图能力，Python 只负责 job 列表与落盘。

```bash
# 列出待生成任务（Agent 读 JSON 后出图）
python scripts/illustration_jobs_cli.py --from-recommend -i 鸡肉 -s seasonal --pretty

# Agent 出图后落盘
python scripts/save_illustration.py --recipe-id sea-014 --kind dish --from 路径.png --generator cursor
```

完整流程见 [`agent-illustration-guide.md`](agent-illustration-guide.md)。

## 可选：Headless 图像 API 批量（维护者 / CI）

仅当**无 Agent 会话**、需脚本批量出图时：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_IMAGE_MODEL` | 出图模型 | `dall-e-3` |
| `OPENAI_IMAGE_SIZE` | 尺寸 | `1024x1024` |
| `OPENAI_IMAGE_QUALITY` | dall-e-3 质量 | `standard` |

```powershell
$env:OPENAI_API_KEY = "你的密钥"
py -3 scripts/generate_ai_illustrations.py --top 10 --candidates 1
```

Windows PowerShell 启动 Web + 文本 LLM 示例：

```powershell
$env:OPENAI_API_KEY = "你的密钥"
py -3 scripts/ensure_web_server.py --foreground
```

## 输出要求

- 必须包含用户全部食材
- 中国计量（克/毫升/℃）
- 烹饪 ≤ 60 分钟
