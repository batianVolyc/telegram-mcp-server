# Contributing to Telegram MCP Server

Thank you for your interest in contributing! 🎉

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/batianVolyc/telegram-mcp-server.git
cd telegram-mcp-server
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest
```

## Development Workflow

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test your changes:
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black telegram_mcp_server/
   ruff check telegram_mcp_server/
   
   # Test CLI
   telegram-mcp-server --help
   ```

4. Commit with clear message:
   ```bash
   git commit -m "Add: description of your changes"
   ```

5. Push and create Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use type hints where possible
- Add docstrings to functions and classes

### Format Code

```bash
# Auto-format
black telegram_mcp_server/

# Check linting
ruff check telegram_mcp_server/
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_config.py
```

### Add New Tests

Create test files in `tests/` directory:

```python
# tests/test_feature.py
def test_my_feature():
    assert True
```

## Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update USAGE.md for user-facing changes
- Add examples if helpful

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass
- [ ] Code is formatted (black)
- [ ] No linting errors (ruff)
- [ ] Documentation updated
- [ ] Commit messages are clear

### PR Description

Include:
- What changes were made
- Why the changes were needed
- How to test the changes
- Screenshots (if UI changes)

### Example PR

```markdown
## Description
Add support for sending images via Telegram

## Changes
- Added `telegram_send_image` tool
- Updated bot.py to handle image uploads
- Added tests for image handling

## Testing
1. Run: telegram-mcp-server --setup
2. In Claude: "Send test.png to Telegram"
3. Verify image received in Telegram

## Screenshots
[Image of Telegram showing received image]
```

## Reporting Issues

### Bug Reports

Include:
- Python version
- OS (macOS/Linux/Windows)
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

- Open a [Discussion](https://github.com/batianVolyc/telegram-mcp-server/discussions)
- Ask in [Issues](https://github.com/batianVolyc/telegram-mcp-server/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙏
