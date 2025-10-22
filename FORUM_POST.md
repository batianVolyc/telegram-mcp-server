# 🚀 开源项目分享：通过 Telegram 远程控制 AI 编程助手

大家好！今天给大家分享一个我刚开源的项目：**Telegram MCP Server**

## 💡 项目背景

不知道大家有没有遇到过这些场景：

- 深夜躺在床上，突然想到一个 bug 需要修复，但不想起床开电脑
- 通勤路上，想让 AI 助手帮忙重构代码，但笔记本不在身边
- 远程服务器上跑着多个 Claude Code/Codex 会话，想随时查看进度
- 长时间任务（测试、构建）需要几小时，但不想一直守在电脑前

我之前就经常遇到这些问题，所以写了这个工具。

## 🎯 项目简介

**Telegram MCP Server** 是一个基于 MCP（Model Context Protocol）的工具，让你可以通过 Telegram 远程控制 Claude Code 和 Codex 等 AI 编程助手。

**核心功能**：
- 📱 随时随地通过 Telegram 查看和控制 AI 助手
- 🌙 真正的无人值守模式（最长等待 7 天）
- 🔄 智能渐进式轮询（30s → 60s → 120s）
- 🎯 多会话管理（同时管理多个项目）
- 📁 文件操作（查看、下载项目文件）

## 🛠️ 技术栈

- **Python 3.10+**
- **MCP Protocol** - AI 助手通信协议
- **python-telegram-bot** - Telegram Bot API
- **异步 I/O** - 高效的轮询机制

## 📦 快速开始

### 安装

```bash
pip install telegram-mcp-server
```

### 配置

```bash
telegram-mcp-server --setup
```

交互式向导会帮你创建 Telegram Bot 并自动配置。

### 使用

```bash
# 启动 AI 助手（推荐使用免确认模式）
claude --permission-mode bypassPermissions

# 在 AI 助手中
> 进入无人值守模式。任务：分析项目结构
```

然后就可以在 Telegram 查看结果并继续对话了！

## 🌟 实际应用场景

### 场景 1：远程服务器多开

```bash
# SSH 到服务器
ssh user@server

# 用 screen 创建多个会话
screen -S project-a
TELEGRAM_SESSION="proj-a" claude --permission-mode bypassPermissions
# Ctrl+A D 分离

screen -S project-b
TELEGRAM_SESSION="proj-b" codex --dangerously-bypass-approvals-and-sandbox
# Ctrl+A D 分离

# 在 Telegram 同时管理两个项目
# 即使关闭 SSH，会话依然运行
```

### 场景 2：过夜任务

```bash
# 晚上 10 点
> 进入无人值守模式。任务：运行完整测试套件，修复所有错误

# 早上 8 点在 Telegram 查看结果
```

### 场景 3：深夜躺在床上

通过 Telegram 发送指令：
```
/to my-session 修复 auth.py 的空指针异常
```

AI 助手会执行任务，完成后通知你。

## 🔧 核心特性

### 8 个 MCP 工具

- `telegram_notify` - 发送结构化通知
- `telegram_wait_reply` - 等待用户回复
- `telegram_unattended_mode` - 无人值守模式
- `telegram_send_code` - 发送代码（带语法高亮）
- `telegram_send_image` - 发送图片
- `telegram_send_file` - 发送文件
- `telegram_send` - 发送自由格式消息
- `telegram_get_context_info` - 获取会话上下文

### 6 个 Telegram 命令

- `/sessions` - 列出所有会话
- `/status <id>` - 查看会话状态
- `/to <id> <msg>` - 发送消息到会话
- `/file <id> <path>` - 查看文件
- `/delete <id>` - 删除会话
- `/help` - 显示帮助

### 智能轮询机制

渐进式轮询策略，节省资源：

| 等待时长 | 检查频率 | 响应延迟 |
|---------|---------|---------|
| 0-30 分钟 | 每 30 秒 | 最多 30 秒 |
| 30-60 分钟 | 每 60 秒 | 最多 60 秒 |
| 1 小时以上 | 每 120 秒 | 最多 120 秒 |

## 📊 工作原理

```
AI 助手 (Claude Code/Codex)
  ↓ MCP 协议
MCP 服务器 (telegram-mcp-server)
  ├─ 8 个工具（通知、等待、文件等）
  └─ Telegram Bot（后台运行）
      ↓ Telegram API
你的 Telegram 客户端
```

## 🎁 项目链接

- **GitHub**: https://github.com/batianVolyc/telegram-mcp-server
- **PyPI**: https://pypi.org/project/telegram-mcp-server/
- **文档**: [README](https://github.com/batianVolyc/telegram-mcp-server#readme)

## 💭 开发心得

这个项目从想法到实现大概花了一周时间。最大的挑战是：

1. **轮询策略设计**：如何在响应速度和资源消耗之间平衡
2. **会话管理**：多进程环境下的状态同步（使用文件锁解决）
3. **错误处理**：Telegram API 的各种边界情况
4. **用户体验**：让配置过程尽可能简单（一键 setup）

## 🤝 欢迎贡献

项目刚开源，还有很多可以改进的地方：

- [ ] 支持更多 AI 助手（如 Cursor）
- [ ] Web 界面
- [ ] 更丰富的通知格式
- [ ] 会话录制和回放
- [ ] Docker 镜像

如果你有兴趣，欢迎提 Issue 或 PR！

## 📝 许可证

MIT License - 完全开源免费

---

## 🙋 Q&A

**Q: 安全性如何？**  
A: Telegram Bot Token 和 Chat ID 存储在本地配置文件中，不会上传到任何服务器。建议在私有 Bot 中使用。

**Q: 支持哪些 AI 助手？**  
A: 目前支持 Claude Code 和 Codex。理论上支持所有实现了 MCP 协议的 AI 助手。

**Q: 会占用很多资源吗？**  
A: 不会。使用渐进式轮询，长时间等待时每 2 分钟才检查一次。

**Q: 可以在 Windows 上用吗？**  
A: 可以！支持 macOS、Linux 和 Windows。

**Q: 需要一直开着电脑吗？**  
A: 建议在远程服务器上运行，配合 screen 或 tmux 使用。本地电脑关机后会话会断开。

---

如果你也经常需要远程控制 AI 编程助手，不妨试试这个工具！

欢迎 Star ⭐ 和反馈！

---

**让 AI 编程助手为你工作，而不是你守着它工作** 🚀
