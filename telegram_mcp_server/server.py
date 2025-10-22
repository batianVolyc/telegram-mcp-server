"""MCP Server implementation"""
import os
import time
import logging
import asyncio
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent

from .session import registry
from .message_queue import message_queue
from . import config

logger = logging.getLogger(__name__)

# Global telegram bot instance (set by main)
telegram_bot = None


def get_session_id() -> str:
    """
    Get session ID for current Claude Code instance
    Priority: TELEGRAM_SESSION env var > current directory name
    """
    if config.TELEGRAM_SESSION_ID:
        return config.TELEGRAM_SESSION_ID

    # Use current working directory name as session ID
    cwd = os.getcwd()
    session_id = os.path.basename(cwd)

    return session_id


def get_project_path() -> str:
    """Get absolute path of current project"""
    return os.getcwd()


async def ensure_session_registered(session_id: str) -> None:
    """
    Ensure session is registered
    Lazy registration: only register when first tool is called
    """
    if not registry.exists(session_id):
        project_path = get_project_path()
        chat_id = config.TELEGRAM_CHAT_ID

        session = registry.register(session_id, project_path, chat_id)
        logger.info(f"Registered session: {session_id} at {project_path}")

        # Send notification to Telegram
        if telegram_bot:
            try:
                message = (
                    f"✅ 新会话已启动\n"
                    f"🆔 `{session_id}`\n"
                    f"📁 `{project_path}`\n"
                    f"使用 /to {session_id} <消息> 与之交互"
                )

                await send_telegram_message(chat_id, message)
            except Exception as e:
                logger.error(f"Failed to send registration notification: {e}")


def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram Markdown"""
    # Characters that need escaping in Telegram Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


async def send_telegram_message(chat_id: str, message: str, parse_mode: str = "Markdown") -> None:
    """Send message to Telegram (async) using HTTP API"""
    import httpx

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    # Only add parse_mode if it's not None
    if parse_mode:
        payload["parse_mode"] = parse_mode

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
            logger.error(f"Failed to send Telegram message: {e}")
            raise
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        raise


def get_poll_interval(elapsed_seconds: float) -> int:
    """
    Get polling interval based on elapsed time
    Progressive slowdown: 30s -> 60s -> 120s
    """
    if elapsed_seconds < config.POLL_THRESHOLDS[0]:  # < 10 minutes
        return config.POLL_INTERVALS[0]  # 30 seconds
    elif elapsed_seconds < config.POLL_THRESHOLDS[1]:  # < 1 hour
        return config.POLL_INTERVALS[1]  # 60 seconds
    else:
        return config.POLL_INTERVALS[2]  # 120 seconds


# Create MCP server
server = Server("telegram")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="telegram_notify",
            description="""
            ⚠️ 这是 Telegram MCP Server 的通知工具
            用于向用户的 Telegram Bot 发送任务进度通知
            
            ❌ 这不是通用的 Telegram 消息发送工具
            ❌ 不能发送消息到任意 Telegram 用户或群组
            ✅ 只能发送通知到配置的 Telegram Bot（用户会在 Telegram 中收到）
            
            💡 推荐使用 telegram_notify_with_actions 代替此工具
            telegram_notify_with_actions 提供动态按钮，用户体验更好

            此工具适用于：
            - 简单的状态更新（不需要用户交互）
            - 快速通知（无需提供下一步建议）
            - 向后兼容旧代码

            参数：
            - event: 事件类型（completed/error/question/progress）
            - summary: 简短总结（必填，200字以内）
            - details: 详细信息（可选）

            示例：
            telegram_notify(
                event="completed",
                summary="修复了 auth.py:45 的空指针异常，所有测试通过"
            )

            💡 更好的选择：使用 telegram_notify_with_actions 提供智能建议按钮
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
                    }
                },
                "required": ["event", "summary"]
            }
        ),
        Tool(
            name="telegram_notify_with_actions",
            description="""
            ⭐ 推荐：发送带有动态操作按钮的智能通知到 Telegram
            
            ⚠️ 这是 Telegram MCP Server 的通知工具（增强版）
            用于向用户的 Telegram Bot 发送任务进度通知，并提供智能操作建议
            
            ❌ 这不是通用的 Telegram 消息发送工具
            ❌ 不能发送消息到任意 Telegram 用户或群组
            ✅ 只能发送通知到配置的 Telegram Bot（用户会在 Telegram 中收到）
            
            这是 telegram_notify 的增强版本，可以根据当前情况为用户提供智能的下一步操作建议。
            
            优势：
            - ✅ 提供 2-4 个智能操作按钮，用户一键执行
            - ✅ 按钮是建议，不强制，用户可以忽略
            - ✅ 自动添加提示："💡 这些是建议的下一步，你也可以直接发送其他指令"
            - ✅ 即使不提供按钮（actions=[]），也可以正常使用
            
            参数：
            - event: 事件类型（completed/error/question/progress）
            - summary: 简短总结（必填，200字以内）
            - details: 详细信息（可选，建议填写）
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
                details="修改文件：auth.py, user.py\\n测试覆盖率：95%",
                actions=[
                    {"text": "实现权限管理", "action": "继续实现权限管理模块，包括角色和权限分配", "emoji": "💡"},
                    {"text": "优化性能", "action": "优化数据库查询性能，添加缓存层", "emoji": "⚡"}
                ]
            )
            
            2. 遇到错误 - 提供解决方案：
            telegram_notify_with_actions(
                event="error",
                summary="❌ 导入错误\\nModuleNotFoundError: No module named 'jwt'",
                details="缺少 PyJWT 依赖包",
                actions=[
                    {"text": "自动修复", "action": "运行 pip install PyJWT 并重试", "emoji": "🔧"},
                    {"text": "添加到依赖", "action": "将 PyJWT 添加到 requirements.txt", "emoji": "📝"},
                    {"text": "显示错误代码", "action": "显示出错位置的代码", "emoji": "🔍"}
                ]
            )
            
            3. 需要决策 - 提供选项：
            telegram_notify_with_actions(
                event="question",
                summary="❓ 数据库选择\\n需要选择数据库方案",
                details="方案A：PostgreSQL - 功能强大\\n方案B：SQLite - 简单轻量",
                actions=[
                    {"text": "PostgreSQL（推荐）", "action": "使用 PostgreSQL，我会配置 docker-compose", "emoji": "1️⃣"},
                    {"text": "SQLite", "action": "使用 SQLite，适合小型项目", "emoji": "2️⃣"}
                ]
            )
            
            按钮设计原则：
            - 明确具体："💡 优化这 3 处性能瓶颈" 而不是 "优化"
            - 标记推荐：用 💡 标记推荐选项，但不强迫用户选择
            - 数量适中：最多 4 个按钮，避免选择困难
            - 可选性：用户可以忽略按钮，直接发送其他指令
            
            注意：
            - 按钮是建议，不是强制选择
            - 如果没有明确的下一步，可以不提供按钮（actions=[]）
            - 消息末尾会自动添加提示："💡 这些是建议的下一步，你也可以直接发送其他指令"
            - 简单确认或自动进行的过程不需要按钮
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
                        "description": "详细信息（可选，建议填写）"
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
        Tool(
            name="telegram_wait_reply",
            description="""
            等待用户回复（阻塞式轮询）

            参数：
            - max_wait: 最长等待时间（秒），默认604800（7天/1周）

            行为：
            - 前10分钟：每30秒检查一次
            - 10分钟-1小时：每60秒检查一次
            - 1小时以上：每120秒检查一次
            - 用户可以按 Ctrl+C 中断等待
            - 超时返回 timeout: true

            返回：
            - reply: 用户回复内容
            - timeout: 是否超时
            - interrupted: 是否被用户中断
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "max_wait": {
                        "type": "integer",
                        "description": "最长等待时间（秒），默认604800（7天）",
                        "default": 604800
                    }
                }
            }
        ),
        Tool(
            name="telegram_send",
            description="""
            发送自由格式消息到 Telegram（不推荐，请优先使用 telegram_notify）

            自动处理：
            - 超过300字自动截断
            - 会提示使用 telegram_notify 发送结构化消息
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "消息内容"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="telegram_send_code",
            description="""
            发送代码段到 Telegram（带语法高亮）

            ⚠️ 使用场景（仅在必要时使用）：
            - 遇到关键错误需要展示问题代码
            - 修复了重要 bug，需要展示修复方案
            - 用户明确要求查看某段代码
            - 需要用户 review 关键代码片段

            ❌ 不要使用的场景：
            - 一般性任务完成（使用 telegram_notify）
            - 创建了新文件（使用 telegram_send_file）
            - 例行操作（使用 telegram_notify 总结即可）

            参数：
            - code: 代码内容（建议不超过50行）
            - language: 编程语言（python/javascript/go/rust/bash/json/yaml等）
            - caption: 可选说明文字（建议填写，解释发送这段代码的原因）

            示例：
            telegram_send_code(
                code="def hello():\\n    print('Hello')",
                language="python",
                caption="修复了空指针异常的关键函数"
            )
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "代码内容"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言（python/javascript/go/rust/bash/json/yaml等）",
                        "default": ""
                    },
                    "caption": {
                        "type": "string",
                        "description": "可选说明文字"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="telegram_send_image",
            description="""
            发送图片到 Telegram

            ⚠️ 使用场景：
            - 生成了图表、可视化结果
            - 创建了截图、示意图
            - 需要用户查看图片内容
            - 图片格式：PNG, JPG, GIF, WebP 等

            参数：
            - image_path: 图片文件路径（相对于项目目录或绝对路径）
            - caption: 可选说明文字

            示例：
            telegram_send_image(
                image_path="output/chart.png",
                caption="性能测试结果图表"
            )
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "图片文件路径"
                    },
                    "caption": {
                        "type": "string",
                        "description": "可选说明文字"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="telegram_send_file",
            description="""
            发送文件到 Telegram

            ⚠️ 使用场景（仅在必要时使用）：
            - 用户明确要求查看某个文件："查看 config.json"、"发送 main.py 给我"
            - 创建了重要的输出文件需要用户确认（如配置文件、报告等）
            - 生成了图表、图片等需要展示的文件
            - 需要用户下载某个文件进行后续操作

            ❌ 不要使用的场景：
            - 创建普通代码文件（用 telegram_notify 总结即可）
            - 修改了文件但不需要用户查看内容
            - 例行的文件操作

            优先级：
            1. 优先使用 telegram_notify 总结文件变更
            2. 如果用户明确要求，或确实需要查看，才发送文件
            3. 对于代码文件，如果只需要展示关键片段，优先使用 telegram_send_code

            参数：
            - file_path: 文件路径（相对于项目目录或绝对路径）
            - caption: 可选说明文字

            支持：
            - 文本文件、代码文件
            - 图片、PDF、文档等任意文件类型
            - 自动处理大文件

            示例：
            telegram_send_file(
                file_path="src/main.py",
                caption="修复后的主文件（用户要求查看）"
            )
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "caption": {
                        "type": "string",
                        "description": "可选说明文字"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="telegram_get_context_info",
            description="""
            获取并发送当前会话的上下文信息到 Telegram

            ⚠️ 重要：调用此工具时，你应该：
            1. 检查系统提供的 token 使用量信息（<budget:token_budget> 标签）
            2. 将 token 使用情况包含在发送的信息中
            3. 发送完整的上下文信息（会话信息 + token 使用情况）

            返回信息应包括：
            - 会话 ID 和项目路径
            - Token 使用量（已使用 / 总量 / 剩余 / 使用率）
            - 会话运行时间
            - 系统信息
            - Telegram 配置

            示例输出格式：
            📊 会话上下文信息
            🆔 会话: testtg
            📁 项目: /path/to/project

            💾 Token 使用:
            - 已使用: 41,853 tokens
            - 总容量: 1,000,000 tokens
            - 剩余: 958,147 tokens
            - 使用率: 4.2%

            ⏱️ 运行时间: 15 分钟
            🖥️ 系统: Darwin 24.6.0
            🐍 Python: 3.14.0
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "token_used": {
                        "type": "integer",
                        "description": "已使用的 token 数量（从系统预算信息中获取）"
                    },
                    "token_total": {
                        "type": "integer",
                        "description": "总 token 容量（从系统预算信息中获取）",
                        "default": 1000000
                    }
                }
            }
        ),
        Tool(
            name="telegram_unattended_mode",
            description="""
            ⚠️ 这是 Telegram MCP Server 的无人值守模式工具
            用于等待用户通过 Telegram Bot 发送的下一步指令
            
            ❌ 这不是通用的 Telegram 操作工具
            ❌ 不用于发送 Telegram 消息（使用 telegram_notify 系列工具）
            ❌ 不用于管理 Telegram 群组或频道
            
            ✅ 正确用途：远程任务循环 - 等待用户通过 Telegram 发送指令

            工作流程：
            1. 执行当前任务
            2. 使用 telegram_notify_with_actions 发送结果（带智能按钮）
            3. 调用 telegram_unattended_mode 等待用户通过 Telegram 发送的下一步指令
            4. 收到指令后执行，重复循环
            
            示例场景：
            用户说："进入无人值守模式，任务：分析项目结构"
            
            你应该：
            1. 分析项目结构
            2. 调用 telegram_notify_with_actions 发送分析结果
            3. 调用 telegram_unattended_mode 等待下一步指令
            4. 用户在 Telegram 中发送"优化性能"
            5. 你收到指令，执行优化
            6. 重复步骤 2-5

            ⚠️ 重要：
            - 完成任务后必须调用通知工具发送结果
            - telegram_unattended_mode 本身不发送消息，只等待
            - 这样用户每次只收到任务结果，不会有重复的等待提示

            📋 推荐使用 telegram_notify_with_actions 发送结果：
            
            ⭐ 最佳实践（带智能按钮）：
            telegram_notify_with_actions(
                event="completed",
                summary="✅ 完成代码审查\\n- 发现 3 个可优化点\\n- 代码质量：B+",
                actions=[
                    {"text": "💡 优化这 3 处", "action": "自动优化发现的问题"},
                    {"text": "📊 查看详情", "action": "显示详细的优化建议"}
                ]
            )
            
            ✅ 简单通知（无按钮）：
            telegram_notify_with_actions(
                event="completed",
                summary="修复了 auth.py 的空指针异常，测试通过",
                actions=[]  # 不提供按钮
            )
            
            或使用基础版本：
            telegram_notify(
                event="completed",
                summary="创建了 3 个文件：main.py, utils.py, test.py"
            )

            ⚠️ 仅在必要时发送代码/文件：
            - 遇到无法自动修复的错误 → telegram_send_code 展示错误代码
            - 用户明确要求 → telegram_send_file 发送文件
            - 修复关键 bug → telegram_send_code 展示修复对比

            🎯 智能判断示例：
            - 任务完成 → telegram_notify_with_actions（带下一步建议按钮）
            - 遇到错误 → telegram_notify_with_actions（带修复方案按钮）
            - 需要决策 → telegram_notify_with_actions（带选项按钮）
            - 简单更新 → telegram_notify（无按钮）

            退出方式：
            - Telegram 发送 "退出" 或 "exit"
            - Claude Code 按 Ctrl+C 或 ESC

            轮询策略：
            - 前10分钟：每30秒检查一次
            - 10分钟-1小时：每60秒检查一次
            - 1小时以上：每120秒检查一次

            参数：
            - current_status: 当前任务状态的简短总结（1-2句话）
            - max_wait: 每次等待的最长时间（秒），默认604800（7天）
            - silent: 静默模式（不发送等待提示，默认 false）
              - 首次进入时使用 false（发送提示）
              - 后续循环使用 true（减少噪音）

            返回：
            - next_instruction: 用户的下一步指令
            - should_exit: 是否应该退出无人值守模式
            - interrupted: 是否被用户中断（Ctrl+C/ESC）
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "current_status": {
                        "type": "string",
                        "description": "当前任务状态描述"
                    },
                    "max_wait": {
                        "type": "integer",
                        "description": "最长等待时间（秒），默认604800（7天）",
                        "default": 604800
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        return [TextContent(type="text", text=f"配置错误: {str(e)}")]

    session_id = get_session_id()

    # Ensure session is registered (lazy registration)
    await ensure_session_registered(session_id)

    session = registry.get(session_id)

    if name == "telegram_notify":
        return await handle_telegram_notify(session, arguments)
    elif name == "telegram_notify_with_actions":
        return await handle_telegram_notify_with_actions(session, arguments)
    elif name == "telegram_wait_reply":
        return await handle_telegram_wait_reply(session, arguments)
    elif name == "telegram_send":
        return await handle_telegram_send(session, arguments)
    elif name == "telegram_send_code":
        return await handle_telegram_send_code(session, arguments)
    elif name == "telegram_send_image":
        return await handle_telegram_send_image(session, arguments)
    elif name == "telegram_send_file":
        return await handle_telegram_send_file(session, arguments)
    elif name == "telegram_get_context_info":
        return await handle_telegram_get_context_info(session, arguments)
    elif name == "telegram_unattended_mode":
        return await handle_telegram_unattended_mode(session, arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_telegram_notify(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_notify tool"""
    event = arguments.get("event")
    summary = arguments.get("summary", "")
    details = arguments.get("details", "")

    # Validate summary length
    if len(summary) > 200:
        return [TextContent(
            type="text",
            text="错误: summary 过长，请精炼到200字以内"
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

    # Update session
    session.last_message = summary
    session.update_activity()
    registry.update_session(session)  # Save to shared storage

    # Send to Telegram
    try:
        await send_telegram_message(session.chat_id, message)
        return [TextContent(
            type="text",
            text=f"✅ 已发送通知到 Telegram (会话: {session.session_id})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送失败: {str(e)}"
        )]


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
        import httpx
        import json
        import hashlib
        import time
        from pathlib import Path
        
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
            actions_file = Path.home() / ".telegram-mcp-actions.json"
            
            # Load existing actions
            existing_actions = {}
            if actions_file.exists():
                try:
                    with open(actions_file, 'r') as f:
                        existing_actions = json.load(f)
                except Exception:
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


async def handle_telegram_wait_reply(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_wait_reply tool"""
    max_wait = arguments.get("max_wait", config.TELEGRAM_MAX_WAIT)

    logger.info(f"Session {session.session_id} waiting for reply (max {max_wait}s)")

    # Mark session as waiting
    session.set_waiting()
    registry.update_session(session)  # Save to shared storage

    # Poll for messages
    start_time = time.time()

    try:
        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed >= max_wait:
                session.set_running()
                registry.update_session(session)  # Save to shared storage
                logger.info(f"Session {session.session_id} wait timeout")
                return [TextContent(
                    type="text",
                    text=f"超时: 等待了 {int(elapsed)} 秒未收到回复"
                )]

            # Check message queue
            if message_queue.has_messages(session.session_id):
                reply = message_queue.pop(session.session_id)
                session.set_running()
                registry.update_session(session)  # Save to shared storage
                logger.info(f"Session {session.session_id} received reply: {reply}")
                return [TextContent(
                    type="text",
                    text=f"用户回复: {reply}"
                )]

            # Progressive polling
            interval = get_poll_interval(elapsed)
            logger.debug(f"Session {session.session_id} polling (interval={interval}s, elapsed={int(elapsed)}s)")
            await asyncio.sleep(interval)
    except (KeyboardInterrupt, asyncio.CancelledError):
        session.set_running()
        registry.update_session(session)  # Save to shared storage
        logger.info(f"Session {session.session_id} wait interrupted by user")
        return [TextContent(
            type="text",
            text=f"⚠️ 等待被用户中断 (Ctrl+C)\n\n已等待: {int(time.time() - start_time)} 秒\n\n你可以继续正常对话。"
        )]


async def handle_telegram_send(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_send tool"""
    message = arguments.get("message", "")

    # Auto-truncate if too long
    if len(message) > 300:
        message = message[:280] + "\n\n... [消息过长已截断，建议使用 telegram_notify]"

    # Format message
    formatted = f"🤖 [`{session.session_id}`]\n{message}"

    # Update session
    session.last_message = message
    session.update_activity()
    registry.update_session(session)  # Save to shared storage

    # Send to Telegram
    try:
        await send_telegram_message(session.chat_id, formatted)
        return [TextContent(
            type="text",
            text=f"✅ 已发送消息到 Telegram (会话: {session.session_id})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送失败: {str(e)}"
        )]


async def handle_telegram_send_image(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_send_image tool"""
    image_path = arguments.get("image_path", "")
    caption = arguments.get("caption", "")

    if not image_path:
        return [TextContent(type="text", text="错误: image_path 参数不能为空")]

    # Resolve image path (relative to project or absolute)
    if not os.path.isabs(image_path):
        full_path = os.path.join(session.project_path, image_path)
    else:
        full_path = image_path

    # Check if file exists
    if not os.path.exists(full_path):
        return [TextContent(
            type="text",
            text=f"❌ 图片文件不存在: {image_path}"
        )]

    if not os.path.isfile(full_path):
        return [TextContent(
            type="text",
            text=f"❌ 不是文件（可能是目录）: {image_path}"
        )]

    # Build caption
    if not caption:
        caption = f"🖼️ [{session.session_id}] {image_path}"
    else:
        caption = f"🖼️ [{session.session_id}] {caption}"

    # Update session
    session.update_activity()

    # Send image to Telegram using HTTP API
    try:
        import httpx

        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"

        with open(full_path, 'rb') as f:
            files = {'photo': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {
                'chat_id': session.chat_id,
                'caption': caption
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, files=files, data=data, timeout=30.0)
                response.raise_for_status()

        return [TextContent(
            type="text",
            text=f"✅ 已发送图片到 Telegram (会话: {session.session_id}, 图片: {image_path})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送图片失败: {str(e)}"
        )]


async def handle_telegram_send_code(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_send_code tool"""
    code = arguments.get("code", "")
    language = arguments.get("language", "")
    caption = arguments.get("caption", "")

    if not code:
        return [TextContent(type="text", text="错误: code 参数不能为空")]

    # Build message
    if caption:
        message = f"📝 [`{session.session_id}`] {caption}\n\n"
    else:
        message = f"💻 [`{session.session_id}`] 代码段\n\n"

    # Add code block with syntax highlighting
    message += f"```{language}\n{code}\n```"

    # Update session
    session.update_activity()

    # Send to Telegram
    try:
        await send_telegram_message(session.chat_id, message)
        return [TextContent(
            type="text",
            text=f"✅ 已发送代码段到 Telegram (会话: {session.session_id}, 语言: {language or '未指定'})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送代码段失败: {str(e)}"
        )]


async def handle_telegram_get_context_info(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_get_context_info tool"""
    import platform
    from datetime import datetime

    token_used = arguments.get("token_used", 0)
    token_total = arguments.get("token_total", 1000000)

    # Gather context information
    info_parts = []

    info_parts.append("📊 会话上下文信息")
    info_parts.append("━━━━━━━━━━━━━━━━")
    info_parts.append(f"🆔 会话 ID: {session.session_id}")
    info_parts.append(f"📁 项目路径: {session.project_path}")
    info_parts.append(f"📂 当前目录: {os.getcwd()}")

    # Token usage (if provided)
    if token_used > 0:
        token_remaining = token_total - token_used
        usage_percent = (token_used / token_total) * 100

        info_parts.append("")
        info_parts.append("💾 Token 使用情况:")
        info_parts.append(f"- 已使用: {token_used:,} tokens")
        info_parts.append(f"- 总容量: {token_total:,} tokens")
        info_parts.append(f"- 剩余: {token_remaining:,} tokens")
        info_parts.append(f"- 使用率: {usage_percent:.1f}%")

    # Session timing
    created = datetime.fromisoformat(session.created_at)
    last_active = datetime.fromisoformat(session.last_active)
    uptime = (datetime.now() - created).total_seconds()

    info_parts.append("")
    info_parts.append("⏱️  会话时间:")
    info_parts.append(f"- 创建时间: {created.strftime('%Y-%m-%d %H:%M:%S')}")

    if uptime < 60:
        info_parts.append(f"- 运行时长: {int(uptime)} 秒")
    elif uptime < 3600:
        info_parts.append(f"- 运行时长: {int(uptime / 60)} 分钟")
    elif uptime < 86400:
        info_parts.append(f"- 运行时长: {int(uptime / 3600)} 小时")
    else:
        info_parts.append(f"- 运行时长: {int(uptime / 86400)} 天")

    # System info
    info_parts.append("")
    info_parts.append("🖥️  系统环境:")
    info_parts.append(f"- 操作系统: {platform.system()} {platform.release()}")
    info_parts.append(f"- Python: {platform.python_version()}")
    info_parts.append(f"- 状态: {session.status}")

    # Telegram config
    info_parts.append("")
    info_parts.append("📱 Telegram 配置:")
    info_parts.append(f"- 最长等待: {config.TELEGRAM_MAX_WAIT // 86400} 天")
    info_parts.append(f"- 轮询: {config.POLL_INTERVALS[0]}s → {config.POLL_INTERVALS[1]}s → {config.POLL_INTERVALS[2]}s")

    message = "\n".join(info_parts)

    # Update session
    session.update_activity()

    # Send to Telegram
    try:
        await send_telegram_message(session.chat_id, message)
        return [TextContent(
            type="text",
            text=f"✅ 上下文信息已发送到 Telegram (会话: {session.session_id})\n\n💡 提示：下次调用时传入 token_used 参数可显示 token 使用量"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送失败: {str(e)}"
        )]


async def handle_telegram_send_file(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_send_file tool"""
    file_path = arguments.get("file_path", "")
    caption = arguments.get("caption", "")

    if not file_path:
        return [TextContent(type="text", text="错误: file_path 参数不能为空")]

    # Resolve file path (relative to project or absolute)
    if not os.path.isabs(file_path):
        full_path = os.path.join(session.project_path, file_path)
    else:
        full_path = file_path

    # Check if file exists
    if not os.path.exists(full_path):
        return [TextContent(
            type="text",
            text=f"❌ 文件不存在: {file_path}"
        )]

    if not os.path.isfile(full_path):
        return [TextContent(
            type="text",
            text=f"❌ 不是文件（可能是目录）: {file_path}"
        )]

    # Build caption
    if not caption:
        caption = f"📄 [{session.session_id}] {file_path}"
    else:
        caption = f"📄 [{session.session_id}] {caption}"

    # Update session
    session.update_activity()

    # Send file to Telegram using HTTP API
    try:
        import httpx

        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument"

        with open(full_path, 'rb') as f:
            files = {'document': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {
                'chat_id': session.chat_id,
                'caption': caption
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, files=files, data=data, timeout=60.0)
                response.raise_for_status()

        return [TextContent(
            type="text",
            text=f"✅ 已发送文件到 Telegram (会话: {session.session_id}, 文件: {file_path})"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 发送文件失败: {str(e)}"
        )]


async def handle_telegram_unattended_mode(session, arguments: dict) -> list[TextContent]:
    """Handle telegram_unattended_mode tool"""
    current_status = arguments.get("current_status", "")
    max_wait = arguments.get("max_wait", config.TELEGRAM_MAX_WAIT)

    # Update session state
    session.last_message = current_status
    session.update_activity()
    session.set_waiting()
    registry.update_session(session)  # Save to shared storage

    # Silent waiting - no notification sent
    # User should call telegram_notify before calling this tool
    logger.info(f"Session {session.session_id} in unattended mode, waiting for instruction (silent)")

    start_time = time.time()

    try:
        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed >= max_wait:
                session.set_running()
                registry.update_session(session)  # Save to shared storage
                logger.info(f"Session {session.session_id} unattended mode timeout")
                return [TextContent(
                    type="text",
                    text=f"⏱️ 超时: 等待了 {int(elapsed)} 秒未收到指令\n\n建议：可以继续调用此工具重新进入等待，或者退出无人值守模式。"
                )]

            # Check message queue
            if message_queue.has_messages(session.session_id):
                reply = message_queue.pop(session.session_id)
                session.set_running()
                registry.update_session(session)  # Save to shared storage
                logger.info(f"Session {session.session_id} received instruction: {reply}")

                # Check if user wants to exit
                if reply.lower() in ['退出', 'exit', 'quit', '结束']:
                    return [TextContent(
                        type="text",
                        text=f"🚪 已退出无人值守模式\n\n用户指令: {reply}\n\n你可以继续正常对话，不再自动循环。"
                    )]

                # Return the instruction
                return [TextContent(
                    type="text",
                    text=f"📨 收到新指令: {reply}\n\n请执行此指令，完成后再次调用 telegram_unattended_mode 继续循环。"
                )]

            # Progressive polling
            interval = get_poll_interval(elapsed)
            logger.debug(f"Session {session.session_id} unattended mode polling (interval={interval}s, elapsed={int(elapsed)}s)")
            await asyncio.sleep(interval)
    except (KeyboardInterrupt, asyncio.CancelledError):
        session.set_running()
        registry.update_session(session)  # Save to shared storage
        logger.info(f"Session {session.session_id} unattended mode interrupted by user")
        return [TextContent(
            type="text",
            text=f"⚠️ 无人值守模式被用户中断 (Ctrl+C)\n\n已运行: {int(time.time() - start_time)} 秒\n\n已退出无人值守模式，你可以继续正常对话。"
        )]
