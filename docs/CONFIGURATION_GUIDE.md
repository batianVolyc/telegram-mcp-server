# 配置指南

## 支持的 AI 编程助手

Telegram MCP Server 支持以下 AI 编程助手：

1. **Claude Code** (Anthropic)
2. **Codex** (OpenAI)
3. **两者同时配置**

## 快速配置

### 交互式配置（推荐）

```bash
telegram-mcp-server --setup
```

向导会引导你：
1. 选择 AI 助手（Claude Code / Codex / 两者）
2. 选择配置范围（仅 Claude Code）
3. 输入 Telegram 凭据
4. 自动生成配置文件

---

## Claude Code 配置

### 配置范围

Claude Code 支持三种配置范围：

#### 1. User Scope（用户级，推荐）

**MCP 配置位置**: `~/.claude.json`

**环境变量配置**: `~/.claude/settings.json`

**特点**:
- 全局可用，所有项目共享
- 个人配置，不会提交到 git
- 适合个人使用

**MCP 配置示例** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_token",
        "TELEGRAM_CHAT_ID": "your_chat_id"
      }
    }
  }
}
```

**环境变量配置** (`~/.claude/settings.json`):
```json
{
  "env": {
    "MCP_TOOL_TIMEOUT": "604800000"
  }
}
```

**说明**:
- `MCP_TOOL_TIMEOUT`: MCP 工具执行超时（毫秒），设置为 7 天（604800000 ms）
- Setup 向导会自动配置此项

**使用**:
```bash
# 任何目录下启动 Claude Code
cd ~/any-project
claude
```

#### 2. Project Scope（项目共享）

**MCP 配置位置**: `.mcp.json` (项目根目录)

**环境变量配置**: `~/.claude/settings.json` (用户级，不共享)

**特点**:
- 团队共享，提交到 git
- 所有团队成员使用相同配置
- 适合团队协作

**MCP 配置示例** (`.mcp.json`):
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID}"
      }
    }
  }
}
```

**说明**:
- 凭据使用环境变量，不提交到 git
- `MCP_TOOL_TIMEOUT` 在用户的 `~/.claude/settings.json` 中配置

**使用**:
```bash
# 团队成员设置环境变量
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 启动 Claude Code
cd ~/team-project
claude
```

**注意**: 首次使用时，Claude Code 会提示批准项目级 MCP 服务器。

#### 3. Local Scope（项目本地）

**位置**: `.claude/mcp.json` (项目目录)

**特点**:
- 项目特定，不共享
- 不提交到 git（添加到 .gitignore）
- 适合项目特定配置

**配置示例**:
```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "project_specific_token",
        "TELEGRAM_CHAT_ID": "project_specific_chat_id"
      }
    }
  }
}
```

### 配置优先级

当多个范围都有配置时，优先级为：

```
Local > Project > User
```

### 环境变量展开

Claude Code 支持在配置中使用环境变量：

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID:-default_chat_id}"
      }
    }
  }
}
```

语法：
- `${VAR}` - 使用环境变量 VAR
- `${VAR:-default}` - 如果 VAR 未设置，使用 default

---

## Codex 配置

### 配置位置

**位置**: `~/.codex/config.toml`

**特点**:
- **仅支持全局配置**（不支持项目级配置）
- CLI 和 IDE 扩展共享
- TOML 格式
- 所有项目使用相同的 MCP 配置

**注意**: 与 Claude Code 不同，Codex 不支持项目级或本地级配置。所有 MCP 服务器配置都是全局的。

### 配置示例

```toml
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]
tool_timeout_sec = 3600  # 1 hour timeout for long-running tools

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

**重要配置项**:
- `tool_timeout_sec` - 工具执行超时（秒）
  - 默认: ~60 秒
  - 推荐: 3600（1 小时）用于无人值守模式
  - 最大: 根据需要设置

### 使用 CLI 配置

```bash
# 添加 MCP 服务器
codex mcp add telegram \
  --env TELEGRAM_BOT_TOKEN=your_token \
  --env TELEGRAM_CHAT_ID=your_chat_id \
  -- uvx telegram-mcp-server

# 查看配置
codex mcp list

# 删除配置
codex mcp remove telegram
```

### 使用 IDE 扩展配置

1. 点击 Codex 扩展右上角的齿轮图标
2. 选择 "MCP settings > Open config.toml"
3. 手动编辑配置文件
4. 保存并重启 Codex

---

## 手动配置

### Claude Code

#### User Scope
```bash
# 创建配置目录
mkdir -p ~/.claude

# 创建配置文件
cat > ~/.claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_token",
        "TELEGRAM_CHAT_ID": "your_chat_id"
      }
    }
  }
}
EOF
```

#### Project Scope
```bash
# 在项目根目录
cd ~/my-project

# 创建配置文件
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID}"
      }
    }
  }
}
EOF

# 添加到 git
git add .mcp.json
git commit -m "Add Telegram MCP server configuration"
```

#### Local Scope
```bash
# 在项目目录
cd ~/my-project

# 创建配置目录
mkdir -p .claude

# 创建配置文件
cat > .claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_token",
        "TELEGRAM_CHAT_ID": "your_chat_id"
      }
    }
  }
}
EOF

# 添加到 .gitignore
echo ".claude/" >> .gitignore
```

### Codex

```bash
# 创建配置目录
mkdir -p ~/.codex

# 创建配置文件
cat > ~/.codex/config.toml << 'EOF'
[mcp_servers.telegram]
command = "uvx"
args = ["telegram-mcp-server"]

[mcp_servers.telegram.env]
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
EOF
```

---

## 验证配置

### Claude Code

```bash
# 启动 Claude Code
claude

# 在 Claude 中检查 MCP
> /mcp

# 应该看到 telegram 服务器已连接
```

### Codex

```bash
# 启动 Codex
codex

# 在 Codex 中检查 MCP
> /mcp

# 应该看到 telegram 服务器已连接
```

---

## 故障排查

### Claude Code: "No MCP servers configured"

**可能原因**:
1. 配置文件位置错误
2. 配置文件格式错误
3. 环境变量未设置（Project scope）

**解决方法**:
```bash
# 检查配置文件是否存在
ls -la ~/.claude/mcp.json
ls -la .mcp.json
ls -la .claude/mcp.json

# 验证 JSON 格式
cat ~/.claude/mcp.json | python -m json.tool

# 检查环境变量（Project scope）
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

### Codex: MCP 服务器未连接

**可能原因**:
1. config.toml 格式错误
2. 命令路径错误

**解决方法**:
```bash
# 检查配置文件
cat ~/.codex/config.toml

# 验证 TOML 格式
python -c "import toml; toml.load(open('~/.codex/config.toml'))"

# 测试命令
uvx telegram-mcp-server --help
```

### 环境变量未展开

**Claude Code (Project scope)**:
```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 验证
echo $TELEGRAM_BOT_TOKEN

# 重启 Claude Code
claude
```

---

## 推荐配置方案

### 个人使用

**Claude Code**: User scope  
**Codex**: 默认配置

```bash
telegram-mcp-server --setup
# 选择: 1 (Claude Code) 或 2 (Codex) 或 3 (Both)
# 选择: 1 (User scope)
```

### 团队协作

**Claude Code**: Project scope  
**Codex**: 每个成员独立配置

```bash
# 项目维护者
telegram-mcp-server --setup
# 选择: 1 (Claude Code)
# 选择: 2 (Project scope)

# 提交配置
git add .mcp.json
git commit -m "Add Telegram MCP configuration"
git push

# 团队成员
git pull
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
claude
```

### 多项目使用

**Claude Code**: User scope（全局）+ Local scope（项目特定）  
**Codex**: 默认配置

```bash
# 全局配置（大多数项目）
telegram-mcp-server --setup
# 选择: 1 (User scope)

# 特定项目配置（不同 bot）
cd ~/special-project
telegram-mcp-server --setup
# 选择: 3 (Local scope)
```

---

## 更多资源

- [Claude Code MCP 文档](https://docs.claude.com/en/docs/claude-code/mcp)
- [Codex MCP 文档](https://developers.openai.com/codex/mcp/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [项目 README](README.md)
