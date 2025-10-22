# Telegram MCP Server

> Remote control AI coding assistants (Claude Code / Codex) via Telegram

[![PyPI](https://img.shields.io/pypi/v/telegram-mcp-server)](https://pypi.org/project/telegram-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/telegram-mcp-server)](https://pypi.org/project/telegram-mcp-server/)
[![License](https://img.shields.io/github/license/batianVolyc/telegram-mcp-server)](LICENSE)

English | [简体中文](README-CN.md)

## Why This Project?

Have you ever encountered these scenarios:

- 💤 **Late at night in bed**, you suddenly think of a bug that needs fixing, but don't want to get up and open your laptop?
- 🚇 **On your commute**, you want AI to refactor code for you, but your laptop isn't with you?
- 🏢 **Multiple Claude Code or Codex sessions** running on remote servers, and you want to check their progress anytime?
- ⏰ **Long-running tasks** (testing, building, refactoring) that take hours, but you don't want to sit in front of the computer?

**Telegram MCP Server was created to solve these problems!**

Through the MCP (Model Context Protocol), this project allows you to:
- 📱 **Anytime, anywhere** view and control AI coding assistants via Telegram
- 🔄 **Multi-session management**: Use `screen` on remote servers to manage multiple projects simultaneously
- 🌙 **True unattended mode**: Wait up to 7 days with smart polling, minimal system resources
- 💬 **Simple interaction**: Send messages via Telegram to give AI assistants next instructions

**Perfect for**:
- 24/7 remote servers
- Long-running tasks
- Multi-project parallel development
- Remote work from anywhere

## Features

- 🌙 **True Unattended Mode** - Wait up to 7 days with smart progressive polling
- 📱 **Remote Control** - Control AI assistants from anywhere via Telegram
- 🔄 **Two-way Communication** - Send notifications, receive replies, continuous dialogue
- 📁 **File Operations** - View and download project files
- 🎯 **Multi-session Management** - Manage multiple projects simultaneously
- 🤖 **Universal Support** - Works with both Claude Code and Codex

## ⚡ Quick Start (New Users)

### Installation & Setup (One Command)

```bash
# Use uvx (recommended, no installation needed, always latest version)
uvx --refresh telegram-mcp-server@latest --setup
```

This will:
1. ✅ Download the latest version from PyPI
2. ✅ Guide you through Telegram Bot setup
3. ✅ Auto-configure Claude Code / Codex / Gemini CLI
4. ✅ Test the connection

**That's it!** 🎉

### Verify Installation

```bash
# Check version (should be 0.2.1 or higher)
uvx telegram-mcp-server@latest --version
```

**Expected output**:
```
telegram-mcp-server version 0.2.1
https://github.com/batianVolyc/telegram-mcp-server
```

---

## 📖 Detailed Installation

### Method 1: Using uvx (Recommended)

```bash
# Always use latest version
uvx telegram-mcp-server@latest --setup

# Or using pip
pip install telegram-mcp-server
```

### 2. Setup

#### Option A: Automatic Setup (Recommended)

```bash
telegram-mcp-server --setup
```

Interactive wizard will help you:
- Create Telegram Bot
- Get credentials
- Auto-configure AI assistant

#### Option B: Manual Setup with `mcp add`

If you already have your Telegram Bot Token and Chat ID, you can quickly add using the `mcp add` command:

**Claude Code**:
```bash
claude mcp add \
  --transport stdio \
  telegram \
  --env TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE \
  --env TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE \
  -- \
  uvx telegram-mcp-server
```

**Codex**:
```bash
codex mcp add telegram \
  --env TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE \
  --env TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE \
  -- \
  npx -y telegram-mcp-server
```

**Gemini CLI**:
```bash
gemini mcp add telegram uvx telegram-mcp-server \
  -e TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE \
  -e TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
```

> 💡 **Tip**: Replace `YOUR_TOKEN_HERE` and `YOUR_CHAT_ID_HERE` with your actual values

### 3. Usage

```bash
# Recommended: Start with bypass permissions mode
# Avoid interruptions due to permission confirmations during AI-Telegram interaction
# Note: Cannot run as root due to security mechanisms

# Claude Code
claude --permission-mode bypassPermissions

# Codex
codex --dangerously-bypass-approvals-and-sandbox

# Gemini CLI (YOLO mode - auto-approve all MCP calls)
gemini --yolo

# In the AI assistant
> Enter unattended mode. Task: analyze project structure
```

Check results in Telegram and continue the conversation!

## How It Works

```
AI Assistant (Claude Code/Codex)
  ↓ MCP Protocol
MCP Server (telegram-mcp-server)
  ├─ 8 tools (notify, wait, file operations, etc.)
  └─ Telegram Bot (background process)
      ↓ Telegram API
Your Telegram Client
```

## Core Features

### MCP Tools (8 tools)

- `telegram_notify` - Send structured notifications (recommended)
- `telegram_wait_reply` - Wait for user reply (blocking poll)
- `telegram_unattended_mode` - Unattended mode (smart loop)
- `telegram_send_code` - Send code (with syntax highlighting)
- `telegram_send_image` - Send images
- `telegram_send_file` - Send files
- `telegram_send` - Send free-form messages
- `telegram_get_context_info` - Get session context info

### Telegram Commands (6 commands)

- `/sessions` - List all sessions
- `/status <id>` - Check session status
- `/to <id> <msg>` - Send message to session
- `/file <id> <path>` - View file
- `/delete <id>` - Delete session
- `/help` - Show help

### Smart Polling

Progressive polling strategy, wait up to 7 days:

| Wait Time | Check Frequency | Response Delay |
|-----------|----------------|----------------|
| 0-30 min | Every 30s | Max 30s |
| 30-60 min | Every 60s | Max 60s |
| 1+ hour | Every 120s | Max 120s |

## Use Cases

### Scenario 1: Overnight Tasks

```bash
# 10 PM
> Enter unattended mode. Task: run full test suite and fix all errors

# 8 AM - check results in Telegram
```

### Scenario 2: Remote Work

```bash
# At office
> Enter unattended mode. Task: refactor database access layer

# On the road - monitor and control via Telegram
```

### Scenario 3: Multi-project Management (Remote Server + screen)

```bash
# SSH to remote server
ssh user@server

# Create multiple screen sessions
screen -S project-a
cd /path/to/project-a
TELEGRAM_SESSION="proj-a" claude --permission-mode bypassPermissions
# Ctrl+A D to detach

screen -S project-b
cd /path/to/project-b
TELEGRAM_SESSION="proj-b" codex --dangerously-bypass-approvals-and-sandbox
# Ctrl+A D to detach

# Manage both projects in Telegram
# Sessions keep running even after closing SSH
```

### Scenario 4: Late Night in Bed

```bash
# During the day, start session on server
screen -S night-task
TELEGRAM_SESSION="night-fix" claude --permission-mode bypassPermissions

# At night in bed, send commands via Telegram
/to night-fix Fix null pointer exception in auth.py

# Next morning, check results
/status night-fix
```

## Configuration

### Claude Code

Supports three configuration scopes:

**MCP Server Configuration**:
- **User scope**: `~/.claude.json` - Global config
- **Project scope**: `.mcp.json` - Team shared
- **Local scope**: `.claude.json` - Project specific

**Environment Variables** (auto-configured):
- `~/.claude/settings.json` - Contains `MCP_TOOL_TIMEOUT=604800000` (7-day timeout)

### Codex

Global config: `~/.codex/config.toml`

Auto-includes `tool_timeout_sec = 604800` (7 days timeout)

## Environment Variables

```bash
# Custom session name
TELEGRAM_SESSION="my-task" claude

# Custom max wait time
TELEGRAM_MAX_WAIT=86400 claude  # 24 hours

# Custom poll intervals
TELEGRAM_POLL_INTERVAL="10,30,60" claude
```

## Troubleshooting

### Issue: Telegram Bot Not Responding

```bash
# Check logs
tail -f /tmp/telegram-mcp-server.log

# Quick fix
cd telegram-mcp-server
./quick_fix.sh
```

### Issue: Codex 60s Timeout

```bash
# Auto fix
./fix_codex_timeout.sh
```

### Issue: Session Not Registered

```bash
# Reconfigure
telegram-mcp-server --setup
```

## Documentation

- [Configuration Guide](docs/CONFIGURATION_GUIDE.md) - Detailed configuration
- [Polling Mechanism](docs/POLLING_MECHANISM.md) - Smart polling explained
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues
- [How MCP Works](docs/HOW_MCP_WORKS.md) - Technical architecture

## Requirements

- Python 3.10+
- Claude Code or Codex
- Telegram account

## Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Support

- 🐛 [Report Issues](https://github.com/batianVolyc/telegram-mcp-server/issues)
- 💬 [Discussions](https://github.com/batianVolyc/telegram-mcp-server/discussions)
- ⭐ Star if you find it useful!

---

**Let AI coding assistants work for you, not you waiting for them** 🚀
