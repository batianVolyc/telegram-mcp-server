#!/bin/bash
# Debug script for Gemini CLI issues

echo "🔍 Gemini CLI 诊断工具"
echo "=" * 50
echo ""

echo "1️⃣ 检查会话文件"
echo "-" * 50
SESSIONS_FILE="$HOME/.telegram-mcp-sessions.json"
if [ -f "$SESSIONS_FILE" ]; then
    echo "✅ 会话文件存在"
    echo "内容："
    cat "$SESSIONS_FILE" | python3 -m json.tool
else
    echo "❌ 会话文件不存在: $SESSIONS_FILE"
fi
echo ""

echo "2️⃣ 检查消息队列"
echo "-" * 50
QUEUE_FILE="$HOME/.telegram-mcp-queue.json"
if [ -f "$QUEUE_FILE" ]; then
    echo "✅ 队列文件存在"
    echo "内容："
    cat "$QUEUE_FILE" | python3 -m json.tool
else
    echo "❌ 队列文件不存在: $QUEUE_FILE"
fi
echo ""

echo "3️⃣ 检查按钮动作"
echo "-" * 50
ACTIONS_FILE="$HOME/.telegram-mcp-actions.json"
if [ -f "$ACTIONS_FILE" ]; then
    echo "✅ 动作文件存在"
    echo "内容："
    cat "$ACTIONS_FILE" | python3 -m json.tool
else
    echo "❌ 动作文件不存在: $ACTIONS_FILE"
fi
echo ""

echo "4️⃣ 检查日志"
echo "-" * 50
LOG_FILE="/tmp/telegram-mcp-server.log"
if [ -f "$LOG_FILE" ]; then
    echo "✅ 日志文件存在"
    echo "最后 20 行："
    tail -20 "$LOG_FILE"
else
    echo "❌ 日志文件不存在: $LOG_FILE"
fi
echo ""

echo "5️⃣ 检查 Gemini 配置"
echo "-" * 50
GEMINI_CONFIG="$HOME/.gemini/settings.json"
if [ -f "$GEMINI_CONFIG" ]; then
    echo "✅ Gemini 配置存在"
    echo "内容："
    cat "$GEMINI_CONFIG" | python3 -m json.tool
else
    echo "❌ Gemini 配置不存在: $GEMINI_CONFIG"
fi
echo ""

echo "6️⃣ 测试消息发送"
echo "-" * 50
echo "请在 Telegram 中运行以下命令："
echo ""
echo "  /sessions"
echo ""
echo "然后查看会话 ID 是否正确"
echo ""

echo "7️⃣ 手动测试消息队列"
echo "-" * 50
echo "运行以下命令测试："
echo ""
echo "python3 << 'EOF'"
echo "from pathlib import Path"
echo "import json"
echo ""
echo "# 读取会话"
echo "sessions_file = Path.home() / '.telegram-mcp-sessions.json'"
echo "if sessions_file.exists():"
echo "    with open(sessions_file) as f:"
echo "        sessions = json.load(f)"
echo "    print('会话列表:')"
echo "    for sid in sessions.keys():"
echo "        print(f'  - {sid}')"
echo "else:"
echo "    print('没有会话')"
echo ""
echo "# 添加测试消息"
echo "queue_file = Path.home() / '.telegram-mcp-queue.json'"
echo "queue = {}"
echo "if queue_file.exists():"
echo "    with open(queue_file) as f:"
echo "        queue = json.load(f)"
echo ""
echo "# 添加消息到第一个会话"
echo "if sessions:"
echo "    first_session = list(sessions.keys())[0]"
echo "    if first_session not in queue:"
echo "        queue[first_session] = []"
echo "    queue[first_session].append('测试消息')"
echo "    "
echo "    with open(queue_file, 'w') as f:"
echo "        json.dump(queue, f, indent=2)"
echo "    print(f'✅ 已添加测试消息到会话: {first_session}')"
echo "EOF"
echo ""

echo "=" * 50
echo "诊断完成！"
echo ""
echo "💡 常见问题："
echo "1. 会话 ID 不匹配 - 检查 /sessions 输出"
echo "2. Telegram Bot 未运行 - 检查日志文件"
echo "3. 消息队列为空 - 尝试 /to <session_id> 测试消息"
echo "4. 按钮动作文件不存在 - 重新发送带按钮的消息"
