# Telegram Bot 交互改进方案

## 🎯 改进目标

让用户在 Telegram 中更方便地管理多个 AI 编程会话，获得更清晰的反馈，更容易做出下一步决策。

---

## 📋 改进 1: 未指定会话时显示按钮选择

### 当前行为
用户发送消息但没用 `/to`，消息被忽略或提示错误。

### 改进后行为
1. 用户发送普通消息（不是命令）
2. Bot 检测到有多个活跃会话
3. 显示内联按钮让用户选择会话
4. 用户点击按钮后，消息自动发送到选择的会话

### 实现代码

```python
# 在 bot.py 中添加

# 存储用户待发送的消息
pending_messages = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command messages"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # 检查是否有活跃会话上下文
    if user_id in context.user_data and 'active_session' in context.user_data[user_id]:
        # 有活跃会话，直接发送
        session_id = context.user_data[user_id]['active_session']
        await send_to_session(update, session_id, message_text)
        return
    
    # 没有活跃会话，检查有多少会话
    sessions = registry.list_all()
    
    if not sessions:
        await update.message.reply_text(
            "❌ 没有活跃会话\n\n"
            "请先在 AI 编程工具中启动会话"
        )
        return
    
    if len(sessions) == 1:
        # 只有一个会话，直接发送
        session_id = list(sessions.keys())[0]
        await send_to_session(update, session_id, message_text)
        return
    
    # 多个会话，显示选择按钮
    pending_messages[user_id] = message_text
    
    keyboard = []
    for sid, session in sessions.items():
        status_emoji = {
            "running": "▶️",
            "waiting": "⏸️",
            "idle": "⏹️"
        }.get(session.status, "❓")
        
        button_text = f"{status_emoji} {sid}"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"send_to:{sid}"
        )])
    
    # 添加取消按钮
    keyboard.append([InlineKeyboardButton("❌ 取消", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📨 你的消息：\n\n{message_text[:100]}...\n\n"
        f"请选择要发送到的会话：",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "cancel":
        await query.edit_message_text("❌ 已取消")
        pending_messages.pop(user_id, None)
        return
    
    if data.startswith("send_to:"):
        session_id = data.split(":", 1)[1]
        message_text = pending_messages.get(user_id)
        
        if not message_text:
            await query.edit_message_text("❌ 消息已过期，请重新发送")
            return
        
        # 发送消息
        if not registry.exists(session_id):
            await query.edit_message_text(f"❌ 会话 `{session_id}` 不存在")
            return
        
        message_queue.push(session_id, message_text)
        await query.edit_message_text(
            f"✅ 消息已发送到 `{session_id}`\n\n"
            f"💬 {message_text}",
            parse_mode="Markdown"
        )
        
        pending_messages.pop(user_id, None)
        return
    
    if data.startswith("next_action:"):
        # 处理下一步操作按钮
        action = data.split(":", 1)[1]
        await handle_next_action(query, action)
        return


async def send_to_session(update: Update, session_id: str, message: str):
    """Send message to session"""
    if not registry.exists(session_id):
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return
    
    message_queue.push(session_id, message)
    await update.message.reply_text(
        f"✅ 消息已发送到 `{session_id}`\n\n"
        f"💬 {message}",
        parse_mode="Markdown"
    )
```

---

## 📋 改进 2: 保持会话上下文

### 新命令：`/keep <session_id>`

设置当前活跃会话，后续所有消息自动发送到该会话。

### 实现代码

```python
async def cmd_keep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keep sending messages to a specific session"""
    user_id = update.effective_user.id
    
    if not context.args:
        # 显示当前活跃会话
        if user_id in context.user_data and 'active_session' in context.user_data[user_id]:
            session_id = context.user_data[user_id]['active_session']
            await update.message.reply_text(
                f"📌 当前活跃会话: `{session_id}`\n\n"
                f"使用 `/keep` 取消锁定\n"
                f"使用 `/keep <session_id>` 切换会话",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ 没有活跃会话\n\n"
                "使用 `/keep <session_id>` 设置活跃会话"
            )
        return
    
    session_id = context.args[0]
    
    # 特殊命令：取消锁定
    if session_id.lower() in ['off', 'cancel', 'clear']:
        if user_id in context.user_data:
            context.user_data[user_id].pop('active_session', None)
        await update.message.reply_text("✅ 已取消会话锁定")
        return
    
    # 检查会话是否存在
    if not registry.exists(session_id):
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return
    
    # 设置活跃会话
    if user_id not in context.user_data:
        context.user_data[user_id] = {}
    
    context.user_data[user_id]['active_session'] = session_id
    
    await update.message.reply_text(
        f"📌 已锁定会话: `{session_id}`\n\n"
        f"✅ 后续消息将自动发送到此会话\n"
        f"💡 使用 `/keep off` 取消锁定",
        parse_mode="Markdown"
    )


async def cmd_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message to specific session (improved)"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("用法: /to <session_id> [消息]")
        return
    
    session_id = context.args[0]
    
    # 如果没有消息，设置为活跃会话
    if len(context.args) == 1:
        if user_id not in context.user_data:
            context.user_data[user_id] = {}
        
        context.user_data[user_id]['active_session'] = session_id
        
        await update.message.reply_text(
            f"📌 已切换到会话: `{session_id}`\n\n"
            f"✅ 后续消息将自动发送到此会话\n"
            f"💡 使用 `/keep off` 取消锁定",
            parse_mode="Markdown"
        )
        return
    
    # 有消息，发送并设置为活跃会话
    message = " ".join(context.args[1:])
    
    if not registry.exists(session_id):
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return
    
    message_queue.push(session_id, message)
    
    # 同时设置为活跃会话
    if user_id not in context.user_data:
        context.user_data[user_id] = {}
    context.user_data[user_id]['active_session'] = session_id
    
    await update.message.reply_text(
        f"✅ 消息已发送到 `{session_id}`\n\n"
        f"💬 {message}\n\n"
        f"📌 已锁定此会话，后续消息将自动发送到这里",
        parse_mode="Markdown"
    )
```

---

## 📋 改进 3: 优化 AI 反馈提示词

### 当前问题
AI 发送的通知过于简单，缺少结构和下一步建议。

### 改进方案

在 `server.py` 的 `telegram_notify` 工具描述中，添加更详细的提示词指导：

```python
Tool(
    name="telegram_notify",
    description="""
    发送结构化通知到 Telegram - 用于汇报任务进度和结果
    
    ⚠️ 重要：这是用户了解你工作进展的主要方式，请提供清晰、有价值的反馈
    
    参数：
    - event: 事件类型（completed/error/question/progress）
    - summary: 简短总结（必填，200字以内）
    - details: 详细信息（可选，建议使用）
    
    📝 最佳实践 - 结构化反馈：
    
    1. **任务完成时** (event="completed"):
       summary 格式：
       ✅ 完成的工作
       - 主要成果1
       - 主要成果2
       - 主要成果3
       
       details 格式：
       📊 详细信息：
       - 修改的文件：file1.py, file2.py
       - 新增功能：xxx
       - 测试结果：12/12 passed
       
       💡 下一步建议：
       1. 继续实现 xxx 功能
       2. 或者优化 xxx 性能
       
       示例：
       telegram_notify(
           event="completed",
           summary="✅ 完成用户认证模块\\n- 实现登录/注册功能\\n- 添加 JWT token 验证\\n- 通过所有单元测试",
           details="📊 详细信息：\\n- 修改文件：auth.py, user.py, test_auth.py\\n- 新增 API：/login, /register, /refresh\\n- 测试：15/15 passed\\n\\n💡 下一步建议：\\n1. 继续实现权限管理模块\\n2. 或者优化数据库查询性能"
       )
    
    2. **遇到问题时** (event="question"):
       summary 格式：
       ❓ 需要决策：[问题描述]
       
       选项：
       1️⃣ 方案A - [简短描述]
       2️⃣ 方案B - [简短描述]
       3️⃣ 方案C - [简短描述]
       
       💡 推荐：方案X，因为 [原因]
       
       details 格式：
       📋 详细分析：
       - 方案A：[优缺点]
       - 方案B：[优缺点]
       - 方案C：[优缺点]
       
       示例：
       telegram_notify(
           event="question",
           summary="❓ 需要决策：数据库设计方案\\n\\n选项：\\n1️⃣ 使用 PostgreSQL - 功能强大\\n2️⃣ 使用 SQLite - 简单轻量\\n3️⃣ 使用 MongoDB - 灵活schema\\n\\n💡 推荐：PostgreSQL，因为项目需要复杂查询和事务支持",
           details="📋 详细分析：\\n- PostgreSQL：✅ 强大功能 ✅ 事务支持 ❌ 需要额外部署\\n- SQLite：✅ 零配置 ✅ 轻量 ❌ 并发性能差\\n- MongoDB：✅ 灵活 ❌ 不适合关系型数据"
       )
    
    3. **进度更新时** (event="progress"):
       summary 格式：
       ⏳ 进行中：[当前任务]
       
       进度：[X/Y] 或 [百分比]
       
       已完成：
       - ✅ 项目1
       - ✅ 项目2
       
       进行中：
       - 🔄 项目3
       
       示例：
       telegram_notify(
           event="progress",
           summary="⏳ 进行中：重构数据库访问层\\n\\n进度：3/5 (60%)\\n\\n已完成：\\n- ✅ 用户模块\\n- ✅ 认证模块\\n- ✅ 权限模块\\n\\n进行中：\\n- 🔄 订单模块",
           details="预计剩余时间：10分钟\\n\\n💡 完成后将继续：\\n1. 优化查询性能\\n2. 添加缓存层"
       )
    
    4. **错误报告时** (event="error"):
       summary 格式：
       ❌ 错误：[错误描述]
       
       位置：[文件:行号]
       
       details 格式：
       🐛 错误详情：
       [错误信息]
       
       🔍 可能原因：
       - 原因1
       - 原因2
       
       💡 建议解决方案：
       1. 方案1
       2. 方案2
       
       示例：
       telegram_notify(
           event="error",
           summary="❌ 错误：导入失败\\n\\n位置：auth.py:45\\n\\n错误：ModuleNotFoundError: No module named 'jwt'",
           details="🐛 错误详情：\\n缺少 PyJWT 依赖包\\n\\n💡 建议解决方案：\\n1. 运行 pip install PyJWT\\n2. 或添加到 requirements.txt"
       )
    
    ⚠️ 注意事项：
    - summary 必须简洁明了（200字以内）
    - 使用 emoji 增加可读性
    - 提供具体的下一步建议
    - 让用户容易做出决策
    - 避免技术术语过多
    - 重点突出关键信息
    
    ❌ 不好的示例：
    telegram_notify(
        event="completed",
        summary="完成了"  # 太简单，没有信息量
    )
    
    ✅ 好的示例：
    telegram_notify(
        event="completed",
        summary="✅ 完成用户认证\\n- 登录/注册 API\\n- JWT token 验证\\n- 15个测试全部通过\\n\\n💡 下一步：实现权限管理？",
        details="修改文件：auth.py, user.py\\n新增 API：/login, /register\\n测试覆盖率：95%"
    )
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
                "description": "简短总结（必填，200字以内，使用结构化格式）",
                "maxLength": 200
            },
            "details": {
                "type": "string",
                "description": "详细信息（强烈建议填写，包含具体数据和下一步建议）"
            }
        },
        "required": ["event", "summary"]
    }
)
```

### 添加动态操作按钮 - 新 MCP 工具

创建一个新的 MCP 工具 `telegram_notify_with_actions`，让 AI 根据具体情况动态生成按钮：

```python
Tool(
    name="telegram_notify_with_actions",
    description="""
    发送带有动态操作按钮的通知到 Telegram
    
    这个工具允许你根据当前情况，为用户提供智能的下一步操作建议。
    
    参数：
    - event: 事件类型（completed/error/question/progress）
    - summary: 简短总结（必填，200字以内）
    - details: 详细信息（可选）
    - actions: 操作按钮列表（可选，最多 4 个）
    
    📋 actions 参数格式：
    [
        {
            "text": "按钮显示文字",
            "action": "用户点击后发送的指令",
            "emoji": "可选的 emoji"
        }
    ]
    
    💡 使用场景和示例：
    
    1. **任务完成 - 提供下一步建议**
    
    telegram_notify_with_actions(
        event="completed",
        summary="✅ 完成用户认证模块\\n- 实现登录/注册\\n- JWT token 验证\\n- 15个测试通过",
        details="修改文件：auth.py, user.py\\n测试覆盖率：95%",
        actions=[
            {
                "text": "💡 实现权限管理",
                "action": "继续实现权限管理模块，包括角色和权限分配",
                "emoji": "💡"
            },
            {
                "text": "⚡ 优化性能",
                "action": "优化数据库查询性能，添加缓存层",
                "emoji": "⚡"
            }
        ]
    )
    
    用户看到：
    ✅ 完成用户认证模块
    - 实现登录/注册
    - JWT token 验证
    - 15个测试通过
    
    [按钮: 💡 实现权限管理] [按钮: ⚡ 优化性能]
    
    💡 这些是建议的下一步，你也可以直接发送其他指令
    
    2. **遇到错误 - 提供解决方案**
    
    telegram_notify_with_actions(
        event="error",
        summary="❌ 导入错误\\n\\n位置：auth.py:45\\n错误：ModuleNotFoundError: No module named 'jwt'",
        details="缺少 PyJWT 依赖包",
        actions=[
            {
                "text": "🔧 自动修复",
                "action": "运行 pip install PyJWT 并重试",
                "emoji": "🔧"
            },
            {
                "text": "📝 添加到依赖",
                "action": "将 PyJWT 添加到 requirements.txt",
                "emoji": "📝"
            },
            {
                "text": "🔍 显示错误代码",
                "action": "显示 auth.py 第 40-50 行的代码",
                "emoji": "🔍"
            }
        ]
    )
    
    3. **需要决策 - 提供选项**
    
    telegram_notify_with_actions(
        event="question",
        summary="❓ 数据库设计方案选择\\n\\n发现3种可行方案，需要你的决策",
        details="方案A：PostgreSQL - 功能强大但需要部署\\n方案B：SQLite - 简单但并发差\\n方案C：MongoDB - 灵活但不适合关系型",
        actions=[
            {
                "text": "1️⃣ PostgreSQL（推荐）",
                "action": "使用 PostgreSQL，我会配置 docker-compose",
                "emoji": "1️⃣"
            },
            {
                "text": "2️⃣ SQLite",
                "action": "使用 SQLite，适合小型项目",
                "emoji": "2️⃣"
            },
            {
                "text": "3️⃣ MongoDB",
                "action": "使用 MongoDB，我会调整数据模型",
                "emoji": "3️⃣"
            }
        ]
    )
    
    4. **进度更新 - 提供控制选项**
    
    telegram_notify_with_actions(
        event="progress",
        summary="⏳ 重构进行中\\n\\n进度：3/5 (60%)\\n\\n已完成：用户、认证、权限模块\\n进行中：订单模块",
        details="预计剩余时间：10分钟",
        actions=[
            {
                "text": "⏸️ 暂停等待",
                "action": "暂停当前任务，等待进一步指示",
                "emoji": "⏸️"
            },
            {
                "text": "📊 查看详情",
                "action": "显示已完成模块的详细信息和代码变更",
                "emoji": "📊"
            }
        ]
    )
    
    ⚠️ 按钮设计原则：
    
    1. **明确性**：按钮文字要清楚说明会做什么
       ✅ "🔧 自动修复依赖问题"
       ❌ "修复"
    
    2. **建议性**：使用"💡"标记推荐选项，但不强迫
       ✅ "💡 实现权限管理（推荐）"
       ✅ "⚡ 优化性能"
    
    3. **数量限制**：最多 4 个按钮，避免选择困难
       ✅ 2-3 个主要选项
       ❌ 6-7 个选项
    
    4. **emoji 使用**：增加可读性
       💡 = 推荐/建议
       🔧 = 修复/解决
       📊 = 查看/详情
       ⏸️ = 暂停/等待
       ⚡ = 优化/性能
       🔍 = 查看/检查
       📝 = 编辑/添加
       1️⃣2️⃣3️⃣ = 选项编号
    
    5. **action 内容**：要具体明确
       ✅ "运行 pip install PyJWT 并重新执行导入"
       ❌ "修复"
    
    ⚠️ 重要提示：
    - 按钮是**建议**，不是强制选择
    - 用户可以忽略按钮，直接发送其他指令
    - 在消息末尾添加提示："💡 这些是建议的下一步，你也可以直接发送其他指令"
    - 如果没有明确的下一步建议，可以不提供按钮（actions=[]）
    
    ❌ 不要做的：
    - 不要提供模糊的按钮："继续"、"下一步"
    - 不要提供太多选项（超过 4 个）
    - 不要强迫用户必须点击按钮
    - 不要在每个通知都加按钮（只在有明确建议时）
    
    ✅ 好的示例：
    telegram_notify_with_actions(
        event="completed",
        summary="✅ 完成代码审查\\n- 发现 3 个可优化点\\n- 代码质量：B+",
        actions=[
            {
                "text": "💡 优化这 3 处",
                "action": "自动优化发现的 3 个可优化点",
                "emoji": "💡"
            },
            {
                "text": "📊 查看详情",
                "action": "显示每个优化点的详细说明和代码位置",
                "emoji": "📊"
            }
        ]
    )
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
)
```

### 实现代码

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
    emoji = {
        "completed": "✅",
        "error": "❌",
        "question": "❓",
        "progress": "⏳"
    }
    
    message = f"{emoji.get(event, '🔔')} [`{session.session_id}`]\n{summary}"
    
    if details:
        message += f"\n\n━━━━━━━━━━━━\n📝 详情:\n{details}"
    
    # Add hint about buttons
    if actions:
        message += "\n\n💡 这些是建议的下一步，你也可以直接发送其他指令"
    
    # Update session
    session.last_message = summary
    session.update_activity()
    registry.update_session(session)
    
    # Create inline keyboard
    keyboard = []
    for action in actions:
        emoji_prefix = action.get("emoji", "")
        text = f"{emoji_prefix} {action['text']}" if emoji_prefix else action['text']
        
        # Store action in a temporary dict for callback
        action_id = f"action_{session.session_id}_{len(keyboard)}"
        # TODO: Store action['action'] in a persistent store
        
        keyboard.append([InlineKeyboardButton(
            text,
            callback_data=f"execute:{session.session_id}:{action_id}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Send to Telegram
    try:
        await bot.send_message(
            chat_id=session.chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return [TextContent(
            type="text",
            text=f"✅ 已发送通知到 Telegram (会话: {session.session_id}, 包含 {len(actions)} 个操作按钮)"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送失败: {str(e)}"
        )]
```

---

## 📊 改进效果对比

### 改进前
```
用户: 分析项目结构
AI: 完成了
```

### 改进后
```
用户: 分析项目结构

AI: ✅ 完成项目结构分析
- 发现 15 个 Python 文件
- 3 个主要模块：auth, api, db
- 代码质量良好，测试覆盖率 85%

📊 详细信息：
- 核心文件：main.py, auth.py, api.py
- 配置文件：config.py, requirements.txt
- 测试文件：12 个测试文件

💡 下一步建议：
1. 继续优化数据库查询性能
2. 或者添加 API 文档

[按钮: ✅ 继续下一步] [按钮: 📊 查看详情] [按钮: ⏸️ 暂停等待]
```

---

## 🎯 实施计划

1. **Phase 1**: 实现会话选择按钮和上下文保持
2. **Phase 2**: 更新 `telegram_notify` 的提示词
3. **Phase 3**: 添加操作按钮和回调处理
4. **Phase 4**: 测试和优化

需要我现在开始实现这些改进吗？
