"""Telegram Bot handlers"""
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from .session import registry
from .message_queue import message_queue
from . import config

logger = logging.getLogger(__name__)

# User context management
user_contexts = {}  # {user_id: {"active_session": session_id}}
pending_messages = {}  # {user_id: message_text}


def format_time_ago(iso_time: str) -> str:
    """Format ISO timestamp as human-readable time ago"""
    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = (now - dt).total_seconds()

        if diff < 60:
            return f"{int(diff)}秒前"
        elif diff < 3600:
            return f"{int(diff / 60)}分钟前"
        elif diff < 86400:
            return f"{int(diff / 3600)}小时前"
        else:
            return f"{int(diff / 86400)}天前"
    except:
        return iso_time


async def cmd_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all active sessions"""
    sessions = registry.list_all()

    if not sessions:
        await update.message.reply_text("没有活跃会话")
        return

    text = "📋 活跃会话：\n\n"
    for i, (sid, session) in enumerate(sessions.items(), 1):
        status_emoji = {
            "running": "▶️",
            "waiting": "⏸️",
            "idle": "⏹️"
        }.get(session.status, "❓")

        text += (
            f"{i}️⃣ {status_emoji} `{sid}`\n"
            f"   📁 `{session.project_path}`\n"
            f"   🕐 {format_time_ago(session.last_active)}\n\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show session status"""
    if not context.args:
        await update.message.reply_text("用法: /status <session_id>")
        return

    session_id = context.args[0]
    session = registry.get(session_id)

    if not session:
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return

    status_emoji = {
        "running": "▶️ 运行中",
        "waiting": "⏸️ 等待回复",
        "idle": "⏹️ 空闲"
    }.get(session.status, "❓ 未知")

    status_text = f"""📊 会话状态
━━━━━━━━━━━━━━━━
🆔 ID: `{session.session_id}`
📁 项目: `{session.project_path}`
⏱️  状态: {status_emoji}
🕐 最后活动: {format_time_ago(session.last_active)}
"""

    if session.last_message:
        status_text += f"💬 最后消息: {session.last_message[:100]}"

    await update.message.reply_text(status_text, parse_mode="Markdown")


async def cmd_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message to specific session (improved with session locking)"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("用法: /to <session_id> [消息]")
        return
    
    session_id = context.args[0]
    
    # Check if session exists
    if not registry.exists(session_id):
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return
    
    # If no message, set as active session
    if len(context.args) == 1:
        if user_id not in user_contexts:
            user_contexts[user_id] = {}
        
        user_contexts[user_id]['active_session'] = session_id
        
        await update.message.reply_text(
            f"📌 已切换到会话: `{session_id}`\n\n"
            f"✅ 后续消息将自动发送到此会话\n"
            f"💡 使用 `/keep off` 取消锁定",
            parse_mode="Markdown"
        )
        return
    
    # Has message, send and set as active session
    message = " ".join(context.args[1:])
    
    message_queue.push(session_id, message)
    
    # Also set as active session
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id]['active_session'] = session_id
    
    await update.message.reply_text(
        f"✅ 消息已发送到 `{session_id}`\n\n"
        f"💬 {message}\n\n"
        f"📌 已锁定此会话，后续消息将自动发送到这里",
        parse_mode="Markdown"
    )


async def cmd_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View or download project file"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "用法: /file <session_id> <file_path> [download]\n\n"
            "示例:\n"
            "/file testtg src/main.py - 查看文件内容\n"
            "/file testtg config.json download - 下载文件"
        )
        return

    session_id = context.args[0]
    file_path = context.args[1]
    download_mode = len(context.args) > 2 and context.args[2] == "download"

    session = registry.get(session_id)
    if not session:
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return

    full_path = os.path.join(session.project_path, file_path)

    if not os.path.exists(full_path):
        await update.message.reply_text(f"❌ 文件不存在: `{file_path}`", parse_mode="Markdown")
        return

    # Check if it's a file (not directory)
    if not os.path.isfile(full_path):
        await update.message.reply_text(f"❌ 不是文件: `{file_path}`", parse_mode="Markdown")
        return

    # If download mode, always send as document
    if download_mode:
        try:
            with open(full_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=os.path.basename(file_path),
                    caption=f"📄 {file_path}"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ 发送文件失败: {str(e)}")
        return

    # Otherwise, try to display content
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # If file is too large, send as document
        if len(content) > 4000:
            with open(full_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=os.path.basename(file_path),
                    caption=f"📄 {file_path} (文件过大，作为附件发送)\n💡 提示: 可直接下载查看"
                )
        else:
            # Detect language for syntax highlighting
            ext = os.path.splitext(file_path)[1]
            lang_map = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".go": "go", ".rs": "rust", ".java": "java",
                ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
                ".sh": "bash", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
                ".xml": "xml", ".html": "html", ".css": "css", ".md": "markdown"
            }
            lang = lang_map.get(ext, "")

            # Truncate if still too long for Telegram
            if len(content) > 3800:
                content = content[:3800] + "\n\n... (已截断)"

            # Try to send with Markdown
            try:
                await update.message.reply_text(
                    f"📄 `{file_path}`\n\n```{lang}\n{content}\n```",
                    parse_mode="Markdown"
                )
            except Exception:
                # Fallback: send as plain text if Markdown fails
                await update.message.reply_text(
                    f"📄 {file_path}\n\n{content}"
                )

    except UnicodeDecodeError:
        # Binary file, send as document
        try:
            with open(full_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=os.path.basename(file_path),
                    caption=f"📄 {file_path} (二进制文件)"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ 发送文件失败: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ 读取文件失败: {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    # Get largest photo
    photo = update.message.photo[-1]
    caption = update.message.caption or "用户发送了一张图片"

    # Download photo
    try:
        file = await context.bot.get_file(photo.file_id)
        file_path = f"/tmp/telegram_photo_{photo.file_id}.jpg"
        await file.download_to_drive(file_path)

        # Format message with image info
        photo_message = f"[图片] {caption}\n文件路径: {file_path}"

        # Check if this is a reply to a message (priority)
        if update.message.reply_to_message:
            replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""

            import re
            session_id = None

            # Try to extract session_id
            match = re.search(r'`([a-zA-Z0-9_-]+)`', replied_text)
            if match and registry.exists(match.group(1)):
                session_id = match.group(1)

            if not session_id:
                all_sessions = registry.list_all()
                for sid in all_sessions.keys():
                    if sid in replied_text:
                        session_id = sid
                        break

            if session_id:
                message_queue.push(session_id, photo_message)
                try:
                    await update.message.set_reaction("👍")
                except:
                    pass
                return

        # No reply, or couldn't extract session - find waiting sessions
        waiting_sessions = registry.list_waiting()

        if len(waiting_sessions) == 0:
            await update.message.reply_text("没有会话在等待。图片已保存到:\n" + file_path)
        elif len(waiting_sessions) == 1:
            session_id = list(waiting_sessions.keys())[0]
            message_queue.push(session_id, photo_message)
            try:
                await update.message.set_reaction("👍")
            except:
                pass
        else:
            # Store photo data first
            import json
            import hashlib

            # Use hash to create short ID
            photo_id = hashlib.md5(photo.file_id.encode()).hexdigest()[:8]

            photo_data = {
                'file_path': file_path,
                'caption': caption,
                'message': photo_message
            }
            with open(f"/tmp/photo_{photo_id}.json", 'w') as f:
                json.dump(photo_data, f)

            # Create buttons with short callback_data
            keyboard = []
            for sid in waiting_sessions.keys():
                keyboard.append([
                    InlineKeyboardButton(
                        f"📤 发送到 {sid}",
                        callback_data=f"photo_{photo_id}_{sid}"  # Short format: photo_HASH_SESSION
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"多个会话在等待，请选择：\n\n📷 {caption}",
                reply_markup=reply_markup
            )

    except Exception as e:
        await update.message.reply_text(f"❌ 处理图片失败: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command messages with smart routing"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check if user has active session context
    if user_id in user_contexts and 'active_session' in user_contexts[user_id]:
        # Has active session, send directly
        session_id = user_contexts[user_id]['active_session']
        await send_to_session(update, session_id, message_text)
        return
    
    # No active session, check how many sessions exist
    sessions = registry.list_all()
    
    if not sessions:
        await update.message.reply_text(
            "❌ 没有活跃会话\n\n"
            "请先在 AI 编程工具中启动会话，或使用命令：\n"
            "• `/sessions` - 查看会话\n"
            "• `/help` - 查看帮助"
        )
        return
    
    if len(sessions) == 1:
        # Only one session, send directly
        session_id = list(sessions.keys())[0]
        await send_to_session(update, session_id, message_text)
        return
    
    # Multiple sessions, show selection buttons
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
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ 取消", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Truncate message for display
    display_message = message_text[:100] + "..." if len(message_text) > 100 else message_text
    
    await update.message.reply_text(
        f"📨 你的消息：\n\n{display_message}\n\n"
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
        
        # Send message
        if not registry.exists(session_id):
            await query.edit_message_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
            return
        
        message_queue.push(session_id, message_text)
        await query.edit_message_text(
            f"✅ 消息已发送到 `{session_id}`\n\n"
            f"💬 {message_text}",
            parse_mode="Markdown"
        )
        
        pending_messages.pop(user_id, None)
        return
    
    if data.startswith("exec:"):
        # Handle action button clicks
        action_id = data.split(":", 1)[1]
        await handle_action_execution(query, action_id)
        return


async def handle_action_execution(query, action_id: str):
    """Handle execution of action buttons"""
    try:
        import json
        from pathlib import Path
        
        # Load actions from file
        actions_file = Path.home() / ".telegram-mcp-actions.json"
        
        if not actions_file.exists():
            await query.edit_message_text("❌ 操作已过期")
            return
        
        with open(actions_file, 'r') as f:
            actions = json.load(f)
        
        if action_id not in actions:
            await query.edit_message_text("❌ 操作已过期")
            return
        
        action_data = actions[action_id]
        session_id = action_data["session_id"]
        command = action_data["command"]
        
        # Check if session still exists
        if not registry.exists(session_id):
            await query.edit_message_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
            return
        
        # Send command to session
        message_queue.push(session_id, command)
        
        # Update message to show execution
        await query.edit_message_text(
            f"✅ 已执行操作\n\n"
            f"📤 发送到: `{session_id}`\n"
            f"💬 指令: {command}",
            parse_mode="Markdown"
        )
        
        # Remove executed action
        actions.pop(action_id, None)
        with open(actions_file, 'w') as f:
            json.dump(actions, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to execute action {action_id}: {e}")
        await query.edit_message_text(f"❌ 执行失败: {str(e)}")


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


async def handle_plain_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages (auto-route to waiting sessions)"""
    message = update.message.text

    # Check if this is a reply to a previous message
    if update.message.reply_to_message:
        # Try to extract session_id from the replied message
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""

        # Extract session_id using multiple patterns
        import re
        session_id = None

        # Pattern 1: [`session-id`]
        match = re.search(r'\[`([a-zA-Z0-9_-]+)`\]', replied_text)
        if match:
            session_id = match.group(1)

        # Pattern 2: [session-id]
        if not session_id:
            match = re.search(r'\[([a-zA-Z0-9_-]+)\]', replied_text)
            if match:
                session_id = match.group(1)

        # Pattern 3: `session-id` (without brackets) - like: ✅ `test-new`
        if not session_id:
            match = re.search(r'`([a-zA-Z0-9_-]+)`', replied_text)
            if match:
                candidate = match.group(1)
                if registry.exists(candidate):
                    session_id = candidate

        # Pattern 4: Search for any known session ID in the text
        if not session_id:
            all_sessions = registry.list_all()
            for sid in all_sessions.keys():
                if sid in replied_text:
                    session_id = sid
                    break

        if session_id and registry.exists(session_id):
            message_queue.push(session_id, message)
            # Silent - user will see Claude's response
            # Add a subtle reaction to confirm
            try:
                await update.message.set_reaction("👍")
            except:
                pass  # Reaction might not be supported
            return

        # If we couldn't extract session_id, show available sessions
        all_sessions = registry.list_all()
        text = "⚠️ 无法识别回复的会话。\n\n"
        if all_sessions:
            text += "可用会话：\n"
            for sid in all_sessions.keys():
                text += f"  /to {sid} {message}\n"
        else:
            text += "当前没有活跃会话。"

        await update.message.reply_text(text)
        return

    # Normal message routing (not a reply)
    # Find sessions waiting for reply
    waiting_sessions = registry.list_waiting()

    if len(waiting_sessions) == 0:
        await update.message.reply_text(
            "没有会话在等待回复。\n"
            "使用 /to <session_id> <消息> 向指定会话发送消息。"
        )
    elif len(waiting_sessions) == 1:
        # Auto-route to the only waiting session
        session_id = list(waiting_sessions.keys())[0]
        message_queue.push(session_id, message)

        # Silent confirmation - user will see Claude's response directly
        # No need to confirm, reduces noise
    else:
        # Multiple sessions waiting, ask user to choose
        text = "多个会话在等待回复，请选择：\n\n"
        for sid in waiting_sessions.keys():
            text += f"/to {sid} {message}\n"

        await update.message.reply_text(text)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Handle photo callback: photo_{photo_id}_{session_id}
    if data.startswith("photo_"):
        import json

        parts = data.split("_")  # photo, photo_id, session_id
        if len(parts) >= 3:
            photo_id = parts[1]
            session_id = parts[2]

            # Load photo data
            try:
                with open(f"/tmp/photo_{photo_id}.json", 'r') as f:
                    photo_data = json.load(f)

                message_queue.push(session_id, photo_data['message'])

                await query.edit_message_text(
                    f"✅ 图片已发送到会话 `{session_id}`",
                    parse_mode="Markdown"
                )

                # Clean up temp file
                try:
                    os.remove(f"/tmp/photo_{photo_id}.json")
                except:
                    pass

            except Exception as e:
                await query.edit_message_text(f"❌ 发送失败: {str(e)}")


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a session"""
    if not context.args:
        await update.message.reply_text("用法: /delete <session_id>")
        return

    session_id = context.args[0]
    session = registry.get(session_id)

    if not session:
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return

    # Try to send exit command
    message_queue.push(session_id, "exit")
    
    await update.message.reply_text(
        f"🗑️ 正在删除会话 `{session_id}`...\n\n"
        f"已发送退出命令。\n"
        f"- 如果 AI 助手正在运行，它会收到退出指令\n"
        f"- 如果进程已关闭，会话将被清理\n\n"
        f"会话将在 10 秒后从列表中移除。",
        parse_mode="Markdown"
    )
    
    # Wait a bit for the session to process exit
    await asyncio.sleep(10)
    
    # Remove session from registry
    if registry.exists(session_id):
        registry.sessions.pop(session_id, None)
        registry._save_to_file()
        await update.message.reply_text(
            f"✅ 会话 `{session_id}` 已删除",
            parse_mode="Markdown"
        )


async def cmd_keep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keep sending messages to a specific session"""
    user_id = update.effective_user.id
    
    if not context.args:
        # Show current active session
        if user_id in user_contexts and 'active_session' in user_contexts[user_id]:
            session_id = user_contexts[user_id]['active_session']
            await update.message.reply_text(
                f"📌 当前活跃会话: `{session_id}`\n\n"
                f"使用 `/keep off` 取消锁定\n"
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
    
    # Special command: cancel lock
    if session_id.lower() in ['off', 'cancel', 'clear']:
        if user_id in user_contexts:
            user_contexts[user_id].pop('active_session', None)
        await update.message.reply_text("✅ 已取消会话锁定")
        return
    
    # Check if session exists
    if not registry.exists(session_id):
        await update.message.reply_text(f"❌ 会话 `{session_id}` 不存在", parse_mode="Markdown")
        return
    
    # Set active session
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    
    user_contexts[user_id]['active_session'] = session_id
    
    await update.message.reply_text(
        f"📌 已锁定会话: `{session_id}`\n\n"
        f"✅ 后续消息将自动发送到此会话\n"
        f"💡 使用 `/keep off` 取消锁定",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """🤖 Telegram MCP Server 使用帮助

📋 会话管理
/sessions - 列出所有活跃会话
/status <session_id> - 查看会话状态
/delete <session_id> - 删除会话（发送退出命令）

💬 消息发送
/to <session_id> [消息] - 向指定会话发送消息（或锁定会话）
/keep <session_id> - 锁定会话（后续消息自动发送）
/keep off - 取消会话锁定
直接发送消息 - 自动发送到锁定的会话或唯一等待的会话

📄 文件操作
/file <session_id> <file_path> - 查看文件内容（带语法高亮）
/file <session_id> <file_path> download - 下载文件

💬 自然语言请求（在无人值守模式下）
"查看 src/main.py" - AI 会自动发送文件
"发送 config.json 给我" - AI 会自动发送
"展示刚才修改的代码" - AI 会智能发送代码段

❓ 帮助
/help - 显示此帮助信息

💡 提示
- 如果只有一个会话在等待回复，直接发送消息即可
- 会话 ID 通常是项目目录名
- 使用 TELEGRAM_SESSION 环境变量自定义会话名
- 在无人值守模式下，AI 会智能判断何时发送代码/文件
"""
    await update.message.reply_text(help_text)


def setup_bot(token: str) -> Application:
    """Setup and configure bot"""
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("sessions", cmd_sessions))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("to", cmd_to))
    application.add_handler(CommandHandler("keep", cmd_keep))
    application.add_handler(CommandHandler("file", cmd_file))
    application.add_handler(CommandHandler("delete", cmd_delete))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("start", cmd_help))

    # Add callback query handler (for inline keyboard buttons) - must be before other handlers
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add photo handler
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )

    # Add smart message handler (with session context and selection)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application
