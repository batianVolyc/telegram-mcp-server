# 更新 uvx 缓存指南

## 问题

当你通过 `uvx` 安装 telegram-mcp-server 时，代码被缓存在：
```
~/.cache/uv/archive-v0/<hash>/lib/python3.12/site-packages/telegram_mcp_server/
```

如果你在开发目录修改了代码，uvx 缓存中的代码不会自动更新。

## 解决方案

### 方法 1：自动更新脚本（推荐）

```bash
cd telegram-mcp-server
./update_uvx_cache.sh
```

这个脚本会：
1. 找到正在运行的进程
2. 定位 uvx 缓存目录
3. 备份旧文件
4. 复制新文件到缓存
5. 提示你重启

### 方法 2：手动更新

1. 找到缓存目录：
```bash
ps aux | grep "telegram_mcp_server"
# 找到 Python 路径，推导出缓存目录
```

2. 复制文件：
```bash
cp telegram-mcp-server/telegram_mcp_server/*.py \
   ~/.cache/uv/archive-v0/<hash>/lib/python3.12/site-packages/telegram_mcp_server/
```

3. 重启服务

### 方法 3：清除缓存重装

```bash
# 清除 uvx 缓存
rm -rf ~/.cache/uv/archive-v0/*

# 重启 Kiro/Claude Code
# uvx 会自动重新下载安装
```

## 完整流程

### 1. 修改代码
在 `telegram-mcp-server/` 开发目录修改代码

### 2. 更新缓存
```bash
cd telegram-mcp-server
./update_uvx_cache.sh
```

### 3. 重启服务
- 重启 Kiro IDE
- 或重启 Claude Code
- MCP 服务器会自动重启并加载新代码

### 4. 验证
在 Telegram 中测试新功能

## 目录结构

```
~/cc2tg/
├── telegram-mcp-server/          # 开发目录（你的代码）
│   ├── telegram_mcp_server/
│   │   ├── server.py            # 修改这里
│   │   ├── bot.py
│   │   └── ...
│   └── update_uvx_cache.sh      # 更新脚本
│
~/.cache/uv/archive-v0/<hash>/    # uvx 缓存（运行的代码）
└── lib/python3.12/site-packages/
    └── telegram_mcp_server/
        ├── server.py            # 更新到这里
        ├── bot.py
        └── ...
```

## 常见问题

### Q: 为什么修改代码后没有生效？
A: 因为运行的是 uvx 缓存中的旧代码，需要更新缓存。

### Q: 每次修改都要更新缓存吗？
A: 是的，除非你使用开发模式安装（`pip install -e .`）。

### Q: 如何知道缓存是否更新成功？
A: 检查文件修改时间：
```bash
ls -la ~/.cache/uv/archive-v0/*/lib/python3.12/site-packages/telegram_mcp_server/server.py
```

### Q: 更新失败怎么办？
A: 使用备份恢复：
```bash
# 脚本会告诉你备份位置
mv <backup_path> ~/.cache/uv/archive-v0/<hash>/lib/python3.12/site-packages/telegram_mcp_server
```

## 最佳实践

### 开发时
1. 在开发目录修改代码
2. 运行 `update_uvx_cache.sh`
3. 重启服务测试

### 发布时
1. 提交代码到 git
2. 更新版本号
3. 发布到 PyPI
4. 用户通过 `uvx` 自动获取新版本

## 相关文件

- `update_uvx_cache.sh` - 自动更新脚本
- `MARKDOWN_FIX.md` - Markdown 错误修复文档
- `QUICK_ANSWER.md` - 400 错误快速解答
