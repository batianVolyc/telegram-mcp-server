# 发布到 PyPI

## ✅ 构建完成

包已成功构建：
- `dist/telegram_mcp_server-0.2.0-py3-none-any.whl`
- `dist/telegram_mcp_server-0.2.0.tar.gz`

包检查通过：`twine check dist/*` ✅

---

## 📦 发布步骤

### 方法 1: 使用 PyPI API Token（推荐）

1. **获取 PyPI API Token**:
   - 访问 https://pypi.org/manage/account/token/
   - 创建新的 API token
   - 复制 token（格式：`pypi-...`）

2. **配置 token**:
   ```bash
   # 创建 ~/.pypirc 文件
   cat > ~/.pypirc << 'EOF'
   [pypi]
   username = __token__
   password = pypi-YOUR_TOKEN_HERE
   EOF
   
   chmod 600 ~/.pypirc
   ```

3. **上传到 PyPI**:
   ```bash
   cd telegram-mcp-server
   twine upload dist/*
   ```

### 方法 2: 使用用户名密码

```bash
cd telegram-mcp-server
twine upload dist/* -u YOUR_USERNAME -p YOUR_PASSWORD
```

### 方法 3: 先上传到 TestPyPI 测试

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ telegram-mcp-server==0.2.0

# 如果测试通过，再上传到正式 PyPI
twine upload dist/*
```

---

## 🧪 发布后测试

```bash
# 安装新版本
pip install --upgrade telegram-mcp-server

# 或使用 uvx
uvx telegram-mcp-server --help

# 验证版本
python3 -c "import telegram_mcp_server; print(telegram_mcp_server.__version__)"
```

---

## 📋 发布检查清单

- [x] 版本号已更新到 0.2.0
- [x] CHANGELOG.md 已创建
- [x] 代码已提交到 Git
- [x] 包已构建成功
- [x] 包检查通过（twine check）
- [ ] 上传到 PyPI
- [ ] 创建 GitHub Release
- [ ] 更新文档链接

---

## 🚀 快速发布命令

如果你已经配置好 PyPI token：

```bash
cd telegram-mcp-server
twine upload dist/*
```

---

## 📝 发布后的工作

1. **创建 GitHub Release**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
   
   然后在 GitHub 上创建 Release，使用 CHANGELOG.md 的内容

2. **更新文档**:
   - 在 README.md 中添加新功能说明
   - 更新安装命令
   - 添加使用示例

3. **宣传**:
   - 在相关社区分享
   - 更新项目主页
   - 发布博客文章

---

## ⚠️ 注意事项

1. **版本号不可重复**：一旦发布到 PyPI，版本号不能再次使用
2. **无法删除**：PyPI 上的包可以 yank（标记为不推荐），但不能完全删除
3. **测试先行**：建议先上传到 TestPyPI 测试
4. **保护 token**：不要将 API token 提交到 Git

---

**准备好了吗？运行 `twine upload dist/*` 发布到 PyPI！** 🚀
