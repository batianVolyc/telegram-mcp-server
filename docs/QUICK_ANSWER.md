# 400 错误快速解答

## 问题

```
❌ 发送失败: Client error '400 Bad Request'
```

## 原因

**不是长度问题，是 Markdown 格式问题！**

Telegram API 的 `parse_mode: "Markdown"` 对特殊字符敏感：
- `•` (bullet point)
- `✓` (checkmark)  
- `*` `_` `[` `]` `(` `)` 等

当这些字符组合在一起时，Telegram 的 Markdown 解析器会报错。

## 解决方案

✅ **已修复！** (commit 462dbb3)

添加了自动降级机制：
1. 首次尝试用 Markdown 发送
2. 如果收到 400 错误
3. 自动移除 `parse_mode`，以纯文本重试
4. 保证消息一定能发送成功

## 使用

**不需要做任何改变！**

修复是透明的：
- AI 继续正常生成消息
- 系统自动处理 Markdown 错误
- 消息保证送达（可能失去格式）

## 验证

重启 Bot 让新代码生效：

```bash
cd telegram-mcp-server
./restart_bot.sh
```

然后重启 AI 工具（Claude Code/Gemini）。

## 测试

```bash
python3 test_markdown_fix.py
```

## 详细文档

- `MARKDOWN_FIX.md` - 完整技术文档
- `CORRECT_USAGE.md` - 使用指南
