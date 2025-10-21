#!/bin/bash
# 发布前检查脚本

echo "🔍 发布前检查"
echo "=============="
echo ""

ERRORS=0
WARNINGS=0

# 检查必需文件
echo "📁 检查必需文件..."
required_files=(
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "pyproject.toml"
    "requirements.txt"
    "telegram_mcp_server/__init__.py"
    "telegram_mcp_server/__main__.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - 缺失"
        ((ERRORS++))
    fi
done
echo ""

# 检查不应该存在的文件
echo "🚫 检查不应该存在的文件..."
unwanted_items=(
    "__pycache__"
    "*.egg-info"
    "venv"
    "demo"
    "test_*.py"
    "WORK_SESSION_RECORD.md"
    "UPDATES.md"
)

for item in "${unwanted_items[@]}"; do
    if ls $item 2>/dev/null | grep -q .; then
        echo "  ⚠️  $item - 应该删除"
        ((WARNINGS++))
    else
        echo "  ✅ $item - 不存在（正确）"
    fi
done
echo ""

# 检查版本号一致性
echo "🔢 检查版本号..."
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "  pyproject.toml: $VERSION"

if grep -q "\[$VERSION\]" CHANGELOG.md; then
    echo "  ✅ CHANGELOG.md 包含版本 $VERSION"
else
    echo "  ❌ CHANGELOG.md 缺少版本 $VERSION"
    ((ERRORS++))
fi
echo ""

# 检查 GitHub 链接
echo "🔗 检查 GitHub 链接..."
GITHUB_USER="batianVolyc"
GITHUB_REPO="telegram-mcp-server"

if grep -q "github.com/$GITHUB_USER/$GITHUB_REPO" pyproject.toml; then
    echo "  ✅ pyproject.toml 链接正确"
else
    echo "  ❌ pyproject.toml 链接错误"
    ((ERRORS++))
fi

if grep -q "github.com/$GITHUB_USER/$GITHUB_REPO" README.md; then
    echo "  ✅ README.md 链接正确"
else
    echo "  ❌ README.md 链接错误"
    ((ERRORS++))
fi
echo ""

# 检查敏感信息
echo "🔐 检查敏感信息..."
sensitive_patterns=(
    "TELEGRAM_BOT_TOKEN.*[0-9]"
    "TELEGRAM_CHAT_ID.*[0-9]"
    "password.*="
    "secret.*="
)

found_sensitive=0
for pattern in "${sensitive_patterns[@]}"; do
    if grep -r -i "$pattern" telegram_mcp_server/ 2>/dev/null | grep -v ".pyc" | grep -q .; then
        echo "  ⚠️  可能包含敏感信息: $pattern"
        ((WARNINGS++))
        found_sensitive=1
    fi
done

if [ $found_sensitive -eq 0 ]; then
    echo "  ✅ 未发现敏感信息"
fi
echo ""

# 检查依赖
echo "📦 检查依赖..."
if python -c "import mcp" 2>/dev/null; then
    echo "  ✅ mcp 已安装"
else
    echo "  ⚠️  mcp 未安装（发布时不影响）"
fi

if python -c "import telegram" 2>/dev/null; then
    echo "  ✅ python-telegram-bot 已安装"
else
    echo "  ⚠️  python-telegram-bot 未安装（发布时不影响）"
fi
echo ""

# 检查 Python 语法
echo "🐍 检查 Python 语法..."
syntax_errors=0
for file in telegram_mcp_server/*.py; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ✅ $file"
    else
        echo "  ⚠️  $file - 可能有语法问题（或缺少依赖）"
        ((WARNINGS++))
    fi
done
echo ""

# 总结
echo "📊 检查总结"
echo "=========="
echo "错误: $ERRORS"
echo "警告: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ 所有检查通过！可以发布。"
    echo ""
    echo "下一步："
    echo "1. 运行 ./publish.sh 发布到 PyPI"
    echo "2. 推送代码到 GitHub"
    echo "3. 在 GitHub 创建 release"
    exit 0
else
    echo "❌ 发现 $ERRORS 个错误，请修复后再发布。"
    exit 1
fi
