#!/bin/bash
# Restart Telegram Bot

echo "🔄 重启 Telegram Bot"
echo "=" * 50
echo ""

# 1. 查找并停止旧的 Bot 进程
echo "1️⃣ 停止旧的 Bot 进程"
LOCK_FILE="/tmp/telegram-mcp-bot.lock"

if [ -f "$LOCK_FILE" ]; then
    OLD_PID=$(cat "$LOCK_FILE")
    echo "找到锁文件，PID: $OLD_PID"
    
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "停止进程 $OLD_PID..."
        kill "$OLD_PID" 2>/dev/null || kill -9 "$OLD_PID" 2>/dev/null
        sleep 2
        
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "❌ 无法停止进程，请手动停止"
            exit 1
        else
            echo "✅ 进程已停止"
        fi
    else
        echo "进程不存在，清理锁文件"
    fi
    
    rm -f "$LOCK_FILE"
    echo "✅ 锁文件已删除"
else
    echo "没有找到锁文件"
fi

echo ""

# 2. 清理队列（可选）
echo "2️⃣ 清理消息队列（可选）"
read -p "是否清理消息队列？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f ~/.claude/telegram-mcp-queue.json
    echo "✅ 队列已清理"
else
    echo "⏭️  保留现有队列"
fi

echo ""

# 3. 显示当前会话
echo "3️⃣ 当前会话列表"
if [ -f ~/.claude/telegram-mcp-sessions.json ]; then
    python3 << 'EOF'
import json
from pathlib import Path

sessions_file = Path.home() / ".claude" / "telegram-mcp-sessions.json"
with open(sessions_file) as f:
    sessions = json.load(f)

print("会话列表：")
for sid, session in sessions.items():
    status = session.get("status", "unknown")
    status_emoji = {"running": "▶️", "waiting": "⏸️", "idle": "⏹️"}.get(status, "❓")
    print(f"  {status_emoji} {sid}")
EOF
else
    echo "没有会话文件"
fi

echo ""

# 4. 提示重启
echo "4️⃣ 重启 AI 工具"
echo "请重启你的 AI 工具："
echo ""
echo "  Claude Code:"
echo "    claude --permission-mode bypassPermissions"
echo ""
echo "  Gemini CLI:"
echo "    gemini --yolo"
echo ""
echo "  Codex:"
echo "    codex --dangerously-bypass-approvals-and-sandbox"
echo ""

echo "=" * 50
echo "✅ Bot 已准备好重启"
echo ""
echo "💡 提示："
echo "  - 重启后，Bot 将使用最新的代码"
echo "  - 所有会话将保留"
echo "  - 消息队列将重新初始化"
