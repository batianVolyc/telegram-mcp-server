# 发布指南 - GitHub & PyPI

## 📋 发布前检查清单

### 1. 代码准备
- [x] 删除所有测试和演示文件
- [x] 清理构建产物
- [x] 更新 .gitignore
- [ ] 确认所有代码可以正常运行
- [ ] 检查没有硬编码的敏感信息

### 2. 文档准备
- [ ] 更新 README.md（确认所有链接正确）
- [ ] 更新 CHANGELOG.md（设置发布日期）
- [ ] 检查所有文档中的 GitHub 链接

### 3. 版本信息
- [ ] 确认 pyproject.toml 中的版本号
- [ ] 确认作者信息和邮箱
- [ ] 确认依赖版本

---

## 🚀 发布步骤

### 第一步：发布到 GitHub

#### 1.1 初始化 Git 仓库（如果还没有）

```bash
cd telegram-mcp-server
git init
git add .
git commit -m "Initial commit: v0.1.0"
```

#### 1.2 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`telegram-mcp-server`
3. 描述：`Remote control AI coding assistants (Claude Code/Codex) via Telegram`
4. 选择 Public
5. **不要**勾选 "Add README" 或 "Add .gitignore"（我们已经有了）
6. 点击 "Create repository"

#### 1.3 推送代码到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/batianVolyc/telegram-mcp-server.git

# 推送代码
git branch -M main
git push -u origin main
```

#### 1.4 创建 Release

```bash
# 创建 tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

然后在 GitHub 网页上：
1. 进入仓库页面
2. 点击右侧 "Releases" → "Create a new release"
3. 选择 tag: `v0.1.0`
4. Release title: `v0.1.0 - Initial Release`
5. 描述：复制 CHANGELOG.md 中的内容
6. 点击 "Publish release"

---

### 第二步：发布到 PyPI

#### 2.1 安装发布工具

```bash
pip install build twine
```

#### 2.2 构建包

```bash
cd telegram-mcp-server

# 清理旧的构建
rm -rf dist/ build/ *.egg-info

# 构建
python -m build
```

这会生成：
- `dist/telegram_mcp_server-0.1.0.tar.gz` - 源码包
- `dist/telegram_mcp_server-0.1.0-py3-none-any.whl` - wheel 包

#### 2.3 检查包

```bash
# 检查包的完整性
twine check dist/*
```

应该看到：
```
Checking dist/telegram_mcp_server-0.1.0.tar.gz: PASSED
Checking dist/telegram_mcp_server-0.1.0-py3-none-any.whl: PASSED
```

#### 2.4 测试上传到 TestPyPI（可选但推荐）

```bash
# 注册 TestPyPI 账号（如果没有）
# https://test.pypi.org/account/register/

# 上传到 TestPyPI
twine upload --repository testpypi dist/*
```

输入 TestPyPI 的用户名和密码（或使用 API token）。

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ telegram-mcp-server
```

#### 2.5 正式上传到 PyPI

```bash
# 注册 PyPI 账号（如果没有）
# https://pypi.org/account/register/

# 上传到 PyPI
twine upload dist/*
```

输入 PyPI 的用户名和密码（或使用 API token）。

---

## 🔐 使用 API Token（推荐）

### PyPI API Token

1. 登录 https://pypi.org
2. 进入 Account settings → API tokens
3. 点击 "Add API token"
4. Scope: "Entire account" 或选择特定项目
5. 复制生成的 token（只显示一次！）

创建 `~/.pypirc`：
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...你的token...
```

### TestPyPI API Token

同样的步骤，在 https://test.pypi.org 创建。

添加到 `~/.pypirc`：
```ini
[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwI...你的token...
```

---

## ✅ 发布后验证

### 验证 GitHub

1. 访问 https://github.com/batianVolyc/telegram-mcp-server
2. 检查 README 显示正常
3. 检查 Release 页面有 v0.1.0
4. 检查所有链接可以点击

### 验证 PyPI

1. 访问 https://pypi.org/project/telegram-mcp-server/
2. 检查页面显示正常
3. 测试安装：
   ```bash
   pip install telegram-mcp-server
   telegram-mcp-server --help
   ```

---

## 📝 发布后的工作

### 1. 更新 README badges

在 README.md 顶部的 badges 会自动生效：
- PyPI 版本
- Python 版本
- License

### 2. 宣传

- 在 Twitter/X 发布
- 在相关社区分享（Reddit, Hacker News 等）
- 写一篇博客介绍

### 3. 监控

- 关注 GitHub Issues
- 关注 PyPI 下载量
- 收集用户反馈

---

## 🔄 后续版本发布

### 更新版本号

1. 更新 `pyproject.toml` 中的 `version`
2. 更新 `CHANGELOG.md`，添加新版本的变更
3. 提交代码
4. 创建新的 tag 和 release
5. 重新构建和上传到 PyPI

```bash
# 示例：发布 v0.1.1
vim pyproject.toml  # 改为 0.1.1
vim CHANGELOG.md    # 添加 [0.1.1] 部分

git add .
git commit -m "Bump version to 0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1

# 重新构建和上传
rm -rf dist/
python -m build
twine upload dist/*
```

---

## 🆘 常见问题

### Q: 上传失败 "File already exists"
A: PyPI 不允许重新上传相同版本。需要增加版本号。

### Q: 包名已被占用
A: 需要在 pyproject.toml 中改名，比如 `telegram-mcp-server-volcy`

### Q: 导入失败
A: 检查 `pyproject.toml` 中的 `packages` 配置是否正确

### Q: 依赖安装失败
A: 检查 `dependencies` 中的版本号是否正确

---

## 📞 需要帮助？

- GitHub Issues: https://github.com/batianVolyc/telegram-mcp-server/issues
- PyPI Help: https://pypi.org/help/

---

**祝发布顺利！** 🎉
