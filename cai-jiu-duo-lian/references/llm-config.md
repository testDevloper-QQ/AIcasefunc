# 大模型 + 网络搜索配置

索引无匹配食材组合时，Skill 会：

1. **DuckDuckGo** 搜索 `{食材} 家常做法 简单 高频`
2. 将摘要交给 **OpenAI 兼容 API** 结构化输出菜谱
3. 未配置 API 或搜索失败 → 降级离线模板

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | API 密钥（必填才启用 LLM） | `sk-...` |
| `OPENAI_BASE_URL` | 兼容接口地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 模型 | `gpt-4o-mini` |

Windows PowerShell 启动示例：

```powershell
$env:OPENAI_API_KEY = "你的密钥"
py -3 scripts/ensure_web_server.py --foreground
```

## 输出要求

- 必须包含用户全部食材
- 中国计量（克/毫升/℃）
- 烹饪 ≤ 60 分钟
