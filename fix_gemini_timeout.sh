#!/bin/bash
# Fix Gemini CLI timeout configuration

echo "🔧 Fixing Gemini CLI timeout configuration..."
echo ""

GEMINI_CONFIG="$HOME/.gemini/settings.json"

if [ ! -f "$GEMINI_CONFIG" ]; then
    echo "❌ Gemini config not found: $GEMINI_CONFIG"
    echo "Please run: uvx telegram-mcp-server@latest --setup"
    exit 1
fi

echo "📋 Current configuration:"
cat "$GEMINI_CONFIG"
echo ""

# Backup
cp "$GEMINI_CONFIG" "$GEMINI_CONFIG.backup"
echo "✅ Backup created: $GEMINI_CONFIG.backup"

# Update timeout using Python
python3 << 'EOF'
import json
from pathlib import Path

config_file = Path.home() / ".gemini" / "settings.json"

with open(config_file, 'r') as f:
    config = json.load(f)

# Update timeout
if "mcpServers" in config and "telegram" in config["mcpServers"]:
    config["mcpServers"]["telegram"]["timeout"] = 604800000
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Timeout updated to 604800000 ms (7 days)")
else:
    print("❌ Telegram MCP server not found in config")
    print("Please run: uvx telegram-mcp-server@latest --setup")
EOF

echo ""
echo "📋 Updated configuration:"
cat "$GEMINI_CONFIG"
echo ""
echo "✅ Done! Please restart Gemini CLI:"
echo "   gemini --yolo"
