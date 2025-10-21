# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-21

### Added
- Remote control Claude Code via Telegram
- Multi-session management
- Unattended mode for autonomous operation
- File viewing via Telegram
- Smart polling with progressive intervals (30s → 60s → 120s)
- 8 MCP tools:
  - `telegram_notify` - Send structured notifications
  - `telegram_wait_reply` - Wait for user reply
  - `telegram_send` - Send free-form messages
  - `telegram_send_code` - Send code with syntax highlighting
  - `telegram_send_image` - Send images
  - `telegram_send_file` - Send files
  - `telegram_get_context_info` - Get session context
  - `telegram_unattended_mode` - Enter autonomous loop
- Telegram bot commands:
  - `/sessions` - List active sessions
  - `/status` - Check session status
  - `/to` - Send message to session
  - `/file` - View/download files
  - `/help` - Show help
- Comprehensive documentation
- Setup wizard with auto-detection
- Cross-platform support (macOS, Linux, Windows)

### Technical
- Python 3.10+ support
- MCP protocol integration
- Telegram Bot API integration
- File-based session storage with locking
- Message queue system
- Progressive polling strategy

[Unreleased]: https://github.com/batianVolyc/telegram-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/batianVolyc/telegram-mcp-server/releases/tag/v0.1.0
