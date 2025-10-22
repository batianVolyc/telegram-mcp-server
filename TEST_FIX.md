# 修复验证指南

## ✅ 已修复的问题

### 1. Claude Code 配置路径错误
- ❌ 旧路径：`~/.claude/mcp.json`
- ✅ 新路径：`~/.claude.json`

### 2. 添加 MCP_TOOL_TIMEOUT 支持
- ✅ 自动配置 `~/.claude/settings.json`
- ✅ 设置 `MCP_TOOL_TIMEOUT=604800000`（7天，毫秒）
- ✅ 智能合并现有的 `env` 配置

### 3. 更新所有文档
- ✅ README.md（英文）
- ✅ README-CN.md（中文）
- ✅ docs/CONFIGURATION_GUIDE.md

## 🧪 测试步骤

### 测试 1: 验证配置路径

```bash
# 运行 setup
telegram-mcp-server --setup

# 选择 Claude Code
# 选择 User scope

# 检查生成的文件
ls -la ~/.claude.json          # 应该存在
cat ~/.claude.json             # 查看 MCP 配置

ls -la ~/.claude/settings.json # 应该存在
cat ~/.claude/settings.json    # 查看环境变量配置
```

**预期结果**：

`~/.claude.json`:
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

`~/.claude/settings.json`:
```json
{
  "env": {
    "MCP_TOOL_TIMEOUT": "604800000"
  }
}
```

### 测试 2: 验证智能合并

```bash
# 1. 创建已有的 settings.json
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "EXISTING_VAR": "existing_value",
    "ANOTHER_VAR": "another_value"
  },
  "permissions": {
    "allow": ["Bash(git)"]
  }
}
EOF

# 2. 运行 setup
telegram-mcp-server --setup

# 3. 检查合并结果
cat ~/.claude/settings.json
```

**预期结果**：
```json
{
  "env": {
    "EXISTING_VAR": "existing_value",
    "ANOTHER_VAR": "another_value",
    "MCP_TOOL_TIMEOUT": "604800000"
  },
  "permissions": {
    "allow": ["Bash(git)"]
  }
}
```

✅ 原有的 `env` 变量保留
✅ 新的 `MCP_TOOL_TIMEOUT` 添加
✅ 其他配置（如 `permissions`）不受影响

### 测试 3: 验证 Claude Code 识别

```bash
# 启动 Claude Code
claude

# 在 Claude Code 中运行
/mcp

# 应该看到 telegram MCP 服务器已连接
```

**预期输出**：
```
MCP Config locations (by scope):
• User config (available in all your projects):
  • /Users/username/.claude.json
  
Connected MCP servers:
• telegram
  - 8 tools available
```

### 测试 4: 验证 7 天超时

```bash
# 启动 Claude Code
claude --permission-mode bypassPermissions

# 测试无人值守模式
> 进入无人值守模式。任务：等待我的指令

# 在 Telegram 查看消息
# 等待几分钟，不发送回复
# Claude Code 应该持续轮询，不会超时
```

## 🐛 如果遇到问题

### 问题 1: Claude Code 找不到配置

**症状**：
```
MCP Config locations (by scope):
• User config: /Users/username/.claude.json (file does not exist)
```

**解决**：
```bash
# 检查文件是否存在
ls -la ~/.claude.json

# 如果不存在，重新运行 setup
telegram-mcp-server --setup
```

### 问题 2: MCP 工具仍然超时

**症状**：
- 等待超过 60 秒后超时
- 错误信息：`Tool execution timeout`

**解决**：
```bash
# 检查 settings.json
cat ~/.claude/settings.json

# 确认包含 MCP_TOOL_TIMEOUT
# 如果没有，手动添加：
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "MCP_TOOL_TIMEOUT": "604800000"
  }
}
EOF

# 重启 Claude Code
```

### 问题 3: 环境变量未生效

**症状**：
- settings.json 中有 MCP_TOOL_TIMEOUT
- 但仍然超时

**解决**：
```bash
# 方式 1: 使用环境变量启动
export MCP_TOOL_TIMEOUT=604800000
claude --permission-mode bypassPermissions

# 方式 2: 检查 Claude Code 版本
claude --version
# 确保使用最新版本
```

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| MCP 配置路径 | `~/.claude/mcp.json` ❌ | `~/.claude.json` ✅ |
| 环境变量配置 | 不支持 ❌ | `~/.claude/settings.json` ✅ |
| MCP_TOOL_TIMEOUT | 未配置 ❌ | 自动配置 7 天 ✅ |
| 智能合并 | N/A | 保留现有配置 ✅ |
| 用户反馈问题 | Claude 无法加载 MCP ❌ | 正常工作 ✅ |

## 🎉 验证成功标志

- ✅ `~/.claude.json` 文件存在且包含 telegram MCP 配置
- ✅ `~/.claude/settings.json` 包含 `MCP_TOOL_TIMEOUT=604800000`
- ✅ Claude Code 能识别并连接 telegram MCP 服务器
- ✅ 无人值守模式可以等待超过 60 秒
- ✅ 现有的 settings.json 配置不会被覆盖

---

**如果所有测试通过，修复成功！** 🎊
