# Codex 超时问题修复

## 🐛 问题

Codex 调用 `telegram_unattended_mode` 工具时，大约 60 秒后报错：

```
Error: tool call error: tool call failed for `telegram/telegram_unattended_mode`
```

## 🔍 原因

Codex 对 MCP 工具调用有**默认超时限制**（约 60 秒）。

`telegram_unattended_mode` 工具会持续等待用户回复（可能等待数小时），超过 Codex 的默认超时时间。

## ✅ 解决方案

在 Codex 配置中增加 `tool_timeout_sec` 参数。

### 步骤 1: 编辑配置文件

```bash
# 打开 Codex 配置文件
vim ~/.codex/config.toml

# 或使用 Codex IDE 扩展
# 点击齿轮图标 → MCP settings → Open config.toml
```

### 步骤 2: 添加超时配置

找到 `[mcp_servers.telegram]` 部分，添加 `tool_timeout_sec`:

```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
tool_timeout_sec = 3600  # ← 添加这一行（1 小时）

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### 步骤 3: 重启 Codex

```bash
# 关闭当前 Codex
# 按 Ctrl+C 或 Ctrl+D

# 重新启动
codex
```

## 📊 超时时间建议

| 使用场景 | 推荐超时 | 说明 |
|---------|---------|------|
| 快速交互 | 1800 秒（30 分钟） | 短时间等待回复 |
| 一般使用 | 3600 秒（1 小时） | 推荐设置 |
| 长时间任务 | 86400 秒（24 小时） | 过夜任务 |
| **完整无人值守** | **604800 秒（7 天）** | **最大等待时间** |

**注意**: 本 MCP 服务器的默认最长等待时间是 7 天（604800 秒），使用渐进式轮询：
- 前 30 分钟：每 30 秒检查一次
- 30 分钟 - 1 小时：每 60 秒检查一次
- 1 小时以上：每 120 秒检查一次

如果你希望使用完整的 7 天等待功能，需要设置 `tool_timeout_sec = 604800`。

## 🧪 验证修复

### 1. 检查配置

```bash
cat ~/.codex/config.toml | grep -A 5 telegram
```

应该看到：
```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
tool_timeout_sec = 3600
```

### 2. 测试无人值守模式

启动 Codex：
```bash
cd ~/cli/codex-project
codex
```

在 Codex 中：
```
> 进入无人值守模式，发送 "hello codex"
```

**预期行为**:
- ✅ 发送通知到 Telegram
- ✅ 进入等待状态（不报错）
- ✅ 持续轮询 Telegram（每 10 秒）
- ✅ 可以等待超过 60 秒

在 Telegram 回复：
```
继续执行
```

Codex 应该收到回复并继续！

### 3. 监控日志

```bash
tail -f /tmp/telegram-mcp-server.log
```

应该看到持续的轮询：
```
2025-10-21 15:17:20 - HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
2025-10-21 15:17:30 - HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
2025-10-21 15:17:40 - HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
...
```

## 🔧 完整配置示例

### 基础配置

```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
tool_timeout_sec = 3600

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "8472362221:AAEH0LfjvwYBA9dnK9R6Mw1LGB7c6gh899k"
TELEGRAM_CHAT_ID = "702154416"
```

### 高级配置

```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
startup_timeout_sec = 30      # 启动超时（可选）
tool_timeout_sec = 7200       # 工具超时（2 小时）

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
TELEGRAM_MAX_WAIT = "7200"    # 最长等待时间（匹配 tool_timeout_sec）
TELEGRAM_POLL_INTERVAL = "30,60,120"  # 轮询间隔
```

## 📝 注意事项

### 1. 超时时间要合理

- ❌ 太短（< 300 秒）: 无人值守模式无法正常工作
- ✅ 适中（3600 秒）: 推荐，适合大多数场景
- ⚠️ 太长（> 86400 秒）: 可能导致 Codex 长时间挂起

### 2. 匹配环境变量

`tool_timeout_sec` 应该 >= `TELEGRAM_MAX_WAIT`:

```toml
tool_timeout_sec = 3600

[mcp_servers.telegram.env]
TELEGRAM_MAX_WAIT = "3600"  # 或更小
```

### 3. Claude Code 不需要此配置

Claude Code 没有工具超时限制，不需要配置 `tool_timeout_sec`。

## 🆚 Claude Code vs Codex

| 特性 | Claude Code | Codex |
|------|-------------|-------|
| 工具超时 | ❌ 无限制 | ✅ 可配置 |
| 默认超时 | - | ~60 秒 |
| 配置方式 | - | `tool_timeout_sec` |
| 无人值守 | ✅ 开箱即用 | ⚠️ 需要配置 |

## 🐛 故障排查

### 问题: 配置后仍然超时

**检查**:
```bash
# 1. 确认配置已保存
cat ~/.codex/config.toml | grep tool_timeout_sec

# 2. 确认 Codex 已重启
ps aux | grep codex

# 3. 查看日志
tail -f /tmp/telegram-mcp-server.log
```

**解决**:
1. 确保配置文件格式正确（TOML 语法）
2. 完全退出 Codex 并重启
3. 增加超时时间

### 问题: 配置文件格式错误

**错误示例**:
```toml
[mcp_servers.telegram]
tool_timeout_sec = "3600"  # ❌ 错误：不要用引号
```

**正确示例**:
```toml
[mcp_servers.telegram]
tool_timeout_sec = 3600  # ✅ 正确：数字不用引号
```

### 问题: 仍然在 60 秒后断开

**可能原因**:
1. 配置未生效（Codex 未重启）
2. 配置文件位置错误
3. 使用了错误的 MCP 服务器名称

**验证**:
```bash
# 检查 Codex 是否读取了配置
codex mcp list

# 应该显示 telegram 服务器
```

## 📚 相关文档

- [Codex MCP 文档](https://developers.openai.com/codex/mcp/)
- [配置指南](CONFIGURATION_GUIDE.md)
- [故障排查](TROUBLESHOOTING.md)

---

**配置完成后，Codex 的无人值守模式应该能正常工作了！** 🎉
