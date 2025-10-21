# Installation Guide

## Quick Install (Recommended)

### Option 1: One-line install (macOS/Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/batianVolyc/telegram-mcp-server/main/install.sh | bash
```

### Option 2: Using uv (Recommended)

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install telegram-mcp-server
uv tool install telegram-mcp-server

# Run setup wizard
telegram-mcp-server --setup
```

### Option 3: Using pip

```bash
pip install telegram-mcp-server

# Run setup wizard
telegram-mcp-server --setup
```

---

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/batianVolyc/telegram-mcp-server.git
cd telegram-mcp-server
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Configure

**Interactive setup:**
```bash
telegram-mcp-server --setup
```

**Or manually edit `~/.claude/config.json`:**

```json
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
```

---

## Getting Telegram Credentials

### 1. Create Bot

1. Open Telegram, search for `@BotFather`
2. Send: `/newbot`
3. Follow instructions
4. Copy the **Bot Token** (format: `123456789:ABCdef...`)

### 2. Get Chat ID

**Method A: Auto-detect (easiest)**
```bash
telegram-mcp-server --setup
# Follow the wizard, it will auto-detect your Chat ID
```

**Method B: Manual**
1. Start your bot in Telegram (send any message)
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find: `"chat":{"id":123456789}`
4. Copy the number

---

## Verification

### Check Configuration

```bash
telegram-mcp-server --config
```

### Test Connection

```bash
# Start Claude Code
claude

# In Claude, ask:
> Use telegram_notify to send a test message
```

You should receive a message in Telegram!

---

## Troubleshooting

### "telegram-mcp-server: command not found"

**Solution 1: Add to PATH**
```bash
# For uv installation
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.zshrc or ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

**Solution 2: Use full path**
```bash
~/.local/bin/telegram-mcp-server --setup
```

### "TELEGRAM_BOT_TOKEN not set"

Run the setup wizard:
```bash
telegram-mcp-server --setup
```

Or manually check `~/.claude/config.json`

### "Failed to connect to Telegram"

1. Check your internet connection
2. Verify Bot Token is correct
3. Test manually:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

### Python version too old

Requires Python 3.10+

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt install python3.11
```

---

## Uninstallation

### If installed via uv:
```bash
uv tool uninstall telegram-mcp-server
```

### If installed via pip:
```bash
pip uninstall telegram-mcp-server
```

### Remove configuration:
```bash
# Edit ~/.claude/config.json and remove the "telegram" section
```

---

## Next Steps

- Read [Usage Guide](USAGE.md)
- See [Examples](examples/)
- Join [Discussions](https://github.com/batianVolyc/telegram-mcp-server/discussions)

---

## Need Help?

- 📖 [Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/batianVolyc/telegram-mcp-server/discussions)
- 🐛 [Report Issues](https://github.com/batianVolyc/telegram-mcp-server/issues)
