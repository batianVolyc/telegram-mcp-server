# Project Structure

```
telegram-mcp-server/
├── telegram_mcp_server/          # Main package
│   ├── __init__.py               # Package initialization
│   ├── __main__.py               # Entry point
│   ├── server.py                 # MCP server (8 tools)
│   ├── bot.py                    # Telegram bot (6 commands)
│   ├── cli.py                    # CLI tool (setup, config)
│   ├── config.py                 # Configuration management
│   ├── session.py                # Session management
│   └── message_queue.py          # Message queue
│
├── docs/                         # Documentation
│   ├── CONFIGURATION_GUIDE.md    # Configuration details
│   ├── TROUBLESHOOTING.md        # Common issues
│   ├── POLLING_MECHANISM.md      # Polling strategy
│   ├── HOW_MCP_WORKS.md          # MCP architecture
│   ├── CODEX_TIMEOUT_FIX.md      # Codex timeout fix
│   ├── CONTRIBUTING.md           # Contribution guide
│   ├── INSTALL.md                # Installation guide
│   └── PUBLISH.md                # Publishing guide
│
├── .gitignore                    # Git ignore rules
├── CHANGELOG.md                  # Version history
├── LICENSE                       # MIT License
├── MANIFEST.in                   # Package manifest
├── pyproject.toml                # Project configuration
├── README.md                     # Main documentation
├── requirements.txt              # Dependencies
│
└── Scripts (optional)
    ├── install.sh                # Installation script
    ├── quick_fix.sh              # Quick fix script
    └── fix_codex_timeout.sh      # Timeout fix script
```

## Core Components

### telegram_mcp_server/

**server.py** - MCP Server
- 8 MCP tools for AI assistant integration
- Handles notifications, replies, file operations

**bot.py** - Telegram Bot
- 6 commands: /sessions, /status, /to, /file, /delete, /help
- Background process management
- Multi-session support

**cli.py** - CLI Tool
- `--setup`: Interactive configuration wizard
- `--config`: Display current configuration
- `--help`: Show help

**config.py** - Configuration
- Manages Claude Code and Codex configs
- Auto-detects configuration scope
- Handles timeout settings

**session.py** - Session Management
- File-based session storage
- Thread-safe with file locks
- Session lifecycle management

**message_queue.py** - Message Queue
- File-based message queue
- Thread-safe operations
- Supports polling mechanism

## Documentation

All user-facing documentation is in `docs/`. The main `README.md` provides quick start guide.

## Scripts

Optional helper scripts for installation and troubleshooting. Users can install via pip without these.
