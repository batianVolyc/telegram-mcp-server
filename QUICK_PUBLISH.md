# 快速发布指南

## 🚀 三步发布

### 1️⃣ 发布前检查

```bash
./pre_release_check.sh
```

确保所有检查通过。

### 2️⃣ 发布到 PyPI

```bash
# 安装发布工具（首次）
pip install build twine

# 运行发布脚本
./publish.sh
```

选择：
- `1` - 先测试（TestPyPI）
- `2` - 直接正式发布
- `3` - 先测试再正式发布（推荐）

### 3️⃣ 发布到 GitHub

```bash
# 初始化仓库（首次）
git init
git add .
git commit -m "Initial commit: v0.1.0"

# 添加远程仓库（首次）
git remote add origin https://github.com/batianVolyc/telegram-mcp-server.git

# 推送代码
git push -u origin main

# 创建 tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

然后在 GitHub 网页创建 Release：
1. 访问 https://github.com/batianVolyc/telegram-mcp-server/releases/new
2. 选择 tag: `v0.1.0`
3. Title: `v0.1.0 - Initial Release`
4. 复制 CHANGELOG.md 的内容
5. 点击 "Publish release"

---

## ✅ 验证发布

### PyPI
```bash
pip install telegram-mcp-server
telegram-mcp-server --help
```

访问：https://pypi.org/project/telegram-mcp-server/

### GitHub
访问：https://github.com/batianVolyc/telegram-mcp-server

---

## 📝 后续版本

更新版本号：
```bash
# 编辑 pyproject.toml，修改 version = "0.1.1"
# 编辑 CHANGELOG.md，添加新版本

git add .
git commit -m "Bump version to 0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1

./publish.sh
```

---

详细说明请查看 [RELEASE_GUIDE.md](RELEASE_GUIDE.md)
