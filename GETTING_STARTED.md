# 🚀 新用户快速开始指南

## 📋 前提条件

1. **Python 3.10+** 已安装
2. **uv/uvx** 已安装（通常 Claude Code 会自动安装）
3. **Telegram Bot Token** 和 **Chat ID**

---

## 🎯 方法 1: 使用 uvx（推荐，最简单）

### 步骤 1: 确保使用最新版本

```bash
# 强制使用最新版本（跳过缓存）
uvx --refresh telegram-mcp-server@latest --version
```

**预期输出**：
```
telegram-mcp-server version 0.2.1
https://github.com/batianVolyc/telegram-mcp-server
```

### 步骤 2: 运行交互式设置

```bash
uvx telegram-mcp-server@latest --setup
```

这会引导你：
1. 输入 Telegram Bot Token
2. 自动检测 Chat ID
3. 配置 Claude Code / Codex / Gemini CLI

### 步骤 3: 在 AI 工具中使用

配置会自动添加到 `~/.claude.json` 或相应的配置文件。

重启 Claude Code，然后在项目中：
```
使用 telegram_notify 发送消息到 Telegram
```

---

## 🎯 方法 2: 使用 pipx（适合命令行工具）

### 安装 pipx（如果还没有）

```bash
brew install pipx
```

### 安装 telegram-mcp-server

```bash
pipx install telegram-mcp-server
```

### 运行设置

```bash
telegram-mcp-server --setup
```

### 验证版本

```bash
telegram-mcp-server --version
```

---

## 🎯 方法 3: 使用虚拟环境（传统方式）

### 创建虚拟环境

```bash
python3 -m venv ~/venvs/telegram-mcp
source ~/venvs/telegram-mcp/bin/activate
```

### 安装

```bash
pip install telegram-mcp-server
```

### 运行设置

```bash
telegram-mcp-server --setup
```

### 退出虚拟环境

```bash
deactivate
```

---

## ⚠️ 常见问题

### 问题 1: `uvx` 使用了旧版本

**症状**：
```bash
uvx telegram-mcp-server --version
# 输出: Unknown option: --version
```

**原因**：uvx 缓存了旧版本（0.2.0 或更早）

**解决方案**：
```bash
# 方法 A: 强制刷新（推荐）
uvx --refresh telegram-mcp-server@latest --version

# 方法 B: 指定版本
uvx telegram-mcp-server@0.2.1 --version

# 方法 C: 清除所有 uvx 缓存
rm -rf ~/.local/share/uv/
uvx telegram-mcp-server --version
```

### 问题 2: `command not found: telegram-mcp-server`

**原因**：没有安装或不在 PATH 中

**解决方案**：
```bash
# 使用 uvx（无需安装）
uvx telegram-mcp-server --version

# 或安装 pipx
brew install pipx
pipx install telegram-mcp-server
```

### 问题 3: `externally-managed-environment` 错误

**原因**：macOS Python 3.14 的安全限制

**解决方案**：
```bash
# 使用 uvx（推荐）
uvx telegram-mcp-server --setup

# 或使用 pipx
pipx install telegram-mcp-server

# 不要使用 pip3 直接安装到系统
```

---

## 🧪 验证安装

### 1. 检查版本

```bash
# 使用 uvx
uvx --refresh telegram-mcp-server@latest --version

# 使用 pipx
telegram-mcp-server --version

# 使用 Python
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

**预期输出**：`0.2.1` 或更高

### 2. 查看帮助

```bash
uvx telegram-mcp-server --help
```

应该看到：
```
Usage:
  telegram-mcp-server              Run MCP server
  telegram-mcp-server --version    Show version
  telegram-mcp-server --setup      Interactive setup wizard
  telegram-mcp-server --config     Show current configuration
  telegram-mcp-server --help       Show this help
```

### 3. 在 Telegram 中测试

启动服务器后，在 Telegram 中发送：
```
/help
```

应该看到：
```
💬 消息发送
/to <session_id> [消息] - 向指定会话发送消息（或锁定会话）
/keep <session_id> - 锁定会话（后续消息自动发送）
/keep off - 取消会话锁定
```

---

## 📖 完整使用流程

### 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示创建 bot
4. 复制 Bot Token（格式：`123456789:ABCdef...`）

### 2. 获取 Chat ID

1. 在 Telegram 中搜索你的 bot
2. 点击 START 或发送任意消息
3. 访问：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 找到 `"chat":{"id":123456789}`

### 3. 运行设置向导

```bash
uvx telegram-mcp-server@latest --setup
```

按提示输入：
- Bot Token
- Chat ID（或自动检测）
- 选择要配置的 AI 工具

### 4. 重启 AI 工具

```bash
# Claude Code
claude --permission-mode bypassPermissions

# Codex
codex --dangerously-bypass-approvals-and-sandbox

# Gemini CLI
gemini
```

### 5. 测试连接

在 AI 工具中：
```
使用 telegram_notify 发送一条测试消息
```

在 Telegram 中应该收到消息。

### 6. 使用新功能

#### 动态按钮
在 AI 中：
```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 测试完成",
    actions=[
        {"text": "继续", "action": "继续下一步", "emoji": "💡"},
        {"text": "查看", "action": "查看详情", "emoji": "📊"}
    ]
)
```

#### 会话锁定
在 Telegram 中：
```
/keep my-project
现在发送的消息会自动发送到 my-project
/keep off
```

---

## 🔗 相关链接

- **PyPI**: https://pypi.org/project/telegram-mcp-server/
- **GitHub**: https://github.com/batianVolyc/telegram-mcp-server
- **文档**: https://github.com/batianVolyc/telegram-mcp-server#readme
- **问题反馈**: https://github.com/batianVolyc/telegram-mcp-server/issues

---

## 💡 推荐配置

### Claude Code 配置示例

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server@latest"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-bot-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    }
  }
}
```

**注意**：使用 `telegram-mcp-server@latest` 确保始终使用最新版本。

---

## 🎉 开始使用

```bash
# 一键开始
uvx --refresh telegram-mcp-server@latest --setup
```

就这么简单！🚀
