# Telegram MCP Server

> 通过 Telegram 远程控制 AI 编程助手（Claude Code / Codex）

[![PyPI](https://img.shields.io/pypi/v/telegram-mcp-server)](https://pypi.org/project/telegram-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/telegram-mcp-server)](https://pypi.org/project/telegram-mcp-server/)
[![License](https://img.shields.io/github/license/batianVolyc/telegram-mcp-server)](LICENSE)

[English](README.md) | 简体中文

## 为什么需要这个项目？

你是否遇到过这些场景：

- 💤 **深夜躺在床上**，突然想到一个需要修复的 bug，但不想起床打开电脑？
- 🚇 **通勤路上**，想让 AI 助手帮你重构代码，但笔记本电脑不在身边？
- 🏢 **远程服务器**上运行着多个 Claude Code 或 Codex 会话，想随时查看进度？
- ⏰ **长时间任务**（测试、构建、重构）需要几小时，但你不想一直守在电脑前？

**Telegram MCP Server 就是为了解决这些问题而生！**

通过 MCP（Model Context Protocol）协议，这个项目让你可以：
- 📱 **随时随地**通过 Telegram 查看和控制 AI 编程助手
- 🔄 **多会话管理**：在远程服务器上用 `screen` 多开会话，同时管理多个项目
- 🌙 **真正的无人值守**：最长等待 7 天，智能轮询，不占用系统资源
- 💬 **简单交互**：通过 Telegram 发送消息，给 AI 助手下一步指示

**特别适合**：
- 24/7 运转的远程服务器
- 需要长时间执行的任务
- 多项目并行开发
- 随时随地的远程工作

## 特性

- 🌙 **真正的无人值守** - 最长等待 7 天，智能渐进式轮询
- 📱 **远程控制** - 通过 Telegram 随时随地控制 AI 助手
- 🔄 **双向通信** - 发送通知，接收回复，持续对话
- 📁 **文件操作** - 查看、下载项目文件
- 🎯 **多会话管理** - 同时管理多个项目
- 🤖 **通用支持** - 同时支持 Claude Code 和 Codex

## 快速开始

### 1. 安装

```bash
# 推荐：使用 uv
uv tool install telegram-mcp-server

# 或使用 pip
pip install telegram-mcp-server
```

### 2. 配置

#### 方式 A：自动配置（推荐）

```bash
telegram-mcp-server --setup
```

交互式向导会帮你：
- 创建 Telegram Bot
- 获取凭据
- 自动配置 AI 助手

#### 方式 B：使用 `mcp add` 命令手动添加

如果你已经有 Telegram Bot Token 和 Chat ID，可以使用 `mcp add` 命令快速添加：

**Claude Code**:
```bash
claude mcp add \
  --transport stdio \
  telegram \
  --env TELEGRAM_BOT_TOKEN=你的TOKEN \
  --env TELEGRAM_CHAT_ID=你的CHAT_ID \
  -- \
  uvx telegram-mcp-server
```

**Codex**:
```bash
codex mcp add telegram \
  --env TELEGRAM_BOT_TOKEN=你的TOKEN \
  --env TELEGRAM_CHAT_ID=你的CHAT_ID \
  -- \
  npx -y telegram-mcp-server
```

**Gemini CLI**:
```bash
gemini mcp add \
  -t stdio \
  -e TELEGRAM_BOT_TOKEN=你的TOKEN \
  -e TELEGRAM_CHAT_ID=你的CHAT_ID \
  telegram \
  uvx \
  telegram-mcp-server
```

> 💡 **提示**：将 `你的TOKEN` 和 `你的CHAT_ID` 替换为你的实际值

### 3. 使用

```bash
# 推荐：使用免确认完整授权模式启动
# 避免因权限确认导致 AI 助手与 Telegram 双向互动被意外打断
# 注意：因安全机制无法在 root 身份下启动

# Claude Code
claude --permission-mode bypassPermissions

# Codex
codex --dangerously-bypass-approvals-and-sandbox

# 在 AI 助手中
> 进入无人值守模式。任务：分析项目结构
```

在 Telegram 查看结果并继续对话！

## 工作原理

```
AI 助手 (Claude Code/Codex)
  ↓ MCP 协议
MCP 服务器 (telegram-mcp-server)
  ├─ 8 个工具（通知、等待、文件等）
  └─ Telegram Bot（后台运行）
      ↓ Telegram API
你的 Telegram 客户端
```

## 核心功能

### MCP 工具（8 个）

- `telegram_notify` - 发送结构化通知（推荐使用）
- `telegram_wait_reply` - 等待用户回复（阻塞式轮询）
- `telegram_unattended_mode` - 无人值守模式（智能循环）
- `telegram_send_code` - 发送代码（带语法高亮）
- `telegram_send_image` - 发送图片
- `telegram_send_file` - 发送文件
- `telegram_send` - 发送自由格式消息
- `telegram_get_context_info` - 获取会话上下文信息

### Telegram 命令（6 个）

- `/sessions` - 列出所有会话
- `/status <id>` - 查看会话状态
- `/to <id> <msg>` - 发送消息到会话
- `/file <id> <path>` - 查看文件
- `/delete <id>` - 删除会话
- `/help` - 显示帮助

### 智能轮询

渐进式轮询策略，最长等待 7 天：

| 等待时长 | 检查频率 | 响应延迟 |
|---------|---------|---------|
| 0-30 分钟 | 每 30 秒 | 最多 30 秒 |
| 30-60 分钟 | 每 60 秒 | 最多 60 秒 |
| 1 小时以上 | 每 120 秒 | 最多 120 秒 |

## 使用场景

### 场景 1: 过夜任务

```bash
# 晚上 10 点
> 进入无人值守模式。任务：运行完整测试套件，修复所有错误

# 早上 8 点在 Telegram 查看结果
```

### 场景 2: 远程工作

```bash
# 在办公室启动任务
> 进入无人值守模式。任务：重构数据库访问层

# 在路上通过 Telegram 查看进度和控制
```

### 场景 3: 多项目管理（远程服务器 + screen）

```bash
# SSH 到远程服务器
ssh user@server

# 创建多个 screen 会话
screen -S project-a
cd /path/to/project-a
TELEGRAM_SESSION="proj-a" claude --permission-mode bypassPermissions
# Ctrl+A D 分离会话

screen -S project-b
cd /path/to/project-b
TELEGRAM_SESSION="proj-b" codex --dangerously-bypass-approvals-and-sandbox
# Ctrl+A D 分离会话

# 在 Telegram 同时管理两个项目
# 即使关闭 SSH 连接，会话依然运行
```

### 场景 4: 深夜躺在床上

```bash
# 白天在服务器上启动会话
screen -S night-task
TELEGRAM_SESSION="night-fix" claude --permission-mode bypassPermissions

# 晚上躺在床上，通过 Telegram 发送指令
/to night-fix 修复 auth.py 的空指针异常

# 第二天早上查看结果
/status night-fix
```

## 配置

### Claude Code

支持三种配置范围：

**MCP 服务器配置**：
- **User scope**: `~/.claude.json` - 全局配置
- **Project scope**: `.mcp.json` - 团队共享
- **Local scope**: `.claude.json` - 项目特定

**环境变量配置**（自动设置）：
- `~/.claude/settings.json` - 包含 `MCP_TOOL_TIMEOUT=604800000`（7天超时）

### Codex

全局配置：`~/.codex/config.toml`

自动包含 `tool_timeout_sec = 604800`（7 天超时）

## 环境变量

```bash
# 自定义会话名
TELEGRAM_SESSION="my-task" claude

# 自定义最长等待时间
TELEGRAM_MAX_WAIT=86400 claude  # 24 小时

# 自定义轮询间隔
TELEGRAM_POLL_INTERVAL="10,30,60" claude
```

## 故障排查

### 问题：Telegram Bot 无响应

```bash
# 查看日志
tail -f /tmp/telegram-mcp-server.log

# 快速修复
cd telegram-mcp-server
./quick_fix.sh
```

### 问题：Codex 60 秒超时

```bash
# 自动修复
./fix_codex_timeout.sh
```

### 问题：会话未注册

```bash
# 重新配置
telegram-mcp-server --setup
```

## 文档

- [配置指南](docs/CONFIGURATION_GUIDE.md) - 详细配置说明
- [轮询机制](docs/POLLING_MECHANISM.md) - 智能轮询原理
- [故障排查](docs/TROUBLESHOOTING.md) - 常见问题解决
- [MCP 工作原理](docs/HOW_MCP_WORKS.md) - 技术架构

## 系统要求

- Python 3.10+
- Claude Code 或 Codex
- Telegram 账号

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 支持

- 🐛 [报告问题](https://github.com/batianVolyc/telegram-mcp-server/issues)
- 💬 [讨论](https://github.com/batianVolyc/telegram-mcp-server/discussions)
- ⭐ 如果觉得有用，请给个 Star！

---

**让 AI 编程助手为你工作，而不是你守着它工作** 🚀
