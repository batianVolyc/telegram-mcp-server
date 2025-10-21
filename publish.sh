#!/bin/bash
# 发布脚本 - 自动化发布到 PyPI

set -e  # 遇到错误立即退出

echo "🚀 Telegram MCP Server - 发布脚本"
echo "=================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 获取当前版本
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 当前版本: $VERSION"
echo ""

# 询问发布类型
echo "选择发布目标："
echo "1) TestPyPI (测试)"
echo "2) PyPI (正式)"
echo "3) 两者都发布"
read -p "请选择 (1/2/3): " choice
echo ""

# 清理旧的构建
echo "🧹 清理旧的构建文件..."
rm -rf dist/ build/ *.egg-info telegram_mcp_server.egg-info
echo "✅ 清理完成"
echo ""

# 构建包
echo "🔨 构建包..."
python3 -m build
if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi
echo "✅ 构建完成"
echo ""

# 检查包
echo "🔍 检查包完整性..."
twine check dist/*
if [ $? -ne 0 ]; then
    echo "❌ 包检查失败"
    exit 1
fi
echo "✅ 包检查通过"
echo ""

# 显示构建的文件
echo "📦 构建的文件："
ls -lh dist/
echo ""

# 上传
case $choice in
    1)
        echo "📤 上传到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ 上传到 TestPyPI 完成！"
        echo "测试安装："
        echo "  pip install --index-url https://test.pypi.org/simple/ telegram-mcp-server"
        ;;
    2)
        read -p "⚠️  确认上传到正式 PyPI？(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "📤 上传到 PyPI..."
            twine upload dist/*
            echo ""
            echo "✅ 上传到 PyPI 完成！"
            echo "安装："
            echo "  pip install telegram-mcp-server"
            echo ""
            echo "查看："
            echo "  https://pypi.org/project/telegram-mcp-server/"
        else
            echo "❌ 取消上传"
            exit 1
        fi
        ;;
    3)
        echo "📤 上传到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ TestPyPI 上传完成"
        echo ""
        
        read -p "⚠️  确认上传到正式 PyPI？(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "📤 上传到 PyPI..."
            twine upload dist/*
            echo "✅ PyPI 上传完成"
        else
            echo "⚠️  跳过 PyPI 上传"
        fi
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 发布完成！"
echo ""
echo "下一步："
echo "1. 在 GitHub 创建 release: https://github.com/batianVolyc/telegram-mcp-server/releases/new"
echo "2. Tag: v$VERSION"
echo "3. 复制 CHANGELOG.md 中的内容作为 release notes"
