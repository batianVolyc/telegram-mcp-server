#!/bin/bash
# Quick fix script for Telegram MCP Server issues

echo "🔧 Telegram MCP Server - Quick Fix"
echo "=================================="
echo ""

# 1. Kill old processes
echo "1. Killing old processes..."
pkill -f telegram-mcp-server 2>/dev/null && echo "   ✅ Killed old processes" || echo "   ℹ️  No old processes"

# 2. Clean up files
echo "2. Cleaning up files..."
rm -f /tmp/telegram-mcp-bot.lock && echo "   ✅ Removed lock file"
rm -f ~/.claude/telegram-mcp-sessions.json && echo "   ✅ Removed sessions file"
rm -f ~/.claude/telegram-mcp-queue.json && echo "   ✅ Removed queue file"

# 3. Clear log
echo "3. Clearing log..."
echo "" > /tmp/telegram-mcp-server.log && echo "   ✅ Cleared log file"

# 4. Reinstall
echo "4. Reinstalling package..."
./venv/bin/pip install -e . --force-reinstall --no-deps > /dev/null 2>&1 && echo "   ✅ Package reinstalled"

echo ""
echo "✅ Quick fix complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Codex/Claude Code"
echo "  2. Check logs: tail -f /tmp/telegram-mcp-server.log"
echo "  3. Test in Telegram: /sessions"
