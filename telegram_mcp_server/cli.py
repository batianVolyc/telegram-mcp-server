#!/usr/bin/env python3
"""CLI for telegram-mcp-server setup and configuration"""
import os
import sys
import json
import asyncio
from pathlib import Path


def get_claude_config_path(scope="user"):
    """
    Get Claude Code MCP config path based on scope
    
    Args:
        scope: "user" (default), "project", or "local"
    
    Returns:
        Path to config file
    """
    if scope == "user":
        return Path.home() / ".claude.json"
    elif scope == "project":
        return Path.cwd() / ".mcp.json"
    elif scope == "local":
        return Path.cwd() / ".claude.json"
    else:
        raise ValueError(f"Invalid scope: {scope}")


def get_claude_settings_path():
    """Get Claude Code settings.json path (for environment variables)"""
    return Path.home() / ".claude" / "settings.json"


def update_claude_settings(env_vars):
    """
    Update Claude Code settings.json with environment variables
    Intelligently merges with existing env configuration
    
    Args:
        env_vars: Dictionary of environment variables to add/update
    """
    settings_path = get_claude_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing settings or create new
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    # Ensure env key exists
    if "env" not in settings:
        settings["env"] = {}
    
    # Merge new environment variables
    settings["env"].update(env_vars)
    
    # Save settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    return settings_path


def get_codex_config_path():
    """Get Codex config path"""
    return Path.home() / ".codex" / "config.toml"


def get_gemini_config_path(scope="user"):
    """
    Get Gemini CLI config path based on scope
    
    Args:
        scope: "user" (default) or "project"
    
    Returns:
        Path to config file
    """
    if scope == "user":
        return Path.home() / ".gemini" / "settings.json"
    elif scope == "project":
        return Path.cwd() / ".gemini" / "settings.json"
    else:
        raise ValueError(f"Invalid scope: {scope}")


def check_tool_installed(tool_name):
    """
    Check if a CLI tool is installed
    
    Args:
        tool_name: Name of the tool (claude, codex, gemini)
    
    Returns:
        bool: True if installed, False otherwise
    """
    import shutil
    return shutil.which(tool_name) is not None


async def interactive_setup():
    """Interactive setup wizard"""
    print("🤖 Telegram MCP Server - Setup Wizard")
    print("=" * 50)
    print()
    
    # Step 0: Detect installed tools and choose configuration
    print("Step 0: Detect and Choose Configuration")
    print("-" * 50)
    
    # Detect installed tools
    installed_tools = []
    if check_tool_installed("claude"):
        installed_tools.append("Claude Code")
    if check_tool_installed("codex"):
        installed_tools.append("Codex")
    if check_tool_installed("gemini"):
        installed_tools.append("Gemini CLI")
    
    if installed_tools:
        print(f"✅ Detected installed tools: {', '.join(installed_tools)}")
        print()
    
    print("Which AI coding assistant do you want to configure?")
    print("  1. Claude Code (Anthropic)")
    print("  2. Codex (OpenAI)")
    print("  3. Gemini CLI (Google)")
    print("  4. Multiple tools")
    print()
    
    client_choice = input("Enter choice [1]: ").strip() or "1"
    
    # Determine which tools to configure
    configure_claude = client_choice in ["1", "4"]
    configure_codex = client_choice in ["2", "4"]
    configure_gemini = client_choice in ["3", "4"]
    
    # Get scope for Claude Code
    claude_scope = None
    if configure_claude:
        print()
        print("Choose configuration scope for Claude Code:")
        print("  1. User scope (global, ~/.claude.json)")
        print("  2. Project scope (shared, .mcp.json in project root)")
        print("  3. Local scope (project-specific, .claude.json)")
        print()
        print("💡 Recommendation:")
        print("   - User scope: Personal use across all projects")
        print("   - Project scope: Team collaboration (checked into git)")
        print("   - Local scope: Project-specific, not shared")
        print()
        
        scope_choice = input("Enter choice [1]: ").strip() or "1"
        scope_map = {"1": "user", "2": "project", "3": "local"}
        claude_scope = scope_map.get(scope_choice, "user")
    
    # Get scope for Gemini CLI
    gemini_scope = None
    if configure_gemini:
        print()
        print("Choose configuration scope for Gemini CLI:")
        print("  1. User scope (global, ~/.gemini/settings.json)")
        print("  2. Project scope (.gemini/settings.json in project root)")
        print()
        
        scope_choice = input("Enter choice [1]: ").strip() or "1"
        scope_map = {"1": "user", "2": "project"}
        gemini_scope = scope_map.get(scope_choice, "user")
    
    if configure_codex:
        print()
        print("ℹ️  Note: Codex only supports global configuration (~/.codex/config.toml)")
        print("   All projects will share the same MCP configuration.")
    
    print()
    
    # Step 1: Bot Token
    print("Step 1: Telegram Bot Token")
    print("-" * 50)
    print("1. Open Telegram and search for @BotFather")
    print("2. Send: /newbot")
    print("3. Follow instructions to create your bot")
    print("4. Copy the Bot Token (format: 123456789:ABCdef...)")
    print()
    
    bot_token = input("Enter your Bot Token: ").strip()
    
    if not bot_token:
        print("❌ Bot Token is required")
        sys.exit(1)
    
    # Validate token format
    if ":" not in bot_token:
        print("⚠️  Warning: Token format looks incorrect (should contain ':')")
    
    # Step 2: Verify bot
    print()
    print("Step 2: Verifying bot...")
    print("-" * 50)
    
    try:
        from telegram import Bot
        bot = Bot(token=bot_token)
        bot_info = await bot.get_me()
        print(f"✅ Bot verified: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Failed to verify bot: {e}")
        print("Please check your Bot Token and try again")
        sys.exit(1)
    
    # Step 3: Chat ID
    print()
    print("Step 3: Get Chat ID")
    print("-" * 50)
    print("1. Open Telegram and search for your bot")
    print("2. Click START or send any message")
    print("3. Press Enter here to auto-detect your Chat ID")
    print()
    
    input("Press Enter after sending a message to your bot...")
    
    try:
        updates = await bot.get_updates()
        if updates:
            chat_id = str(updates[-1].message.chat.id)
            print(f"✅ Chat ID detected: {chat_id}")
        else:
            print("⚠️  No messages found. Please enter manually:")
            print("   Visit: https://api.telegram.org/bot{}/getUpdates".format(bot_token))
            print("   Find: \"chat\":{\"id\":123456789}")
            chat_id = input("Enter your Chat ID: ").strip()
    except Exception as e:
        print(f"⚠️  Auto-detection failed: {e}")
        print("Please enter manually:")
        chat_id = input("Enter your Chat ID: ").strip()
    
    if not chat_id:
        print("❌ Chat ID is required")
        sys.exit(1)
    
    # Step 4: Generate config
    print()
    print("Step 4: Generating configuration")
    print("-" * 50)
    
    # Detect installation method
    if os.path.exists(Path.home() / ".local" / "bin" / "uvx"):
        command = "uvx"
        args = ["telegram-mcp-server"]
    else:
        command = sys.executable
        args = ["-m", "telegram_mcp_server"]
    
    # Configure Claude Code
    if configure_claude:
        config_path = get_claude_config_path(claude_scope)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Ensure mcpServers key exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add telegram server config
        config["mcpServers"]["telegram"] = {
            "command": command,
            "args": args,
            "env": {
                "TELEGRAM_BOT_TOKEN": bot_token,
                "TELEGRAM_CHAT_ID": chat_id
            }
        }
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Claude Code MCP configuration saved to: {config_path}")
        
        # Update settings.json with MCP_TOOL_TIMEOUT for 7-day unattended mode
        settings_path = update_claude_settings({
            "MCP_TOOL_TIMEOUT": "604800000"  # 7 days in milliseconds
        })
        print(f"✅ Claude Code settings updated: {settings_path}")
        print("   - MCP_TOOL_TIMEOUT set to 7 days (604800000 ms)")
        
        if claude_scope == "project":
            print("💡 Remember to commit .mcp.json to version control for team sharing")
    
    # Configure Gemini CLI
    if configure_gemini:
        gemini_config_path = get_gemini_config_path(gemini_scope)
        
        # Only create if tool is installed or user confirms
        if not check_tool_installed("gemini"):
            print()
            print("⚠️  Gemini CLI not detected on your system")
            create_anyway = input("Create configuration anyway? (y/N): ").strip().lower()
            if create_anyway != 'y':
                print("⏭️  Skipping Gemini CLI configuration")
                configure_gemini = False
        
        if configure_gemini:
            gemini_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config or create new
            if gemini_config_path.exists():
                with open(gemini_config_path, 'r') as f:
                    gemini_config = json.load(f)
            else:
                gemini_config = {}
            
            # Ensure mcpServers key exists
            if "mcpServers" not in gemini_config:
                gemini_config["mcpServers"] = {}
            
            # Add telegram server config
            gemini_config["mcpServers"]["telegram"] = {
                "command": command,
                "args": args,
                "env": {
                    "TELEGRAM_BOT_TOKEN": bot_token,
                    "TELEGRAM_CHAT_ID": chat_id
                },
                "timeout": 604800000  # 7 days in milliseconds
            }
            
            # Save config
            with open(gemini_config_path, 'w') as f:
                json.dump(gemini_config, f, indent=2)
            
            print(f"✅ Gemini CLI configuration saved to: {gemini_config_path}")
            print("   - Timeout set to 7 days (604800000 ms)")
            
            if gemini_scope == "project":
                print("💡 Remember to commit .gemini/settings.json to version control for team sharing")
    
    # Configure Codex
    if configure_codex:
        try:
            import toml
        except ImportError:
            print("⚠️  Installing toml package for Codex configuration...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "toml"])
            import toml
        
        codex_config_path = get_codex_config_path()
        codex_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new
        if codex_config_path.exists():
            with open(codex_config_path, 'r') as f:
                codex_config = toml.load(f)
        else:
            codex_config = {}
        
        # Ensure mcp_servers section exists
        if "mcp_servers" not in codex_config:
            codex_config["mcp_servers"] = {}
        
        # Add telegram server config
        codex_config["mcp_servers"]["telegram"] = {
            "command": command,
            "args": args,
            "tool_timeout_sec": 604800,  # 7 days for unattended mode
            "env": {
                "TELEGRAM_BOT_TOKEN": bot_token,
                "TELEGRAM_CHAT_ID": chat_id
            }
        }
        
        # Save config
        with open(codex_config_path, 'w') as f:
            toml.dump(codex_config, f)
        
        print(f"✅ Codex configuration saved to: {codex_config_path}")
    
    # Step 5: Test connection
    print()
    print("Step 5: Testing connection")
    print("-" * 50)
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text="✅ Telegram MCP Server configured successfully!\n\n"
                 "You can now start using Claude Code with Telegram integration."
        )
        print("✅ Test message sent to Telegram")
    except Exception as e:
        print(f"⚠️  Failed to send test message: {e}")
    
    # Done
    print()
    print("=" * 50)
    print("🎉 Setup complete!")
    print()
    print("Next steps:")
    print("  1. Start your AI assistant:")
    
    if configure_claude:
        print("     - Claude Code: claude --permission-mode bypassPermissions")
    
    if configure_codex:
        print("     - Codex: codex --dangerously-bypass-approvals-and-sandbox")
    
    if configure_gemini:
        print("     - Gemini CLI: gemini")
    
    print()
    print("  2. Check MCP connection: /mcp")
    print("  3. Test: Use telegram_notify to send a message")
    print()
    print("  In Telegram:")
    print("    - Send: /help")
    print("    - Try: 'Enter unattended mode. Task: analyze project'")
    print()
    
    # Show mcp add commands for other tools
    print()
    print("=" * 50)
    print("📋 Or add to other tools using mcp add commands:")
    print()
    
    if not configure_claude:
        print("Claude Code:")
        print(f"  claude mcp add \\")
        print(f"    --transport stdio \\")
        print(f"    telegram \\")
        print(f"    --env TELEGRAM_BOT_TOKEN={bot_token} \\")
        print(f"    --env TELEGRAM_CHAT_ID={chat_id} \\")
        print(f"    -- \\")
        print(f"    uvx telegram-mcp-server")
        print()
    
    if not configure_codex:
        print("Codex:")
        print(f"  codex mcp add telegram \\")
        print(f"    --env TELEGRAM_BOT_TOKEN={bot_token} \\")
        print(f"    --env TELEGRAM_CHAT_ID={chat_id} \\")
        print(f"    -- \\")
        print(f"    npx -y telegram-mcp-server")
        print()
    
    if not configure_gemini:
        print("Gemini CLI:")
        print(f"  gemini mcp add telegram uvx telegram-mcp-server \\")
        print(f"    -e TELEGRAM_BOT_TOKEN={bot_token} \\")
        print(f"    -e TELEGRAM_CHAT_ID={chat_id}")
        print()
    
    print("Documentation: https://github.com/batianVolyc/telegram-mcp-server")


def show_config():
    """Show current configuration"""
    config_path = get_claude_config_path()
    
    if not config_path.exists():
        print("❌ No configuration found")
        print(f"Expected location: {config_path}")
        print()
        print("Run: telegram-mcp-server --setup")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if "telegram" not in config.get("mcpServers", {}):
        print("❌ Telegram MCP Server not configured")
        print()
        print("Run: telegram-mcp-server --setup")
        return
    
    telegram_config = config["mcpServers"]["telegram"]
    
    print("📋 Current Configuration")
    print("=" * 50)
    print(f"Config file: {config_path}")
    print()
    print(f"Command: {telegram_config.get('command')}")
    print(f"Args: {telegram_config.get('args')}")
    print()
    
    env = telegram_config.get("env", {})
    bot_token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")
    
    if bot_token:
        print(f"Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    else:
        print("Bot Token: ❌ Not set")
    
    if chat_id:
        print(f"Chat ID: {chat_id}")
    else:
        print("Chat ID: ❌ Not set")
    
    print()
    print("=" * 50)


def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ["--version", "-v", "version"]:
            from . import __version__
            print(f"telegram-mcp-server version {__version__}")
            print("https://github.com/batianVolyc/telegram-mcp-server")
        elif arg in ["--setup", "-s", "setup"]:
            asyncio.run(interactive_setup())
        elif arg in ["--config", "-c", "config"]:
            show_config()
        elif arg in ["--help", "-h", "help"]:
            print("Telegram MCP Server - CLI")
            print()
            print("Usage:")
            print("  telegram-mcp-server              Run MCP server")
            print("  telegram-mcp-server --version    Show version")
            print("  telegram-mcp-server --setup      Interactive setup wizard")
            print("  telegram-mcp-server --config     Show current configuration")
            print("  telegram-mcp-server --help       Show this help")
            print()
            print("Documentation: https://github.com/batianVolyc/telegram-mcp-server")
        else:
            print(f"Unknown option: {arg}")
            print("Run: telegram-mcp-server --help")
            sys.exit(1)
    else:
        # Run MCP server
        from . import __main__
        asyncio.run(__main__.main())


if __name__ == "__main__":
    main()
