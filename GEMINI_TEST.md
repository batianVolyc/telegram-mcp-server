# Gemini CLI MCP 添加测试指南

## ✅ 正确的命令格式

### 完整命令

```bash
gemini mcp add \
  -t stdio \
  -e TELEGRAM_BOT_TOKEN=8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k \
  -e TELEGRAM_CHAT_ID=7021932416 \
  telegram \
  uvx \
  telegram-mcp-server
```

### 简化版（默认 stdio）

```bash
gemini mcp add \
  -e TELEGRAM_BOT_TOKEN=8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k \
  -e TELEGRAM_CHAT_ID=7021932416 \
  telegram \
  uvx \
  telegram-mcp-server
```

## 🔍 命令解析

```
gemini mcp add [options] <name> <commandOrUrl> [args...]
                          ^^^^^^  ^^^^^^^^^^^^  ^^^^^^^
                          telegram    uvx       telegram-mcp-server
```

**参数说明**：
- `<name>`: `telegram` - MCP 服务器名称
- `<commandOrUrl>`: `uvx` - 启动命令
- `[args...]`: `telegram-mcp-server` - 命令参数

**选项说明**：
- `-t stdio`: 传输类型（默认就是 stdio，可省略）
- `-e KEY=VALUE`: 环境变量（可以多次使用）

## ❌ 常见错误

### 错误 1：使用 `--` 分隔符

```bash
# ❌ 错误
gemini mcp add telegram \
  --env TELEGRAM_BOT_TOKEN=xxx \
  --env TELEGRAM_CHAT_ID=xxx \
  -- \
  uvx telegram-mcp-server
```

**问题**：Gemini CLI 不需要 `--` 分隔符

### 错误 2：使用 `--env` 而不是 `-e`

```bash
# ❌ 错误
gemini mcp add telegram uvx \
  --env TELEGRAM_BOT_TOKEN=xxx \
  --env TELEGRAM_CHAT_ID=xxx \
  telegram-mcp-server
```

**问题**：应该使用 `-e` 而不是 `--env`

### 错误 3：参数顺序错误

```bash
# ❌ 错误
gemini mcp add \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx \
  uvx \
  telegram \
  telegram-mcp-server
```

**问题**：`<name>` 必须在 `<commandOrUrl>` 之前

## 🧪 验证步骤

### 1. 添加 MCP 服务器

```bash
gemini mcp add \
  -e TELEGRAM_BOT_TOKEN=8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k \
  -e TELEGRAM_CHAT_ID=7021932416 \
  telegram \
  uvx \
  telegram-mcp-server
```

**预期输出**：
```
✓ Successfully added MCP server 'telegram'
```

### 2. 列出 MCP 服务器

```bash
gemini mcp list
```

**预期输出**：
```
MCP Servers:
  telegram (stdio)
    Command: uvx telegram-mcp-server
    Status: Connected
```

### 3. 查看服务器详情

```bash
gemini mcp get telegram
```

**预期输出**：
```
Server: telegram
Transport: stdio
Command: uvx
Args: telegram-mcp-server
Environment:
  TELEGRAM_BOT_TOKEN: 8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k
  TELEGRAM_CHAT_ID: 7021932416
Status: Connected
Tools: 8
```

### 4. 测试 MCP 工具

```bash
gemini
```

在 Gemini CLI 中：
```
> List available tools
```

**预期输出**：应该看到 8 个 telegram 工具：
- telegram_notify
- telegram_wait_reply
- telegram_unattended_mode
- telegram_send_code
- telegram_send_image
- telegram_send_file
- telegram_send
- telegram_get_context_info

### 5. 测试发送通知

```
> Use telegram_notify to send a test message
```

**预期结果**：在 Telegram 收到测试消息

## 📝 配置文件位置

Gemini CLI 的配置保存在：
```
~/.gemini/settings.json
```

或者项目级配置：
```
.gemini/settings.json
```

### 查看配置

```bash
cat ~/.gemini/settings.json
```

**预期内容**：
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k",
        "TELEGRAM_CHAT_ID": "7021932416"
      }
    }
  }
}
```

## 🔧 故障排查

### 问题 1：命令未找到

**错误**：
```
uvx: command not found
```

**解决**：
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 npx
gemini mcp add \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx \
  telegram \
  npx \
  -y telegram-mcp-server
```

### 问题 2：MCP 服务器无法连接

**错误**：
```
Failed to connect to MCP server 'telegram'
```

**解决**：
```bash
# 检查 telegram-mcp-server 是否已安装
pip list | grep telegram-mcp-server

# 如果未安装
pip install telegram-mcp-server

# 或使用 uv
uv tool install telegram-mcp-server
```

### 问题 3：环境变量未生效

**症状**：MCP 服务器启动但无法连接 Telegram

**解决**：
```bash
# 检查配置文件
cat ~/.gemini/settings.json

# 确认 env 字段存在且正确
# 如果不正确，删除并重新添加
gemini mcp remove telegram
gemini mcp add -e TELEGRAM_BOT_TOKEN=xxx -e TELEGRAM_CHAT_ID=xxx telegram uvx telegram-mcp-server
```

## 📊 与其他工具的对比

| 工具 | 分隔符 | 环境变量 | 命令格式 |
|------|--------|---------|---------|
| Claude Code | `--` | `--env` | `claude mcp add --transport stdio name --env KEY=VAL -- cmd` |
| Codex | `--` | `--env` | `codex mcp add name --env KEY=VAL -- cmd` |
| Gemini CLI | ❌ 无 | `-e` | `gemini mcp add -e KEY=VAL name cmd args` |

**关键差异**：
- ✅ Gemini CLI 不需要 `--` 分隔符
- ✅ 使用 `-e` 而不是 `--env`
- ✅ 参数顺序：`name` → `command` → `args`

---

**测试完成后，请反馈结果！** 🎉
