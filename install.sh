#!/bin/bash
# One-click installation script for Telegram MCP Server
# Usage: curl -fsSL https://raw.githubusercontent.com/batianVolyc/telegram-mcp-server/main/install.sh | bash

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}🚀 Telegram MCP Server - One-Click Installer${NC}"
echo ""

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python 3 not found${NC}"
        echo "Please install Python 3.10 or higher from https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
    MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
        echo -e "${RED}❌ Python 3.10+ required, found: $PYTHON_VERSION${NC}"
        echo ""
        echo "Upgrade Python:"
        echo "  macOS:  brew install python@3.11"
        echo "  Ubuntu: sudo apt install python3.11"
        exit 1
    fi

    echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
}

# Check if uv is installed
check_uv() {
    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✅ uv installed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  uv not found${NC}"
        return 1
    fi
}

# Install via uv (recommended)
install_via_uv() {
    echo ""
    echo -e "${BOLD}📦 Installing via uv (recommended)...${NC}"
    
    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    echo "Installing telegram-mcp-server..."
    uv tool install telegram-mcp-server
    
    echo -e "${GREEN}✅ Installation complete!${NC}"
    INSTALL_METHOD="uv"
}

# Install via pip
install_via_pip() {
    echo ""
    echo -e "${BOLD}📦 Installing via pip...${NC}"
    
    $PYTHON_CMD -m pip install --user telegram-mcp-server
    
    echo -e "${GREEN}✅ Installation complete!${NC}"
    INSTALL_METHOD="pip"
}

# Configure Claude Code
configure_claude() {
    echo ""
    echo -e "${BOLD}⚙️  Configuration${NC}"
    echo ""
    
    # Check if config exists
    CLAUDE_CONFIG="$HOME/.claude/config.json"
    
    if [ ! -f "$CLAUDE_CONFIG" ]; then
        echo "Creating $CLAUDE_CONFIG..."
        mkdir -p "$HOME/.claude"
        echo '{"mcpServers": {}}' > "$CLAUDE_CONFIG"
    fi
    
    echo -e "${YELLOW}📝 You need to configure Telegram credentials:${NC}"
    echo ""
    echo "1. Create a Telegram bot:"
    echo "   - Open Telegram, search for @BotFather"
    echo "   - Send: /newbot"
    echo "   - Follow instructions to get your BOT_TOKEN"
    echo ""
    echo "2. Get your Chat ID:"
    echo "   - Start your bot in Telegram"
    echo "   - Send any message to it"
    echo "   - Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
    echo "   - Find \"chat\":{\"id\":123456789}"
    echo ""
    echo "3. Add to $CLAUDE_CONFIG:"
    echo ""
    
    if [ "$INSTALL_METHOD" = "uv" ]; then
        cat << 'EOF'
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp-server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_bot_token_here",
        "TELEGRAM_CHAT_ID": "your_chat_id_here"
      }
    }
  }
}
EOF
    else
        cat << EOF
{
  "mcpServers": {
    "telegram": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "telegram_mcp_server"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_bot_token_here",
        "TELEGRAM_CHAT_ID": "your_chat_id_here"
      }
    }
  }
}
EOF
    fi
    
    echo ""
    echo -e "${GREEN}💡 Tip: Run 'telegram-mcp-server --setup' for interactive configuration${NC}"
}

# Main installation flow
main() {
    check_python
    
    echo ""
    echo "Choose installation method:"
    echo "  1) uv (recommended, faster)"
    echo "  2) pip (traditional)"
    echo ""
    read -p "Enter choice [1]: " choice
    choice=${choice:-1}
    
    case $choice in
        1)
            install_via_uv
            ;;
        2)
            install_via_pip
            ;;
        *)
            echo "Invalid choice, using uv..."
            install_via_uv
            ;;
    esac
    
    configure_claude
    
    echo ""
    echo -e "${BOLD}${GREEN}🎉 Installation complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure Telegram credentials (see above)"
    echo "  2. Run: telegram-mcp-server --setup (optional, for guided setup)"
    echo "  3. Start Claude Code: claude"
    echo ""
    echo "Documentation: https://github.com/batianVolyc/telegram-mcp-server"
}

main
