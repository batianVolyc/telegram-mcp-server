# 准备实施 - 完整代码清单

## 🎯 状态

所有设计文档已完成：
- ✅ BOT_IMPROVEMENTS.md - 技术方案
- ✅ DYNAMIC_BUTTONS_EXAMPLES.md - 使用示例
- ✅ IMPLEMENTATION_PLAN.md - 实施计划

现在需要修改代码实现功能。

---

## 📝 需要添加的代码

### 1. server.py - 添加新工具（在 telegram_notify 后面）

在 `list_tools()` 函数的返回列表中，在 `telegram_notify` 工具后添加：

```python
Tool(
    name="telegram_notify_with_actions",
    description="""
    发送带有动态操作按钮的通知到 Telegram
    
    让你根据当前情况为用户提供智能的下一步操作建议。
    
    参数：
    - event: 事件类型（completed/error/question/progress）
    - summary: 简短总结（必填，200字以内）
    - details: 详细信息（可选）
    - actions: 操作按钮列表（可选，最多 4 个）
    
    actions 格式：
    [
        {
            "text": "按钮显示文字",
            "action": "用户点击后发送的指令",
            "emoji": "可选的 emoji"
        }
    ]
    
    使用场景：
    
    1. 任务完成 - 提供下一步建议：
    telegram_notify_with_actions(
        event="completed",
        summary="✅ 完成用户认证模块\\n- 实现登录/注册\\n- JWT验证\\n- 15个测试通过",
        actions=[
            {"text": "💡 实现权限管理", "action": "继续实现权限管理模块"},
            {"text": "⚡ 优化性能", "action": "优化数据库查询性能"}
        ]
    )
    
    2. 遇到错误 - 提供解决方案：
    telegram_notify_with_actions(
        event="error",
        summary="❌ 导入错误\\nModuleNotFoundError: No module named 'jwt'",
        actions=[
            {"text": "🔧 自动修复", "action": "运行 pip install PyJWT 并重试"},
            {"text": "📝 添加到依赖", "action": "将 PyJWT 添加到 requirements.txt"}
        ]
    )
    
    3. 需要决策 - 提供选项：
    telegram_notify_with_actions(
        event="question",
        summary="❓ 数据库选择\\n需要选择数据库方案",
        actions=[
            {"text": "1️⃣ PostgreSQL（推荐）", "action": "使用 PostgreSQL"},
            {"text": "2️⃣ SQLite", "action": "使用 SQLite"}
        ]
    )
    
    按钮设计原则：
    - 明确具体："💡 优化这 3 处性能瓶颈" 而不是 "优化"
    - 标记推荐：用 💡 标记推荐选项
    - 数量适中：最多 4 个按钮
    - 可选性：用户可以忽略按钮直接发送指令
    
    注意：
    - 按钮是建议，不是强制选择
    - 如果没有明确的下一步，可以不提供按钮（actions=[]）
    - 消息末尾会自动添加提示："💡 这些是建议的下一步，你也可以直接发送其他指令"
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "event": {
                "type": "string",
                "enum": ["completed", "error", "question", "progress"],
                "description": "事件类型"
            },
            "summary": {
                "type": "string",
                "description": "简短总结（必填，200字以内）",
                "maxLength": 200
            },
            "details": {
                "type": "string",
                "description": "详细信息（可选）"
            },
            "actions": {
                "type": "array",
                "description": "操作按钮列表（可选，最多 4 个）",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "按钮显示文字"
                        },
                        "action": {
                            "type": "string",
                            "description": "用户点击后发送的指令"
                        },
                        "emoji": {
                            "type": "string",
                            "description": "可选的 emoji"
                        }
                    },
                    "required": ["text", "action"]
                },
                "maxItems": 4
            }
        },
        "required": ["event", "summary"]
    }
),
```

### 2. server.py - 添加处理函数（在 call_tool 函数中）

在 `call_tool()` 函数的 if-elif 链中添加：

```python
elif name == "telegram_notify_with_actions":
    return await handle_telegram_notify_with_actions(session, arguments)
```

### 3. server.py - 实现处理函数（在文件末尾，其他 handle 函数附近）

```python
async def handle_telegram_notify_with_actions(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_notify_with_actions tool"""
    event = arguments.get("event")
    summary = arguments.get("summary", "")
    details = arguments.get("details", "")
    actions = arguments.get("actions", [])
    
    # Validate summary length
    if len(summary) > 200:
        return [TextContent(
            type="text",
            text="错误: summary 过长，请精炼到200字以内"
        )]
    
    # Validate actions count
    if len(actions) > 4:
        return [TextContent(
            type="text",
            text="错误: 最多只能提供 4 个操作按钮"
        )]
    
    # Format message
    emoji_map = {
        "completed": "✅",
        "error": "❌",
        "question": "❓",
        "progress": "⏳"
    }
    
    message = f"{emoji_map.get(event, '🔔')} [`{session.session_id}`]\n{summary}"
    
    if details:
        message += f"\n\n━━━━━━━━━━━━\n📝 详情:\n{details}"
    
    # Add hint about buttons
    if actions:
        message += "\n\n💡 这些是建议的下一步，你也可以直接发送其他指令"
    
    # Update session
    session.last_message = summary
    session.update_activity()
    registry.update_session(session)
    
    # Send to Telegram with buttons
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import httpx
        import json
        import hashlib
        import time
        
        # Create inline keyboard
        keyboard = []
        action_store = {}
        
        for idx, action in enumerate(actions):
            emoji_prefix = action.get("emoji", "")
            text = f"{emoji_prefix} {action['text']}" if emoji_prefix else action['text']
            
            # Generate unique action ID
            action_id = hashlib.md5(
                f"{session.session_id}:{time.time()}:{idx}".encode()
            ).hexdigest()[:16]
            
            # Store action command
            action_store[action_id] = {
                "session_id": session.session_id,
                "command": action["action"],
                "timestamp": time.time()
            }
            
            keyboard.append([{
                "text": text,
                "callback_data": f"exec:{action_id}"
            }])
        
        # Save action store to a temporary file
        if action_store:
            import os
            from pathlib import Path
            
            actions_file = Path.home() / ".claude" / "telegram-mcp-actions.json"
            actions_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing actions
            existing_actions = {}
            if actions_file.exists():
                try:
                    with open(actions_file, 'r') as f:
                        existing_actions = json.load(f)
                except:
                    pass
            
            # Merge and save
            existing_actions.update(action_store)
            
            # Clean old actions (older than 1 hour)
            current_time = time.time()
            existing_actions = {
                k: v for k, v in existing_actions.items()
                if current_time - v.get("timestamp", 0) < 3600
            }
            
            with open(actions_file, 'w') as f:
                json.dump(existing_actions, f, indent=2)
        
        # Send message with inline keyboard
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": session.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        if keyboard:
            payload["reply_markup"] = {"inline_keyboard": keyboard}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
        
        return [TextContent(
            type="text",
            text=f"✅ 已发送通知到 Telegram (会话: {session.session_id}, 包含 {len(actions)} 个操作按钮)"
        )]
    except Exception as e:
        logger.error(f"Failed to send notification with actions: {e}")
        return [TextContent(
            type="text",
            text=f"❌ 发送失败: {str(e)}"
        )]
```

---

## 📊 实施状态

- ✅ 设计文档完成
- ⏳ 代码实现待完成
- ⏳ 测试待进行

---

## 🚀 下一步

1. 修改 `server.py` 添加新工具
2. 修改 `bot.py` 添加按钮处理
3. 测试功能
4. 推送到 GitHub

由于代码量较大，建议：
1. 先实现核心的 `telegram_notify_with_actions` 工具
2. 测试基本功能
3. 再添加会话管理功能
4. 最后添加智能选择功能

---

**所有设计已完成，代码清单已准备好！** 🎯
