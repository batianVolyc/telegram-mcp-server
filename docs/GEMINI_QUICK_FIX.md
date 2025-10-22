# Gemini CLI 快速修复指南

## 🐛 问题：Telegram 无法发送消息给 Gemini

### 症状
1. ✅ Gemini 成功发送消息到 Telegram
2. ✅ Telegram 收到消息和按钮
3. ❌ 在 Telegram 发送消息，Gemini 没反应
4. ❌ 点击按钮没反应

---

## 🔍 诊断步骤

### 步骤 1: 运行诊断脚本

```bash
cd telegram-mcp-server
./debug_gemini.sh
```

这会检查：
- 会话文件
- 消息队列
- 按钮动作
- 日志文件
- Gemini 配置

### 步骤 2: 检查会话 ID

在 Telegram 中发送：
```
/sessions
```

**预期输出**：
```
📋 活跃会话：

1️⃣ ⏸️ `tt`
   📁 `/path/to/project`
   🕐 1分钟前
```

**关键**：确认会话 ID 是 `tt`（或你在 Gemini 中看到的 ID）

### 步骤 3: 测试消息发送

在 Telegram 中发送：
```
/to tt 测试消息
```

**预期输出**：
```
✅ 消息已发送到 `tt`

💬 测试消息
```

如果看到这个，说明消息队列工作正常。

### 步骤 4: 检查 Gemini 是否收到

在 Gemini 终端中，应该看到：
```
📨 收到新指令: 测试消息

请执行此指令，完成后再次调用 telegram_unattended_mode 继续循环。
```

---

## 🔧 常见问题和解决方案

### 问题 1: Telegram Bot 没有运行

**症状**：
- `/sessions` 没有响应
- 发送消息没有任何反应

**原因**：Telegram Bot 进程没有启动

**解决方案**：

Telegram Bot 应该在 Gemini 启动时自动启动。检查日志：

```bash
tail -f /tmp/telegram-mcp-server.log
```

应该看到：
```
Starting Telegram bot (first instance)...
Telegram bot started successfully
```

如果没有，可能是：
1. 配置错误 - 检查 `~/.gemini/settings.json`
2. Bot Token 无效 - 重新运行 setup
3. 端口被占用 - 重启系统

### 问题 2: 会话 ID 不匹配

**症状**：
- `/sessions` 显示的会话 ID 和 Gemini 中的不一致
- 发送消息到错误的会话

**解决方案**：

设置环境变量指定会话 ID：

```bash
# 方法 A: 在启动 Gemini 时设置
TELEGRAM_SESSION=my-project gemini --yolo

# 方法 B: 在配置文件中设置
# 编辑 ~/.gemini/settings.json
{
  "mcpServers": {
    "telegram": {
      "env": {
        "TELEGRAM_SESSION": "my-project",
        "TELEGRAM_BOT_TOKEN": "...",
        "TELEGRAM_CHAT_ID": "..."
      }
    }
  }
}
```

### 问题 3: 消息队列文件不存在

**症状**：
- 消息发送成功，但 Gemini 收不到
- `~/.telegram-mcp-queue.json` 不存在

**解决方案**：

手动创建队列文件：

```bash
python3 << 'EOF'
import json
from pathlib import Path

queue_file = Path.home() / ".telegram-mcp-queue.json"
queue_file.write_text(json.dumps({}, indent=2))
print(f"✅ 创建队列文件: {queue_file}")
EOF
```

### 问题 4: 按钮点击没反应

**症状**：
- 点击 "运行脚本"、"查看代码" 等按钮没反应
- 按钮变灰但没有任何输出

**原因**：按钮动作文件不存在或已过期

**解决方案**：

检查动作文件：

```bash
cat ~/.telegram-mcp-actions.json
```

如果文件不存在或为空，让 Gemini 重新发送带按钮的消息：

在 Gemini 中：
```
使用 telegram_notify_with_actions 重新发送一条带按钮的测试消息
```

### 问题 5: Gemini 超时

**症状**：
- Gemini 显示 "Anticipating User Input (esc to cancel, 4m 27s)"
- 然后超时退出

**原因**：Gemini 的 MCP 超时设置太短

**解决方案**：

运行修复脚本：

```bash
cd telegram-mcp-server
./fix_gemini_timeout.sh
```

或手动编辑 `~/.gemini/settings.json`：

```json
{
  "mcpServers": {
    "telegram": {
      "timeout": 604800000
    }
  }
}
```

**重要**：`timeout` 单位是毫秒，604800000 = 7天

---

## 🧪 完整测试流程

### 1. 清理旧数据

```bash
rm ~/.telegram-mcp-sessions.json
rm ~/.telegram-mcp-queue.json
rm ~/.telegram-mcp-actions.json
```

### 2. 重启 Gemini

```bash
# 停止 Gemini (Ctrl+C)

# 设置会话 ID 并启动
TELEGRAM_SESSION=test-session gemini --yolo
```

### 3. 在 Gemini 中测试

```
使用 telegram_notify_with_actions 发送一条测试消息，包含 2 个操作按钮
```

### 4. 在 Telegram 中验证

应该收到消息和按钮。

### 5. 测试消息发送

在 Telegram 中：
```
/sessions
```

确认会话 ID，然后：
```
/to test-session 你好
```

### 6. 在 Gemini 中确认

应该看到：
```
📨 收到新指令: 你好
```

### 7. 测试按钮

点击任意按钮，应该看到：
```
✅ 已执行操作

📤 发送到: `test-session`
💬 指令: ...
```

然后 Gemini 应该收到指令并执行。

---

## 💡 最佳实践

### 1. 始终设置会话 ID

```bash
# 推荐：使用项目名作为会话 ID
cd /path/to/my-project
TELEGRAM_SESSION=my-project gemini --yolo
```

### 2. 使用 /keep 锁定会话

在 Telegram 中：
```
/keep my-project
```

之后直接发送消息，无需 `/to`。

### 3. 监控日志

在另一个终端：
```bash
tail -f /tmp/telegram-mcp-server.log
```

实时查看消息流动。

### 4. 定期清理

```bash
# 清理过期的按钮动作（自动清理 1 小时前的）
python3 << 'EOF'
import json
import time
from pathlib import Path

actions_file = Path.home() / ".telegram-mcp-actions.json"
if actions_file.exists():
    with open(actions_file) as f:
        actions = json.load(f)
    
    current_time = time.time()
    cleaned = {
        k: v for k, v in actions.items()
        if current_time - v.get("timestamp", 0) < 3600
    }
    
    with open(actions_file, 'w') as f:
        json.dump(cleaned, f, indent=2)
    
    print(f"✅ 清理完成：保留 {len(cleaned)}/{len(actions)} 个动作")
EOF
```

---

## 🆘 仍然无法工作？

### 收集诊断信息

```bash
# 1. 运行诊断脚本
./debug_gemini.sh > gemini_debug.txt

# 2. 收集日志
tail -100 /tmp/telegram-mcp-server.log >> gemini_debug.txt

# 3. 收集配置
cat ~/.gemini/settings.json >> gemini_debug.txt

# 4. 在 Telegram 中运行
/sessions
/status tt  # 替换为你的会话 ID
```

### 提交 Issue

在 GitHub 提交 Issue，附上：
1. `gemini_debug.txt` 文件
2. Gemini 版本：`gemini --version`
3. 截图（Gemini 终端 + Telegram）
4. 详细的操作步骤

https://github.com/batianVolyc/telegram-mcp-server/issues

---

## 📞 快速联系

如果问题紧急，可以：
1. 在 GitHub Issue 中 @batianVolyc
2. 查看 README.md 中的联系方式

---

**记住**：大多数问题都是会话 ID 不匹配或 Telegram Bot 没有运行导致的！
