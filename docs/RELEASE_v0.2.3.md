# Release v0.2.3 - Markdown Parsing Fix

**Release Date**: October 22, 2024

## 🎯 Overview

This release fixes a critical issue where Telegram's Markdown parser would reject messages containing certain special characters, causing 400 Bad Request errors. The fix includes an automatic fallback mechanism that ensures message delivery even when Markdown parsing fails.

## 🐛 Bug Fixes

### Telegram Markdown Parsing (Critical)

**Problem**: Messages with special characters (•, ✓, etc.) caused 400 errors
- AI-generated messages often contain bullet points and checkmarks
- Telegram's Markdown parser is sensitive to character combinations
- Messages would fail to send, breaking the user experience

**Solution**: Automatic fallback to plain text
- Try sending with Markdown first (preserves formatting)
- On 400 error, automatically retry without `parse_mode`
- Guarantees message delivery in all cases
- Transparent to both AI and users

**Affected Tools**:
- `telegram_notify`
- `telegram_notify_with_actions`

**Technical Details**:
```python
# Before: Would fail on special characters
payload = {"text": message, "parse_mode": "Markdown"}

# After: Auto-retry without parse_mode on 400 error
try:
    response = await client.post(url, json=payload)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        payload.pop("parse_mode", None)  # Retry as plain text
        response = await client.post(url, json=payload)
```

## 📚 Documentation

### New Documentation
- **UPDATE_GUIDE.md** - Guide for updating uvx cached installations
- **CORRECT_USAGE.md** - Clarified tool usage to prevent AI confusion
- **docs/MARKDOWN_FIX.md** - Technical details of the Markdown fix
- **docs/QUICK_ANSWER.md** - Quick reference for 400 error

### Improved Tool Descriptions
- Added explicit warnings about correct usage context
- Clarified that tools work with configured Telegram Bot only
- Emphasized these are not generic Telegram messaging tools

## 🛠️ Developer Tools

### New Scripts
- **update_uvx_cache.sh** - Automatically update uvx cached code
  - Finds running process
  - Locates cache directory
  - Backs up old files
  - Copies new files
  - Provides restart instructions

### Project Cleanup
- Moved documentation to `docs/` directory
- Removed test scripts and temporary files
- Cleaner project structure
- Better organization

## 📦 Installation

### New Installation
```bash
uvx telegram-mcp-server@latest
```

### Upgrade from Previous Version
```bash
# Clear uvx cache to get latest version
rm -rf ~/.cache/uv/archive-v0/*

# Restart your AI tool (Kiro/Claude Code)
# uvx will automatically download v0.2.3
```

### Development Installation
```bash
git clone https://github.com/batianVolyc/telegram-mcp-server.git
cd telegram-mcp-server
./update_uvx_cache.sh  # Update running instance
```

## 🔄 Migration Guide

### From v0.2.2 to v0.2.3

**No breaking changes!** This is a bug fix release.

**What you need to do**:
1. Clear uvx cache or wait for automatic update
2. Restart your AI tool
3. That's it!

**What's different**:
- Messages with special characters now work reliably
- No visible changes to functionality
- Same API, same tools, same behavior

## 🧪 Testing

### Verify the Fix

1. **Test with special characters**:
```
进入无人值守模式，任务：分析项目结构
```

2. **AI generates message with bullets**:
```
✅ 项目分析完成

核心功能:
• 模块 A - 处理用户认证
• 模块 B - 数据处理
✓ 所有测试通过
```

3. **Message should send successfully** (even if formatting is lost)

### Run Test Script
```bash
cd telegram-mcp-server
python3 test_markdown_fix.py  # If you have the dev version
```

## 📊 Statistics

- **Files Changed**: 23
- **Lines Added**: 258
- **Lines Removed**: 1,956
- **Commits**: 3
- **Documentation**: 9 new/updated files

## 🙏 Acknowledgments

Thanks to all users who reported the 400 error issue and helped test the fix!

## 🔗 Links

- **PyPI**: https://pypi.org/project/telegram-mcp-server/0.2.3/
- **GitHub**: https://github.com/batianVolyc/telegram-mcp-server/releases/tag/v0.2.3
- **Documentation**: https://github.com/batianVolyc/telegram-mcp-server#readme
- **Issues**: https://github.com/batianVolyc/telegram-mcp-server/issues

## 📝 Full Changelog

See [CHANGELOG.md](../CHANGELOG.md) for complete version history.

---

**Previous Release**: [v0.2.2](RELEASE_v0.2.2.md) - Tool descriptions and Gemini support  
**Next Release**: TBD
