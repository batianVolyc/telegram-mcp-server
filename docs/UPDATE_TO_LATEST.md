# 如何更新到最新版本

## 问题

运行 `uvx telegram-mcp-server@latest --version` 显示旧版本？

## 原因

uvx 会缓存包，即使 PyPI 上有新版本，它也可能使用旧缓存。

## 解决方案

### 方法 1：清除缓存（推荐）

```bash
# 删除 telegram-mcp-server 的所有缓存
find ~/.cache/uv -name "*telegram*" -type d -exec rm -rf {} + 2>/dev/null

# 重新运行（会自动下载最新版本）
uvx telegram-mcp-server@latest --version
```

### 方法 2：指定版本号

```bash
# 直接指定最新版本号
uvx telegram-mcp-server@0.2.4 --version
```

### 方法 3：清除整个 uv 缓存

```bash
# 警告：这会清除所有 uv 缓存的包
rm -rf ~/.cache/uv/*

# 重新运行
uvx telegram-mcp-server@latest --version
```

## 验证

运行后应该看到：

```
telegram-mcp-server version 0.2.4
https://github.com/batianVolyc/telegram-mcp-server
```

## 更新 MCP 服务器

如果你在 Kiro/Claude Code 中使用 MCP 服务器：

1. **清除缓存**（使用上面的方法）
2. **重启 AI 工具**（Kiro IDE 或 Claude Code）
3. **验证版本**：
   ```bash
   uvx telegram-mcp-server@latest --version
   ```

## 常见问题

### Q: 为什么 `@latest` 不总是获取最新版本？

A: uvx 会缓存包索引和包本身。即使 PyPI 有新版本，uvx 可能使用缓存的旧索引。

### Q: 如何强制 uvx 刷新？

A: 目前最可靠的方法是删除缓存目录。uvx 的 `--refresh` 选项对 `uvx` 命令不起作用。

### Q: 删除缓存安全吗？

A: 完全安全！缓存只是为了加速，删除后 uvx 会重新下载需要的包。

### Q: PyPI 显示新版本，但 uvx 还是旧的？

A: 等待 1-2 分钟让 PyPI CDN 同步，然后清除缓存重试。

## 版本历史

- **0.2.4** (2024-10-22) - 修复版本号显示
- **0.2.3** (2024-10-22) - Markdown 解析修复（版本号错误）
- **0.2.2** (2024-10-22) - 工具描述改进
- **0.2.1** (2024-10-22) - 添加 --version 标志
- **0.2.0** (2024-10-22) - 动态按钮系统

## 相关链接

- PyPI: https://pypi.org/project/telegram-mcp-server/
- GitHub: https://github.com/batianVolyc/telegram-mcp-server
- Issues: https://github.com/batianVolyc/telegram-mcp-server/issues
