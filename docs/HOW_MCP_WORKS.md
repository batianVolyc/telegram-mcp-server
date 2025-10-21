# MCP 工作原理详解

## 🤔 你的疑问

> "只在 `~/.codex/config.toml` 添加配置就能生效吗？MCP 的其他代码在哪里？"

答案：**配置文件只是告诉 AI 助手如何启动 MCP 服务器，实际的服务器代码是独立运行的进程。**

---

## 📚 MCP 架构

### 三个组件

```
┌─────────────────┐
│  AI 助手        │  (Claude Code / Codex)
│  (客户端)       │  - 读取配置文件
└────────┬────────┘  - 启动 MCP 服务器
         │           - 调用 MCP 工具
         │
         │ MCP 协议
         │
┌────────▼────────┐
│  MCP 服务器     │  (telegram-mcp-server)
│  (进程)         │  - 提供工具定义
└────────┬────────┘  - 处理工具调用
         │           - 与外部服务通信
         │
         │ Telegram API
         │
┌────────▼────────┐
│  Telegram Bot   │  (外部服务)
│  (远程)         │  - 接收/发送消息
└─────────────────┘  - 管理会话
```

---

## 🔧 配置文件的作用

### Codex 配置 (`~/.codex/config.toml`)

```toml
[mcp_servers.telegram]
command = "uvx"                    # ← 如何启动服务器
args = ["telegram-mcp-server"]     # ← 启动参数

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "xxx"         # ← 传递给服务器的环境变量
TELEGRAM_CHAT_ID = "yyy"
```

**这个配置文件的作用**：
1. 告诉 Codex："有一个叫 telegram 的 MCP 服务器"
2. 告诉 Codex："用 `uvx telegram-mcp-server` 命令启动它"
3. 告诉 Codex："启动时设置这些环境变量"

### Claude Code 配置 (`~/.claude/mcp.json`)

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "xxx",
        "TELEGRAM_CHAT_ID": "yyy"
      }
    }
  }
}
```

**作用相同**，只是格式不同（JSON vs TOML）。

---

## 🚀 启动流程

### 1. 用户启动 AI 助手

```bash
codex  # 或 claude
```

### 2. AI 助手读取配置

```
Codex 读取: ~/.codex/config.toml
发现: [mcp_servers.telegram]
```

### 3. AI 助手启动 MCP 服务器

```bash
# Codex 在后台执行:
TELEGRAM_BOT_TOKEN="xxx" \
TELEGRAM_CHAT_ID="yyy" \
uvx telegram-mcp-server
```

这个命令实际上运行的是：
```bash
# uvx 会下载并运行 telegram-mcp-server 包
# 相当于:
python -m telegram_mcp_server
```

### 4. MCP 服务器启动

```python
# telegram_mcp_server/__main__.py
async def main():
    # 1. 启动 Telegram Bot
    bot_task = asyncio.create_task(run_telegram_bot())
    
    # 2. 启动 MCP 服务器（stdio）
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, ...)
```

### 5. MCP 服务器注册工具

```python
# telegram_mcp_server/server.py
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="telegram_notify", ...),
        Tool(name="telegram_wait_reply", ...),
        Tool(name="telegram_send_file", ...),
        # ... 其他工具
    ]
```

### 6. AI 助手获取工具列表

```
Codex → MCP 服务器: "列出可用工具"
MCP 服务器 → Codex: "telegram_notify, telegram_wait_reply, ..."
```

### 7. 用户在 Codex 中查看

```bash
> /mcp

# 显示:
telegram (connected)
  - telegram_notify
  - telegram_wait_reply
  - telegram_send_file
  - ...
```

---

## 💬 工具调用流程

### 用户请求

```
用户: "Use telegram_notify to send a test message"
```

### AI 助手决策

```
Codex 分析: 需要调用 telegram_notify 工具
```

### 调用 MCP 工具

```
Codex → MCP 服务器:
{
  "tool": "telegram_notify",
  "arguments": {
    "event": "completed",
    "summary": "Test message",
    "details": ""
  }
}
```

### MCP 服务器处理

```python
# telegram_mcp_server/server.py
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "telegram_notify":
        return await handle_telegram_notify(session, arguments)
```

### 发送到 Telegram

```python
# telegram_mcp_server/server.py
async def handle_telegram_notify(session, arguments):
    # 1. 格式化消息
    message = f"✅ [{session.session_id}]\n{summary}"
    
    # 2. 调用 Telegram API
    await send_telegram_message(chat_id, message)
    
    # 3. 返回结果
    return [TextContent(text="✅ 已发送通知到 Telegram")]
```

### 返回结果

```
MCP 服务器 → Codex: "✅ 已发送通知到 Telegram"
Codex → 用户: "I've sent the notification to Telegram"
```

---

## 📁 代码位置

### 配置文件（告诉 AI 助手如何启动）

```
~/.codex/config.toml        # Codex 配置
~/.claude/mcp.json          # Claude Code 配置（User scope）
.mcp.json                   # Claude Code 配置（Project scope）
.claude/mcp.json            # Claude Code 配置（Local scope）
```

### MCP 服务器代码（实际运行的程序）

```
telegram-mcp-server/
├── telegram_mcp_server/
│   ├── __main__.py         # 入口点，启动服务器
│   ├── server.py           # MCP 工具定义和处理
│   ├── bot.py              # Telegram Bot 逻辑
│   ├── cli.py              # CLI 工具（setup 等）
│   ├── config.py           # 配置管理
│   ├── session.py          # 会话管理
│   └── message_queue.py    # 消息队列
```

### 安装位置（uvx 安装后）

```
~/.local/share/uv/tools/telegram-mcp-server/
└── lib/python3.x/site-packages/telegram_mcp_server/
    ├── __main__.py
    ├── server.py
    ├── bot.py
    └── ...
```

---

## 🔍 验证 MCP 服务器运行

### 查看进程

```bash
# 启动 codex 后，查看进程
ps aux | grep telegram-mcp-server

# 应该看到类似:
python -m telegram_mcp_server
```

### 查看日志

```bash
tail -f /tmp/telegram-mcp-server.log

# 应该看到:
Starting Telegram MCP Server...
Starting Telegram bot...
Starting MCP stdio server...
```

### 测试连接

```bash
# 在 Codex 中
> /mcp

# 应该显示:
telegram (connected)
  Tools: 8
```

---

## 🌐 通信协议

### MCP 协议（stdio）

AI 助手和 MCP 服务器通过标准输入/输出通信：

```
AI 助手 (stdin/stdout) ←→ MCP 服务器 (stdin/stdout)
```

消息格式（JSON-RPC）：

```json
// AI 助手 → MCP 服务器
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "telegram_notify",
    "arguments": {...}
  }
}

// MCP 服务器 → AI 助手
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "✅ 已发送通知"}
    ]
  }
}
```

### Telegram API（HTTP）

MCP 服务器和 Telegram 通过 HTTP API 通信：

```
MCP 服务器 (HTTP) ←→ Telegram API (https://api.telegram.org)
```

---

## 🎯 为什么这样设计？

### 优点

1. **解耦**: AI 助手和外部服务分离
2. **复用**: 一个 MCP 服务器可以被多个 AI 助手使用
3. **安全**: 凭据存储在配置文件，不暴露给 AI
4. **扩展**: 可以轻松添加新工具
5. **标准化**: 遵循 MCP 协议标准

### 类比

就像：
- **配置文件** = 电话号码簿（告诉你如何联系某人）
- **MCP 服务器** = 实际的人（提供服务）
- **MCP 协议** = 电话线（通信方式）
- **Telegram API** = 外部服务（最终目的地）

---

## 📊 完整流程图

```
用户输入
  ↓
┌─────────────────────────────────────────┐
│ Codex / Claude Code                     │
│ 1. 解析用户意图                         │
│ 2. 决定调用 telegram_notify            │
└──────────────┬──────────────────────────┘
               │ MCP 协议 (JSON-RPC)
               │ {"method": "tools/call", ...}
               ↓
┌─────────────────────────────────────────┐
│ MCP 服务器 (telegram-mcp-server)        │
│ 1. 接收工具调用请求                     │
│ 2. 执行 handle_telegram_notify()       │
│ 3. 格式化消息                           │
└──────────────┬──────────────────────────┘
               │ HTTP API
               │ POST /sendMessage
               ↓
┌─────────────────────────────────────────┐
│ Telegram API                            │
│ 1. 接收消息                             │
│ 2. 发送到用户的 Telegram                │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│ 用户的 Telegram 客户端                  │
│ 显示: "✅ [demo] Test message"          │
└─────────────────────────────────────────┘
```

---

## 🔑 关键点总结

1. **配置文件不包含 MCP 服务器代码**
   - 只包含启动命令和参数

2. **MCP 服务器是独立进程**
   - 由 AI 助手启动
   - 通过 stdio 通信

3. **实际代码在 Python 包中**
   - 安装在 `~/.local/share/uv/tools/`
   - 或虚拟环境中

4. **Codex 只支持全局配置**
   - 不支持项目级配置
   - 所有项目共享同一配置

5. **Claude Code 支持多级配置**
   - User scope: 全局
   - Project scope: 项目共享
   - Local scope: 项目本地

---

## 💡 实际例子

### 查看 MCP 服务器在哪里

```bash
# 找到 telegram-mcp-server 的实际位置
which telegram-mcp-server

# 或
uvx --help telegram-mcp-server

# 查看包内容
ls -la ~/.local/share/uv/tools/telegram-mcp-server/
```

### 手动启动 MCP 服务器（测试）

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 手动启动
python -m telegram_mcp_server

# 应该看到:
Starting Telegram MCP Server...
Starting Telegram bot...
Starting MCP stdio server...
```

### 查看 MCP 通信（调试）

```bash
# 启用调试日志
export MCP_DEBUG=1

# 启动 codex
codex

# 查看日志
tail -f /tmp/telegram-mcp-server.log
```

---

**现在明白了吗？配置文件只是"启动说明书"，实际的服务器代码是独立运行的程序！** 🎉
