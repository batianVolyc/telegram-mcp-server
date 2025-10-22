# 完整实现计划 - 动态按钮和会话管理

## 🎯 目标

实现三大核心功能：
1. **动态按钮** - AI 根据情况生成智能建议
2. **会话上下文** - 保持会话锁定，简化交互
3. **智能选择** - 未指定会话时显示选择按钮

---

## 📋 文件修改清单

### 1. `telegram_mcp_server/server.py`
- [ ] 添加 `telegram_notify_with_actions` 工具
- [ ] 优化 `telegram_notify` 的提示词
- [ ] 添加处理函数 `handle_telegram_notify_with_actions`

### 2. `telegram_mcp_server/bot.py`
- [ ] 添加 `pending_messages` 存储
- [ ] 添加 `pending_actions` 存储
- [ ] 添加 `handle_message` 处理普通消息
- [ ] 添加 `button_callback` 处理按钮点击
- [ ] 添加 `/keep` 命令
- [ ] 改进 `/to` 命令
- [ ] 添加会话选择按钮逻辑

### 3. `telegram_mcp_server/message_queue.py`
- 无需修改（已有功能足够）

### 4. `telegram_mcp_server/session.py`
- 无需修改（已有功能足够）

---

## 🔧 实现细节

### Phase 1: 添加动态按钮支持

#### 1.1 在 server.py 添加新工具

```python
Tool(
    name="telegram_notify_with_actions",
    description="""[详细的提示词 - 见 BOT_IMPROVEMENTS.md]""",
    inputSchema={
        "type": "object",
        "properties": {
            "event": {...},
            "summary": {...},
            "details": {...},
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "action": {"type": "string"},
                        "emoji": {"type": "string"}
                    },
                    "required": ["text", "action"]
                },
                "maxItems": 4
            }
        },
        "required": ["event", "summary"]
    }
)
```

#### 1.2 添加处理函数

```python
async def handle_telegram_notify_with_actions(session, arguments: dict):
    # 1. 验证参数
    # 2. 格式化消息
    # 3. 创建按钮
    # 4. 存储 actions 到临时存储
    # 5. 发送到 Telegram
    pass
```

### Phase 2: 实现会话上下文管理

#### 2.1 添加用户数据存储

```python
# 在 bot.py 顶部
user_contexts = {}  # {user_id: {"active_session": session_id}}
pending_messages = {}  # {user_id: message_text}
pending_actions = {}  # {action_id: action_command}
```

#### 2.2 添加 /keep 命令

```python
async def cmd_keep(update, context):
    # 设置/取消活跃会话
    pass
```

#### 2.3 改进 /to 命令

```python
async def cmd_to(update, context):
    # 如果没有消息，设置为活跃会话
    # 如果有消息，发送并设置为活跃会话
    pass
```

### Phase 3: 实现智能会话选择

#### 3.1 添加消息处理器

```python
async def handle_message(update, context):
    # 1. 检查是否有活跃会话
    # 2. 如果有，直接发送
    # 3. 如果没有，显示会话选择按钮
    pass
```

#### 3.2 添加按钮回调

```python
async def button_callback(update, context):
    # 处理三种类型的按钮：
    # 1. send_to:session_id - 发送消息到会话
    # 2. execute:session_id:action_id - 执行动作
    # 3. cancel - 取消操作
    pass
```

---

## 🧪 测试计划

### 测试 1: 动态按钮
- [ ] AI 发送带按钮的通知
- [ ] 用户点击按钮
- [ ] 指令正确发送到会话

### 测试 2: 会话上下文
- [ ] `/keep session-a` 锁定会话
- [ ] 后续消息自动发送到 session-a
- [ ] `/keep off` 取消锁定

### 测试 3: 智能选择
- [ ] 用户发送消息但没指定会话
- [ ] 显示会话选择按钮
- [ ] 点击按钮后消息正确发送

### 测试 4: 边界情况
- [ ] 只有一个会话时自动发送
- [ ] 没有会话时提示错误
- [ ] 会话不存在时提示错误
- [ ] 按钮过期处理

---

## 📊 实现优先级

### P0 - 核心功能（必须）
1. ✅ 动态按钮工具
2. ✅ 按钮回调处理
3. ✅ 会话上下文管理

### P1 - 用户体验（重要）
1. ✅ 智能会话选择
2. ✅ /keep 命令
3. ✅ 改进 /to 命令

### P2 - 优化（可选）
1. ⏳ 按钮状态管理（已点击/过期）
2. ⏳ 操作历史记录
3. ⏳ 批量操作支持

---

## 🚀 开始实施

准备好了吗？让我们开始！
