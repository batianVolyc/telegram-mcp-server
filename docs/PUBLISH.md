# Publishing to PyPI

## Prerequisites

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml`:
```toml
version = "0.1.0"  # Increment this
```

### 2. Build Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# Build
python -m build
```

This creates:
- `dist/telegram_mcp_server-0.1.0.tar.gz` (source)
- `dist/telegram_mcp_server-0.1.0-py3-none-any.whl` (wheel)

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ telegram-mcp-server
```

### 4. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Enter your PyPI credentials when prompted
```

### 5. Verify

```bash
# Install from PyPI
pip install telegram-mcp-server

# Or with uv
uv tool install telegram-mcp-server
```

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Then:
1. Create PyPI API token: https://pypi.org/manage/account/token/
2. Add to GitHub Secrets as `PYPI_API_TOKEN`
3. Create GitHub Release → Auto-publish to PyPI

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features (backward compatible)
- `1.0.0` - Stable release
- `2.0.0` - Breaking changes

## Checklist Before Publishing

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run tests: `pytest`
- [ ] Build package: `python -m build`
- [ ] Test locally: `pip install dist/*.whl`
- [ ] Test installation: `telegram-mcp-server --help`
- [ ] Update README.md if needed
- [ ] Commit and push changes
- [ ] Create GitHub Release
- [ ] Publish to PyPI: `twine upload dist/*`
- [ ] Verify on PyPI: https://pypi.org/project/telegram-mcp-server/
- [ ] Test installation: `pip install telegram-mcp-server`

## Post-Publishing

1. **Announce**:
   - GitHub Discussions
   - Reddit (r/Python, r/ClaudeAI)
   - Twitter/X
   - Dev.to

2. **Monitor**:
   - PyPI download stats
   - GitHub issues
   - User feedback

3. **Update Documentation**:
   - Add installation badge to README
   - Update version numbers in docs

## Troubleshooting

### "Invalid distribution filename"
- Check `pyproject.toml` format
- Ensure version follows PEP 440

### "Package already exists"
- You can't re-upload the same version
- Increment version number

### "Authentication failed"
- Check PyPI credentials
- Use API token instead of password

## Resources

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/
