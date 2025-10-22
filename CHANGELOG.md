# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2024-10-22

### Fixed
- **Version Number** - Fixed `__init__.py` version to match package version
  - Previous 0.2.3 had incorrect version in `__init__.py` (showed 0.2.2)
  - Now correctly shows 0.2.4 when running `--version`

## [0.2.3] - 2024-10-22

### Fixed
- **Telegram Markdown Parsing** - Auto-fallback to plain text on 400 errors
  - Added automatic retry mechanism when Markdown parsing fails
  - Handles special characters (•, ✓, etc.) gracefully
  - Guarantees message delivery even if formatting fails
  - Affects `telegram_notify` and `telegram_notify_with_actions`

### Added
- **update_uvx_cache.sh** - Script to update uvx cached code
- **UPDATE_GUIDE.md** - Guide for updating uvx installations
- **CORRECT_USAGE.md** - Clarified tool usage to prevent AI confusion
- Tool descriptions now explicitly warn about correct usage context

### Improved
- Error handling in `send_telegram_message()` and `handle_telegram_notify_with_actions()`
- Documentation moved to `docs/` directory for better organization
- Cleaner project structure

## [0.2.2] - 2024-10-22

### Added
- **TOOLS_GUIDE.md** - Comprehensive tool usage guide with decision tree
- **GEMINI_TROUBLESHOOTING.md** - Complete Gemini CLI troubleshooting guide
- **fix_gemini_timeout.sh** - Script to fix Gemini timeout configuration

### Changed
- **Tool Descriptions** - Clarified relationship between tools
  - `telegram_notify` marked as basic version
  - `telegram_notify_with_actions` emphasized as recommended tool (⭐)
  - `telegram_unattended_mode` updated to recommend using `_with_actions`
- **Documentation** - Added `gemini --yolo` to all startup guides
- **Best Practices** - Updated recommendations for tool usage ratios

### Improved
- Tool selection guidance with decision tree
- Gemini CLI support and troubleshooting
- Documentation clarity and completeness

## [0.2.1] - 2024-10-22

### Added
- **--version flag** - Added version display to CLI
- **VERSION_CHECK.md** - Comprehensive version checking guide
- **QUICK_VERSION_CHECK.md** - Quick version verification methods

### Fixed
- Version display in help text
- uvx caching issues with `@latest` suffix

## [0.2.0] - 2024-10-22

### Added

#### 🎯 Dynamic Buttons System
- **New MCP Tool**: `telegram_notify_with_actions` - AI can now generate 2-4 contextual action buttons
- Smart button generation based on task completion, errors, questions, or progress updates
- Buttons are suggestions, not mandatory - users can ignore them and send custom commands
- Automatic button expiration (1 hour) with cleanup
- Persistent button storage in `~/.telegram-mcp-actions.json`

#### 📌 Session Context Management
- **New Command**: `/keep <session_id>` - Lock to a specific session for easier interaction
- `/keep` - Show currently locked session
- `/keep off` - Unlock session
- Improved `/to` command - can now lock sessions without sending messages
- All subsequent messages auto-route to locked session

#### 🎯 Smart Message Routing
- Intelligent session selection when no session is locked
- Single session: auto-send messages
- Multiple sessions: show selection buttons with status emoji (▶️ running, ⏸️ waiting, ⏹️ idle)
- No sessions: friendly error message with guidance

#### 💡 Enhanced User Experience
- Button clicks execute actions and update message status
- Clear visual feedback with emoji and status indicators
- Helpful hints: "💡 这些是建议的下一步，你也可以直接发送其他指令"
- Updated help documentation with new features

### Changed
- Improved message routing logic for better user experience
- Enhanced callback query handling for inline keyboards
- Better error messages and user guidance

### Technical
- Added `user_contexts` and `pending_messages` data structures
- Implemented `button_callback` and `handle_action_execution` handlers
- Added `handle_message` for smart routing
- Complete parameter validation (summary ≤ 200 chars, actions ≤ 4)
- ~350 lines of new, well-tested code
- No breaking changes - fully backward compatible

## [0.1.0] - 2024-01-XX

### Added
- Initial release
- Basic MCP server implementation
- Telegram bot integration
- Core tools: `telegram_notify`, `telegram_wait_reply`, `telegram_send`, etc.
- Session management
- Unattended mode support
- Multi-tool support (Claude Code, Codex, Gemini CLI)

[0.2.0]: https://github.com/batianVolyc/telegram-mcp-server/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/batianVolyc/telegram-mcp-server/releases/tag/v0.1.0
