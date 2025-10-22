# Telegram Markdown 解析错误修复

## 问题描述

在使用 `telegram_notify_with_actions` 发送消息时，遇到 **400 Bad Request** 错误：

```
❌ 发送失败: Client error '400 Bad Request' for url 
'https://api.telegram.org/bot.../sendMessage'
```

## 根本原因

Telegram API 的 `parse_mode: "Markdown"` 对特殊字符非常敏感。以下字符组合可能导致解析失败：

### 问题字符
- `•` (bullet point)
- `✓` (checkmark)
- `*` (asterisk)
- `_` (underscore)
- `[` `]` (brackets)
- `(` `)` (parentheses)
- 其他 Markdown 特殊字符

### 触发场景
当 AI（如 Claude Code）生成包含这些字符的复杂消息时：

```
✅ Mandelbrot.py 代码分析完成

📊 功能分析:

核心功能:
• mandelbrot() 函数:判断复数点是否在 Mandelbrot集合中
• render_mandelbrot()函数: 将分形图案渲染到控制台

技术特点:
• 使用复数运算: z =z*z + c
• 最大迭代次数: 100

代码质量:
✓ 简洁高效(~50 行)
✓ 配置灵活
```

Telegram 的 Markdown 解析器会因为字符组合问题返回 400 错误。

## 解决方案

### 自动降级机制

修改了两个函数，添加自动降级逻辑：

#### 1. `send_telegram_message` (server.py:77-106)

```python
try:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400 and parse_mode:
        # Markdown parsing failed, retry without parse_mode
        logger.warning(f"Markdown parsing failed (400 Bad Request), retrying as plain text")
        payload.pop("parse_mode", None)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
    else:
        raise
```

#### 2. `handle_telegram_notify_with_actions` (server.py:838-862)

```python
async with httpx.AsyncClient() as client:
    try:
        # Try with Markdown first
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            # Markdown parsing failed, retry without parse_mode
            logger.warning(f"Markdown parsing failed, retrying as plain text")
            payload.pop("parse_mode", None)
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
        else:
            raise
```

### 工作流程

1. **首次尝试**：使用 `parse_mode: "Markdown"` 发送
2. **检测失败**：如果收到 400 错误
3. **自动降级**：移除 `parse_mode`，以纯文本重试
4. **保证送达**：消息一定能发送成功（虽然可能失去格式）

## 优势

✅ **透明处理**：AI 不需要知道这个问题  
✅ **自动恢复**：400 错误自动降级到纯文本  
✅ **保证送达**：消息不会因为格式问题丢失  
✅ **保留格式**：大多数情况下仍使用 Markdown  
✅ **向后兼容**：不影响现有功能  

## 测试

运行测试脚本验证修复：

```bash
cd telegram-mcp-server
python3 test_markdown_fix.py
```

测试内容：
1. 发送包含问题字符的消息
2. 验证自动降级机制
3. 测试带按钮的消息

## 最佳实践

虽然有自动降级机制，但仍建议：

### AI 生成消息时
- 避免过度使用特殊字符
- 使用简单的格式
- 保持消息简洁（200字以内）

### 好的消息格式
```
✅ 任务完成

修复了 auth.py 的空指针异常
- 添加了空值检查
- 更新了测试用例
- 所有测试通过
```

### 避免的格式
```
✅ 任务完成

📊 详细分析:
• 修复了 auth.py:45 的空指针异常
• 使用了 if x is not None: 检查
• 添加了 try/except 块
✓ 测试通过 (100%)
✓ 代码覆盖率: 95%
```

## 相关文件

- `telegram_mcp_server/server.py` - 主要修复
- `test_markdown_fix.py` - 测试脚本
- `CORRECT_USAGE.md` - 使用指南

## 版本

- 修复版本: v0.2.1
- 修复日期: 2025-10-22
- 影响范围: `telegram_notify`, `telegram_notify_with_actions`
