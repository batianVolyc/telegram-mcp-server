#!/bin/bash
# 更新 uvx 缓存中的代码

set -e

echo "🔍 查找 uvx 缓存目录..."

# 找到正在运行的 telegram-mcp-server 进程
PID=$(ps aux | grep "python -m telegram_mcp_server" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "❌ 没有找到运行中的 telegram-mcp-server 进程"
    echo "💡 请先启动 MCP 服务器（重启 Kiro 或 Claude Code）"
    exit 1
fi

echo "✅ 找到进程 PID: $PID"

# 获取进程的可执行文件路径
PYTHON_PATH=$(ps -p $PID -o command= | awk '{print $1}')
echo "📍 Python 路径: $PYTHON_PATH"

# 推导出 site-packages 路径
CACHE_DIR=$(dirname $(dirname $PYTHON_PATH))
SITE_PACKAGES="$CACHE_DIR/lib/python3.12/site-packages/telegram_mcp_server"

if [ ! -d "$SITE_PACKAGES" ]; then
    echo "❌ 找不到缓存目录: $SITE_PACKAGES"
    exit 1
fi

echo "📁 缓存目录: $SITE_PACKAGES"
echo ""

# 备份旧文件
echo "💾 备份旧文件..."
BACKUP_DIR="$SITE_PACKAGES.backup.$(date +%Y%m%d_%H%M%S)"
cp -r "$SITE_PACKAGES" "$BACKUP_DIR"
echo "✅ 备份到: $BACKUP_DIR"
echo ""

# 复制新文件
echo "📋 复制新文件..."
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$CURRENT_DIR/telegram_mcp_server"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 找不到源代码目录: $SOURCE_DIR"
    exit 1
fi

# 复制所有 Python 文件
for file in "$SOURCE_DIR"/*.py; do
    filename=$(basename "$file")
    echo "  📄 $filename"
    cp "$file" "$SITE_PACKAGES/"
done

echo ""
echo "✅ 更新完成！"
echo ""
echo "🔄 下一步："
echo "1. 杀掉旧进程: kill $PID"
echo "2. 重启 Kiro 或 Claude Code"
echo "3. 新代码将自动生效"
echo ""
echo "💡 如果出问题，可以恢复备份:"
echo "   rm -rf $SITE_PACKAGES"
echo "   mv $BACKUP_DIR $SITE_PACKAGES"
