# 多工具支持 - 测试指南

## ✅ 已完成的更新

### 1. 添加 Gemini CLI 支持

**新功能**：
- ✅ 自动检测已安装的 CLI 工具
- ✅ 支持配置 Gemini CLI（用户级和项目级）
- ✅ 自动设置 7 天超时（`timeout: 604800000`）
- ✅ 智能跳过未安装的工具

### 2. 更新 README 命令

**修正了 Gemini CLI 的 `mcp add` 命令**：

❌ **旧命令**（错误）：
```bash
gemini mcp add \
  -t stdio \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx \
  telegram \
  uvx \
  telegram-mcp-server
```

✅ **新命令**（正确）：
```bash
gemini mcp add telegram uvx telegram-mcp-server \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx
```

**关键差异**：
- 参数顺序：`name` → `command` → `args` → 选项
- 不需要 `--` 分隔符
- 使用 `-e` 而不是 `--env`

### 3. Setup 完成后显示 mcp add 命令

现在 `telegram-mcp-server --setup` 完成后会显示：
- 已配置工具的启动命令
- 未配置工具的 `mcp add` 命令模板（包含实际的 token）

---

## 🧪 测试步骤

### 测试 1：只有 Claude Code

```bash
# 运行 setup
telegram-mcp-server --setup

# 选择：1 (Claude Code)
# 选择 scope: 1 (User)

# 预期结果：
# ✅ 配置 ~/.claude.json
# ✅ 配置 ~/.claude/settings.json (MCP_TOOL_TIMEOUT)
# ✅ 显示 Codex 和 Gemini CLI 的 mcp add 命令
```

### 测试 2：只有 Codex

```bash
# 运行 setup
telegram-mcp-server --setup

# 选择：2 (Codex)

# 预期结果：
# ✅ 配置 ~/.codex/config.toml (tool_timeout_sec: 604800)
# ✅ 显示 Claude Code 和 Gemini CLI 的 mcp add 命令
```

### 测试 3：只有 Gemini CLI

```bash
# 运行 setup
telegram-mcp-server --setup

# 选择：3 (Gemini CLI)
# 选择 scope: 1 (User)

# 预期结果：
# ✅ 配置 ~/.gemini/settings.json (timeout: 604800000)
# ✅ 显示 Claude Code 和 Codex 的 mcp add 命令
```

### 测试 4：多个工具

```bash
# 运行 setup
telegram-mcp-server --setup

# 选择：4 (Multiple tools)
# 为每个工具选择 scope

# 预期结果：
# ✅ 配置所有选择的工具
# ✅ 只显示未配置工具的 mcp add 命令
```

### 测试 5：Gemini CLI 未安装

```bash
# 确保 gemini 未安装
which gemini  # 应该返回空

# 运行 setup
telegram-mcp-server --setup

# 选择：3 (Gemini CLI)

# 预期结果：
# ⚠️  提示 "Gemini CLI not detected"
# ❓ 询问 "Create configuration anyway? (y/N)"
# 如果选 N：跳过配置
# 如果选 y：创建配置文件
```

---

## 📋 各工具的配置文件和超时设置

### Claude Code

**MCP 配置**：`~/.claude.json`
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "...",
        "TELEGRAM_CHAT_ID": "..."
      }
    }
  }
}
```

**环境变量配置**：`~/.claude/settings.json`
```json
{
  "env": {
    "MCP_TOOL_TIMEOUT": "604800000"
  }
}
```

**超时**：7 天（604800000 毫秒）

---

### Codex

**配置**：`~/.codex/config.toml`
```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
tool_timeout_sec = 604800

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "..."
TELEGRAM_CHAT_ID = "..."
```

**超时**：7 天（604800 秒）

---

### Gemini CLI

**配置**：`~/.gemini/settings.json`
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "...",
        "TELEGRAM_CHAT_ID": "..."
      },
      "timeout": 604800000
    }
  }
}
```

**超时**：7 天（604800000 毫秒）

---

## 🎯 mcp add 命令对比

### Claude Code
```bash
claude mcp add \
  --transport stdio \
  telegram \
  --env TELEGRAM_BOT_TOKEN=xxx \
  --env TELEGRAM_CHAT_ID=xxx \
  -- \
  uvx telegram-mcp-server
```

**特点**：
- 需要 `--` 分隔符
- 使用 `--env`
- 使用 `--transport`

### Codex
```bash
codex mcp add telegram \
  --env TELEGRAM_BOT_TOKEN=xxx \
  --env TELEGRAM_CHAT_ID=xxx \
  -- \
  npx -y telegram-mcp-server
```

**特点**：
- 需要 `--` 分隔符
- 使用 `--env`
- 默认 stdio，不需要指定 transport

### Gemini CLI
```bash
gemini mcp add telegram uvx telegram-mcp-server \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx
```

**特点**：
- ❌ 不需要 `--` 分隔符
- 使用 `-e` 而不是 `--env`
- 参数顺序：name → command → args → options

---

## 🔍 验证配置

### Claude Code
```bash
cat ~/.claude.json
cat ~/.claude/settings.json
claude
# 在 Claude 中：/mcp
```

### Codex
```bash
cat ~/.codex/config.toml
codex
# 在 Codex 中：/mcp
```

### Gemini CLI
```bash
cat ~/.gemini/settings.json
gemini
# 在 Gemini 中：/mcp list
```

---

## 🐛 已知问题

### 问题 1：Gemini CLI 的 args 为空

**症状**：
```json
{
  "args": []  // ❌ 应该是 ["telegram-mcp-server"]
}
```

**原因**：`-e` 选项位置不对

**解决**：将 `-e` 放在最后
```bash
gemini mcp add telegram uvx telegram-mcp-server \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e TELEGRAM_CHAT_ID=xxx
```

### 问题 2：未安装工具时创建配置

**行为**：Setup 会检测工具是否安装，如果未安装会询问是否创建配置

**建议**：
- 如果计划安装该工具：选择 y
- 如果不使用该工具：选择 N

---

## 📊 测试清单

- [ ] 测试 Claude Code 配置（用户级）
- [ ] 测试 Claude Code 配置（项目级）
- [ ] 测试 Codex 配置
- [ ] 测试 Gemini CLI 配置（用户级）
- [ ] 测试 Gemini CLI 配置（项目级）
- [ ] 测试多工具配置
- [ ] 测试未安装工具的提示
- [ ] 验证 mcp add 命令显示
- [ ] 验证超时配置
- [ ] 测试实际连接和工具使用

---

**准备测试！** 🚀
