# 如何确认安装的版本

## 🔍 方法 1: 使用 `--version` 参数（推荐）

### 使用 uvx
```bash
uvx telegram-mcp-server --version
```

输出应该是：
```
telegram-mcp-server version 0.2.0
https://github.com/batianVolyc/telegram-mcp-server
```

### 使用 pipx
```bash
telegram-mcp-server --version
```

### 使用 pip（在虚拟环境中）
```bash
source ~/venvs/telegram-mcp/bin/activate
telegram-mcp-server --version
```

---

## 🔍 方法 2: 使用 Python 检查

```bash
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

输出应该是：
```
0.2.0
```

---

## 🔍 方法 3: 使用 pip show

### 如果用 pip 安装
```bash
pip3 show telegram-mcp-server
```

### 如果用 pipx 安装
```bash
pipx list | grep telegram-mcp-server
```

输出示例：
```
Name: telegram-mcp-server
Version: 0.2.0
Summary: Remote control Claude Code via Telegram - MCP Server with Dynamic Buttons
Home-page: https://github.com/batianVolyc/telegram-mcp-server
Author: Ray Volcy
License: MIT
```

---

## 🔍 方法 4: 检查 PyPI 最新版本

```bash
# 检查 PyPI 上的最新版本
pip3 index versions telegram-mcp-server
```

或者访问：
https://pypi.org/project/telegram-mcp-server/

---

## 🔄 如何升级到 0.2.0

### 使用 uvx（推荐）
```bash
# uvx 每次都会使用最新版本，无需手动升级
uvx telegram-mcp-server --version
```

### 使用 pipx
```bash
# 升级
pipx upgrade telegram-mcp-server

# 验证版本
telegram-mcp-server --version
```

### 使用 pip（在虚拟环境中）
```bash
# 激活虚拟环境
source ~/venvs/telegram-mcp/bin/activate

# 升级
pip install --upgrade telegram-mcp-server

# 验证版本
telegram-mcp-server --version

# 或者
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

### 使用 pip（系统级，不推荐）
```bash
pip3 install --break-system-packages --upgrade telegram-mcp-server
```

---

## 🧪 完整验证流程

### 1. 卸载旧版本（如果需要）

```bash
# 使用 pipx
pipx uninstall telegram-mcp-server

# 使用 pip（在虚拟环境中）
pip uninstall telegram-mcp-server

# 使用 pip（系统级）
pip3 uninstall telegram-mcp-server
```

### 2. 安装新版本

```bash
# 推荐：使用 uvx（无需安装）
uvx telegram-mcp-server --version

# 或使用 pipx
pipx install telegram-mcp-server
telegram-mcp-server --version
```

### 3. 验证版本

```bash
# 方法 1: 命令行参数
telegram-mcp-server --version

# 方法 2: Python 导入
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"

# 方法 3: pip show
pip3 show telegram-mcp-server | grep Version
```

### 4. 测试新功能

```bash
# 运行 setup
telegram-mcp-server --setup

# 或直接运行
telegram-mcp-server
```

在 Telegram 中测试：
```
/help
```

应该看到新的 `/keep` 命令说明。

---

## ✅ 确认 0.2.0 的特征

如果你安装的是 0.2.0，应该有以下特征：

### 1. 命令行帮助包含新命令
```bash
telegram-mcp-server --help
```

应该显示：
```
  telegram-mcp-server --version    Show version
```

### 2. Telegram Bot 帮助包含新功能
在 Telegram 中发送 `/help`，应该看到：
```
💬 消息发送
/to <session_id> [消息] - 向指定会话发送消息（或锁定会话）
/keep <session_id> - 锁定会话（后续消息自动发送）
/keep off - 取消会话锁定
```

### 3. Python 模块版本
```bash
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

输出：`0.2.0`

### 4. 新的 MCP 工具
在 AI 助手中，应该可以使用：
```python
telegram_notify_with_actions(
    event="completed",
    summary="测试",
    actions=[{"text": "测试按钮", "action": "测试指令"}]
)
```

---

## 🐛 故障排查

### 问题 1: 版本显示仍然是 0.1.0

**原因**：可能有多个安装位置

**解决**：
```bash
# 查找所有安装位置
which -a telegram-mcp-server

# 或
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__file__)"

# 卸载所有旧版本
pip3 uninstall telegram-mcp-server
pipx uninstall telegram-mcp-server

# 重新安装
uvx telegram-mcp-server --version
```

### 问题 2: uvx 显示旧版本

**原因**：uvx 缓存

**解决**：
```bash
# 清除 uvx 缓存
rm -rf ~/.local/share/uv/

# 重新运行
uvx telegram-mcp-server --version
```

### 问题 3: 找不到命令

**原因**：PATH 问题

**解决**：
```bash
# 使用完整路径
python3 -m telegram_mcp_server.cli --version

# 或使用 uvx
uvx telegram-mcp-server --version
```

---

## 📞 需要帮助？

如果版本检查有问题，请提供以下信息：

```bash
# 1. Python 版本
python3 --version

# 2. 安装方法
which telegram-mcp-server

# 3. 包信息
pip3 show telegram-mcp-server

# 4. 模块位置
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__file__)"

# 5. 版本号
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

在 GitHub 提交 Issue：
https://github.com/batianVolyc/telegram-mcp-server/issues

---

**快速验证命令**：
```bash
uvx telegram-mcp-server --version && echo "✅ 版本正确" || echo "❌ 需要升级"
```
