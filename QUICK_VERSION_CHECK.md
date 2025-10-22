# 🔍 快速版本检查

## ✅ 最简单的方法

```bash
# 使用 uvx（推荐，无需安装）
uvx telegram-mcp-server --version
```

**预期输出**：
```
telegram-mcp-server version 0.2.1
https://github.com/batianVolyc/telegram-mcp-server
```

---

## 📋 完整验证步骤

### 1. 检查命令行版本

```bash
# 方法 A: 使用 uvx（推荐）
uvx telegram-mcp-server --version

# 方法 B: 如果已安装
telegram-mcp-server --version

# 方法 C: 使用 Python
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

### 2. 检查 PyPI 最新版本

```bash
# 查看 PyPI 上的最新版本
curl -s https://pypi.org/pypi/telegram-mcp-server/json | python3 -c "import sys, json; print('Latest:', json.load(sys.stdin)['info']['version'])"
```

### 3. 在 Telegram 中验证

启动服务器后，在 Telegram 中发送：
```
/help
```

如果看到以下内容，说明是 0.2.x 版本：
```
💬 消息发送
/to <session_id> [消息] - 向指定会话发送消息（或锁定会话）
/keep <session_id> - 锁定会话（后续消息自动发送）
/keep off - 取消会话锁定
```

---

## 🔄 如何升级

### 使用 uvx（推荐）
```bash
# uvx 每次都自动使用最新版本，无需手动升级
uvx telegram-mcp-server --version
```

### 使用 pipx
```bash
pipx upgrade telegram-mcp-server
telegram-mcp-server --version
```

### 使用 pip（在虚拟环境中）
```bash
source ~/venvs/telegram-mcp/bin/activate
pip install --upgrade telegram-mcp-server
telegram-mcp-server --version
```

---

## ✅ 确认是 0.2.x 的特征

1. **命令行有 --version 参数**
   ```bash
   telegram-mcp-server --help
   ```
   应该显示：`--version    Show version`

2. **Telegram 有 /keep 命令**
   在 Telegram 中发送 `/help`，应该看到 `/keep` 命令

3. **AI 可以使用动态按钮**
   在 AI 助手中可以调用：
   ```python
   telegram_notify_with_actions(...)
   ```

---

## 🐛 如果版本不对

### 清除缓存并重新安装

```bash
# 1. 清除 uvx 缓存
rm -rf ~/.local/share/uv/

# 2. 重新运行
uvx telegram-mcp-server --version

# 应该显示 0.2.1
```

### 卸载旧版本

```bash
# 如果用 pip 安装过
pip3 uninstall telegram-mcp-server

# 如果用 pipx 安装过
pipx uninstall telegram-mcp-server

# 然后使用 uvx
uvx telegram-mcp-server --version
```

---

## 📞 需要帮助？

如果版本检查有问题，运行以下命令并提供输出：

```bash
echo "=== Python 版本 ==="
python3 --version

echo -e "\n=== 命令位置 ==="
which telegram-mcp-server

echo -e "\n=== 包信息 ==="
pip3 show telegram-mcp-server 2>/dev/null || echo "Not installed via pip"

echo -e "\n=== 模块版本 ==="
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)" 2>/dev/null || echo "Module not found"

echo -e "\n=== uvx 测试 ==="
uvx telegram-mcp-server --version
```

在 GitHub 提交 Issue：https://github.com/batianVolyc/telegram-mcp-server/issues

---

**快速验证命令**：
```bash
uvx telegram-mcp-server --version && echo "✅ 版本正确 (0.2.1)" || echo "❌ 需要检查"
```
