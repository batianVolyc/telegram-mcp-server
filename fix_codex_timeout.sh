#!/bin/bash
# Fix Codex timeout issue by adding tool_timeout_sec

echo "🔧 Fixing Codex Timeout Issue"
echo "=============================="
echo ""

CODEX_CONFIG="$HOME/.codex/config.toml"

# Check if config exists
if [ ! -f "$CODEX_CONFIG" ]; then
    echo "❌ Codex config not found: $CODEX_CONFIG"
    echo "Please run: telegram-mcp-server --setup"
    exit 1
fi

echo "📝 Current configuration:"
echo "------------------------"
grep -A 10 "\[mcp_servers.telegram\]" "$CODEX_CONFIG" || echo "telegram server not configured"
echo ""

# Check if tool_timeout_sec already exists
if grep -q "tool_timeout_sec" "$CODEX_CONFIG"; then
    echo "✅ tool_timeout_sec already configured"
    echo ""
    echo "Current value:"
    grep "tool_timeout_sec" "$CODEX_CONFIG"
    echo ""
    read -p "Update timeout value? (y/N): " update
    if [ "$update" != "y" ] && [ "$update" != "Y" ]; then
        echo "No changes made"
        exit 0
    fi
fi

# Ask for timeout value
echo "Choose timeout value:"
echo "  1. 3600 seconds (1 hour) - Good for quick tasks"
echo "  2. 86400 seconds (24 hours) - Good for overnight tasks"
echo "  3. 604800 seconds (7 days) - Full unattended mode (Recommended)"
echo "  4. Custom value"
echo ""
read -p "Enter choice [3]: " choice
choice=${choice:-3}

case $choice in
    1) timeout=3600 ;;
    2) timeout=86400 ;;
    3) timeout=604800 ;;
    4)
        read -p "Enter custom timeout (seconds): " timeout
        if ! [[ "$timeout" =~ ^[0-9]+$ ]]; then
            echo "❌ Invalid number"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice, using default (3600)"
        timeout=3600
        ;;
esac

echo ""
echo "Setting tool_timeout_sec = $timeout"

# Backup config
cp "$CODEX_CONFIG" "$CODEX_CONFIG.backup"
echo "✅ Backup created: $CODEX_CONFIG.backup"

# Add or update tool_timeout_sec
if grep -q "tool_timeout_sec" "$CODEX_CONFIG"; then
    # Update existing
    sed -i.tmp "s/tool_timeout_sec = [0-9]*/tool_timeout_sec = $timeout/" "$CODEX_CONFIG"
    rm -f "$CODEX_CONFIG.tmp"
    echo "✅ Updated tool_timeout_sec"
else
    # Add new line after [mcp_servers.telegram]
    sed -i.tmp "/\[mcp_servers.telegram\]/a\\
tool_timeout_sec = $timeout
" "$CODEX_CONFIG"
    rm -f "$CODEX_CONFIG.tmp"
    echo "✅ Added tool_timeout_sec"
fi

echo ""
echo "📝 New configuration:"
echo "--------------------"
grep -A 10 "\[mcp_servers.telegram\]" "$CODEX_CONFIG"

echo ""
echo "✅ Configuration updated!"
echo ""
echo "Next steps:"
echo "  1. Restart Codex (Ctrl+C then 'codex')"
echo "  2. Test: 进入无人值守模式，发送 hello"
echo "  3. Wait > 60 seconds - should not timeout"
echo ""
echo "Documentation: CODEX_TIMEOUT_FIX.md"
