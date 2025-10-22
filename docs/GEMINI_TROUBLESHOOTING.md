# Gemini CLI 故障排查指南

## 🐛 问题：Telegram Bot 发送消息，Gemini 没有反应

### 症状

1. ✅ Gemini 成功调用 `telegram_notify_with_actions`
2. ✅ Telegram 收到消息和按钮
3. ❌ 在 Telegram 中发送回复，Gemini 没有反应
4. ❌ `telegram_wait_reply` 似乎没有工作

### 原因分析

从你的截图看到：
```
✅ 已发送通知到 Telegram (会话: tt, 包含 3 个操作按钮)

⏸️ telegram_wait_reply (telegram MCP Server) {}
Determining Script Purpose
(esc to cancel, 3m 30s)
```

**问题**：Gemini CLI 在等待 `telegram_wait_reply` 返回，但是：
1. Gemini 的 MCP 工具超时设置可能太短
2. 消息队列可能没有正确工作
3. 会话 ID 可能不匹配

---

## 🔍 诊断步骤

### 1. 检查 Gemini MCP 配置

查看配置文件：
```bash
cat ~/.gemini/settings.json
```

应该包含：
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server@latest"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      },
      "timeout": 604800000
    }
  }
}
```

**关键**：`timeout` 必须设置为 `604800000`（7天，单位毫秒）

### 2. 检查会话 ID

在 Telegram 中发送：
```
/sessions
```

应该看到会话列表，例如：
```
📋 活跃会话：

1️⃣ ▶️ `tt`
   📁 `/path/to/project`
   🕐 1分钟前
```

确认会话 ID 是 `tt`。

### 3. 检查消息队列

在 Telegram 中发送消息到会话：
```
/to tt 测试消息
```

应该看到：
```
✅ 消息已发送到 `tt`

💬 测试消息
```

### 4. 检查 Gemini 日志

查看 MCP 服务器日志：
```bash
tail -f /tmp/telegram-mcp-server.log
```

应该看到类似：
```
Session tt waiting for reply (max 604800s)
Session tt polling (interval=30s, elapsed=0s)
Session tt received reply: 测试消息
```

---

## 🔧 解决方案

### 方案 1: 增加 Gemini 超时时间

编辑 `~/.gemini/settings.json`：
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server@latest"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      },
      "timeout": 604800000
    }
  }
}
```

**重要**：
- `timeout` 单位是**毫秒**
- `604800000` = 7天
- 如果没有设置，默认可能只有 30 秒

### 方案 2: 使用 `telegram_unattended_mode`

不要直接使用 `telegram_wait_reply`，而是使用 `telegram_unattended_mode`：

在 Gemini 中：
```
进入无人值守模式，任务：分析项目结构
```

Gemini 应该：
1. 执行任务
2. 调用 `telegram_notify` 发送结果
3. 调用 `telegram_unattended_mode` 等待下一步指令
4. 收到指令后继续执行

### 方案 3: 手动测试消息队列

在 Gemini 运行时，打开另一个终端：

```bash
# 查看会话
python3 << 'EOF'
import json
from pathlib import Path

sessions_file = Path.home() / ".telegram-mcp-sessions.json"
if sessions_file.exists():
    with open(sessions_file) as f:
        sessions = json.load(f)
    print(json.dumps(sessions, indent=2))
else:
    print("No sessions file")
EOF

# 查看消息队列
python3 << 'EOF'
import json
from pathlib import Path

queue_file = Path.home() / ".telegram-mcp-queue.json"
if queue_file.exists():
    with open(queue_file) as f:
        queue = json.load(f)
    print(json.dumps(queue, indent=2))
else:
    print("No queue file")
EOF
```

### 方案 4: 重启 Gemini 和 MCP 服务器

```bash
# 1. 停止 Gemini（Ctrl+C）

# 2. 清理旧会话
rm ~/.telegram-mcp-sessions.json
rm ~/.telegram-mcp-queue.json

# 3. 重启 Gemini
gemini --yolo

# 4. 在 Telegram 中测试
/sessions
```

---

## 🧪 测试流程

### 完整测试步骤

1. **启动 Gemini**：
   ```bash
   gemini --yolo
   ```

2. **在 Gemini 中**：
   ```
   使用 telegram_notify 发送一条测试消息
   ```

3. **在 Telegram 中**：
   应该收到消息

4. **在 Gemini 中**：
   ```
   使用 telegram_wait_reply 等待我的回复，最多等待 60 秒
   ```

5. **在 Telegram 中**：
   ```
   /to tt 收到了
   ```

6. **在 Gemini 中**：
   应该显示：
   ```
   用户回复: 收到了
   ```

---

## 📊 常见问题

### Q1: Gemini 显示 "Determining Script Purpose" 然后超时

**原因**：Gemini 的 MCP 超时设置太短

**解决**：
1. 编辑 `~/.gemini/settings.json`
2. 添加 `"timeout": 604800000`
3. 重启 Gemini

### Q2: Telegram 发送消息后，Gemini 没有任何反应

**原因**：会话 ID 不匹配或消息队列问题

**解决**：
1. 在 Telegram 中发送 `/sessions` 确认会话 ID
2. 使用 `/to <session_id> <消息>` 明确指定会话
3. 检查日志：`tail -f /tmp/telegram-mcp-server.log`

### Q3: Gemini 说"已发送"，但 Telegram 没收到

**原因**：Bot Token 或 Chat ID 配置错误

**解决**：
1. 检查配置：`cat ~/.gemini/settings.json`
2. 测试 Bot：`curl -s "https://api.telegram.org/bot<TOKEN>/getMe"`
3. 重新运行 setup：`uvx telegram-mcp-server@latest --setup`

---

## 🎯 推荐配置

### Gemini CLI 最佳配置

`~/.gemini/settings.json`:
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server@latest"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-bot-token",
        "TELEGRAM_CHAT_ID": "your-chat-id",
        "TELEGRAM_SESSION": "gemini-project"
      },
      "timeout": 604800000
    }
  }
}
```

**关键配置**：
- `timeout: 604800000` - 7天超时（毫秒）
- `TELEGRAM_SESSION` - 自定义会话名称
- `@latest` - 始终使用最新版本

### 启动命令

```bash
# 使用 YOLO 模式（自动批准所有 MCP 调用）
gemini --yolo

# 或者在项目目录中
cd /path/to/project
TELEGRAM_SESSION=my-project gemini --yolo
```

---

## 🔗 相关资源

- **Gemini CLI 文档**: https://github.com/google/generative-ai-cli
- **MCP 协议**: https://modelcontextprotocol.io/
- **问题反馈**: https://github.com/batianVolyc/telegram-mcp-server/issues

---

## 💡 调试技巧

### 启用详细日志

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 启动 Gemini
gemini --yolo
```

### 实时监控

```bash
# 终端 1: 运行 Gemini
gemini --yolo

# 终端 2: 监控日志
tail -f /tmp/telegram-mcp-server.log

# 终端 3: 监控会话文件
watch -n 1 'cat ~/.telegram-mcp-sessions.json 2>/dev/null | python3 -m json.tool'
```

---

**如果问题仍然存在，请提供**：
1. Gemini 版本：`gemini --version`
2. 配置文件：`cat ~/.gemini/settings.json`
3. 日志文件：`tail -100 /tmp/telegram-mcp-server.log`
4. 会话信息：在 Telegram 中发送 `/sessions`

在 GitHub 提交 Issue：https://github.com/batianVolyc/telegram-mcp-server/issues
