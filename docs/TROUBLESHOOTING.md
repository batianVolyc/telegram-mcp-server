# 故障排查指南

## 🐛 常见问题

### 问题 1: Telegram Bot 收不到消息 / `/sessions` 命令无响应

**症状**:
- 在 Telegram 发送 `/sessions` 没有响应
- 在 Telegram 发送消息，Codex/Claude Code 收不到
- `telegram_unattended_mode` 工具调用失败

**原因**:
Telegram Bot 进程没有正常启动。

**诊断**:
```bash
# 1. 查看日志
tail -50 /tmp/telegram-mcp-server.log

# 2. 查找错误
grep "ERROR" /tmp/telegram-mcp-server.log

# 3. 检查 Bot 进程
ps aux | grep telegram-mcp-server
```

**常见错误**:

#### 错误 A: `ModuleNotFoundError: No module named 'message_queue'`

```
2025-10-21 14:19:47,217 - __main__ - ERROR - Bot startup error: No module named 'message_queue'
```

**原因**: 项目根目录有旧的 Python 文件（`server.py`, `bot.py` 等），使用了错误的导入方式。

**解决**:
```bash
cd telegram-mcp-server

# 删除旧文件
rm -f __main__.py server.py bot.py config.py session.py message_queue.py

# 重新安装
./venv/bin/pip install -e . --force-reinstall --no-deps

# 杀掉旧进程
pkill -f telegram-mcp-server
rm -f /tmp/telegram-mcp-bot.lock

# 重启 Codex/Claude Code
```

#### 错误 B: `Bot already running in another process`

```
2025-10-21 14:52:35,535 - __main__ - INFO - Telegram bot already running in another process (PID: 25057)
```

**原因**: 有旧的 Bot 进程在运行，但可能已经失效。

**解决**:
```bash
# 查找进程
ps aux | grep telegram-mcp-server

# 杀掉进程
kill <PID>

# 删除锁文件
rm -f /tmp/telegram-mcp-bot.lock

# 重启 Codex/Claude Code
```

---

### 问题 2: `telegram_unattended_mode` 工具调用失败

**症状**:
```
Error: tool call error: tool call failed for `telegram/telegram_unattended_mode`
```

**原因**: Telegram Bot 没有运行，无法处理消息队列。

**解决**: 参考问题 1 的解决方案。

---

### 问题 3: 会话注册成功，但收不到 Telegram 消息

**症状**:
- 日志显示: `Registered session: codex-project`
- 日志显示: `HTTP Request: POST https://api.telegram.org/bot.../sendMessage "HTTP/1.1 200 OK"`
- 但 Telegram 没有收到消息

**诊断**:
```bash
# 检查 Bot Token 和 Chat ID
cat ~/.codex/config.toml | grep -A 5 telegram

# 或
cat ~/.claude/mcp.json | grep -A 10 telegram
```

**解决**:
1. 确认 Bot Token 正确
2. 确认 Chat ID 正确
3. 在 Telegram 中向 bot 发送 `/start`
4. 重新运行 setup: `telegram-mcp-server --setup`

---

### 问题 4: 多个 MCP 服务器实例冲突

**症状**:
- 日志显示多个 "Starting Telegram MCP Server"
- 有些实例说 "bot already running"

**原因**: 同时启动了多个 Codex/Claude Code 实例。

**解决**:
```bash
# 1. 关闭所有 Codex/Claude Code
# 按 Ctrl+C 或 Ctrl+D

# 2. 清理进程
pkill -f telegram-mcp-server
pkill -f codex
pkill -f claude

# 3. 清理锁文件
rm -f /tmp/telegram-mcp-bot.lock

# 4. 重新启动一个实例
codex  # 或 claude
```

---

## 🔍 诊断工具

### 检查 MCP 服务器状态

```bash
# 查看最新日志
tail -f /tmp/telegram-mcp-server.log

# 查看错误
grep "ERROR" /tmp/telegram-mcp-server.log | tail -10

# 查看 Bot 启动
grep "Starting Telegram bot" /tmp/telegram-mcp-server.log | tail -5
```

### 检查进程

```bash
# 查找 MCP 服务器进程
ps aux | grep telegram-mcp-server

# 查找 Python 进程
ps aux | grep python | grep telegram

# 查看进程详情
ps -p <PID> -f
```

### 检查配置

```bash
# Codex 配置
cat ~/.codex/config.toml

# Claude Code 配置
cat ~/.claude/mcp.json

# 或项目级配置
cat .mcp.json
cat .claude/mcp.json
```

### 测试 Telegram 连接

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 测试发送消息
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=Test message"
```

---

## 🛠️ 完整重置流程

如果所有方法都不行，执行完整重置：

```bash
# 1. 停止所有进程
pkill -f telegram-mcp-server
pkill -f codex
pkill -f claude

# 2. 清理文件
rm -f /tmp/telegram-mcp-server.log
rm -f /tmp/telegram-mcp-bot.lock
rm -f ~/.claude/telegram-mcp-sessions.json
rm -f ~/.claude/telegram-mcp-queue.json

# 3. 删除旧的 Python 文件（如果存在）
cd telegram-mcp-server
rm -f __main__.py server.py bot.py config.py session.py message_queue.py

# 4. 重新安装
./venv/bin/pip install -e . --force-reinstall

# 5. 重新配置
./venv/bin/telegram-mcp-server --setup

# 6. 重启
codex  # 或 claude
```

---

## 📊 正常工作的标志

### 日志应该显示

```
2025-10-21 XX:XX:XX - __main__ - INFO - Starting Telegram MCP Server...
2025-10-21 XX:XX:XX - __main__ - INFO - Starting Telegram bot (first instance)...
2025-10-21 XX:XX:XX - __main__ - INFO - Starting MCP stdio server...
```

**没有** ERROR 信息。

### Telegram Bot 命令应该工作

```
/sessions  → 显示会话列表
/help      → 显示帮助信息
```

### MCP 工具应该工作

在 Codex/Claude Code 中：
```
> /mcp
telegram (connected)
  Tools: 8
```

调用工具：
```
> Use telegram_notify to send a test message
✅ 已发送通知到 Telegram
```

---

## 💡 预防措施

### 1. 不要在项目根目录放置 Python 文件

❌ 错误:
```
telegram-mcp-server/
├── server.py          ← 会导致导入冲突
├── bot.py             ← 会导致导入冲突
└── telegram_mcp_server/
    ├── server.py      ← 正确的文件
    └── bot.py         ← 正确的文件
```

✅ 正确:
```
telegram-mcp-server/
├── telegram_mcp_server/
│   ├── server.py      ← 所有代码在这里
│   └── bot.py
└── test_config.py     ← 测试脚本可以在根目录
```

### 2. 使用一个 AI 助手实例

同时运行多个 Codex/Claude Code 实例会导致冲突。

### 3. 定期清理

```bash
# 每天清理一次
rm -f /tmp/telegram-mcp-bot.lock
rm -f ~/.claude/telegram-mcp-sessions.json
rm -f ~/.claude/telegram-mcp-queue.json
```

---

## 📞 获取帮助

如果问题仍然存在：

1. **收集信息**:
   ```bash
   # 保存日志
   cp /tmp/telegram-mcp-server.log ~/telegram-mcp-debug.log
   
   # 保存配置
   cat ~/.codex/config.toml > ~/codex-config.txt
   cat ~/.claude/mcp.json > ~/claude-config.txt
   
   # 保存进程信息
   ps aux | grep telegram > ~/telegram-processes.txt
   ```

2. **创建 Issue**: https://github.com/batianVolyc/telegram-mcp-server/issues

3. **包含信息**:
   - 操作系统
   - Python 版本
   - AI 助手（Codex/Claude Code）
   - 错误日志
   - 配置文件（隐藏敏感信息）

---

**记住**: 大多数问题都是因为旧的 Python 文件或进程冲突导致的。删除旧文件并重启通常能解决问题！
