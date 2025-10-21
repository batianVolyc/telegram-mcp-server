"""Main entry point for Telegram MCP Server"""
import sys
import os
import logging
import asyncio
from mcp.server.stdio import stdio_server

from . import config
from .server import server
from .bot import setup_bot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/telegram-mcp-server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)


async def run_telegram_bot():
    """Run Telegram bot asynchronously (only if not already running)"""
    try:
        config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Telegram bot will not start. MCP server will continue without Telegram integration.")
        return

    # Check if another bot instance is already running
    import socket
    lock_file = "/tmp/telegram-mcp-bot.lock"

    try:
        # Try to create lock file
        if os.path.exists(lock_file):
            # Check if the process is still running
            with open(lock_file, 'r') as f:
                old_pid = f.read().strip()

            # Check if process exists
            try:
                os.kill(int(old_pid), 0)  # Check if process exists
                logger.info(f"Telegram bot already running in another process (PID: {old_pid})")
                logger.info("This MCP server instance will use shared storage without starting bot")
                return
            except OSError:
                # Process doesn't exist, remove stale lock
                os.remove(lock_file)

        # Write our PID to lock file
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))

        logger.info("Starting Telegram bot (first instance)...")

        # Setup bot
        bot_app = setup_bot(config.TELEGRAM_BOT_TOKEN)

        # Set global telegram_bot reference
        from . import server as server_module
        server_module.telegram_bot = bot_app

        # Initialize and start bot
        try:
            async with bot_app:
                await bot_app.initialize()
                await bot_app.start()
                await bot_app.updater.start_polling(allowed_updates=None)
                # Keep bot running
                while True:
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Telegram bot error: {e}", exc_info=True)
        finally:
            # Remove lock file on exit
            if os.path.exists(lock_file):
                os.remove(lock_file)

    except Exception as e:
        logger.error(f"Bot startup error: {e}", exc_info=True)


async def main():
    """Main entry point"""
    logger.info("Starting Telegram MCP Server...")

    # Create task for Telegram bot
    bot_task = asyncio.create_task(run_telegram_bot())

    # Give bot time to start
    await asyncio.sleep(2)

    # Run MCP server (stdio)
    logger.info("Starting MCP stdio server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        # Cancel bot task on exit
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
