# MCP 工具使用指南

## 📋 工具概览

### 核心通知工具

| 工具 | 用途 | 推荐度 | 特点 |
|------|------|--------|------|
| `telegram_notify_with_actions` | ⭐ 智能通知（带按钮） | ⭐⭐⭐⭐⭐ | 提供下一步建议，用户体验最佳 |
| `telegram_notify` | 简单通知 | ⭐⭐⭐ | 快速通知，向后兼容 |
| `telegram_send_code` | 发送代码 | ⭐⭐ | 仅在必要时使用 |
| `telegram_send_file` | 发送文件 | ⭐⭐ | 用户明确要求时使用 |
| `telegram_send_image` | 发送图片 | ⭐⭐ | 图表、截图等 |

### 交互工具

| 工具 | 用途 | 推荐度 |
|------|------|--------|
| `telegram_unattended_mode` | 无人值守循环 | ⭐⭐⭐⭐⭐ |
| `telegram_wait_reply` | 等待单次回复 | ⭐⭐⭐ |

---

## ⭐ 推荐：telegram_notify_with_actions

### 为什么推荐？

1. **智能建议**：根据情况提供 2-4 个操作按钮
2. **用户友好**：一键执行，无需手动输入
3. **灵活性**：按钮是建议，用户可以忽略
4. **向后兼容**：不提供按钮时（`actions=[]`）等同于 `telegram_notify`

### 使用场景

#### 1. 任务完成 - 提供下一步建议

```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 完成用户认证模块\n- 实现登录/注册\n- JWT验证\n- 15个测试通过",
    details="修改文件：auth.py, user.py\n测试覆盖率：95%",
    actions=[
        {
            "text": "实现权限管理",
            "action": "继续实现权限管理模块，包括角色和权限分配",
            "emoji": "💡"
        },
        {
            "text": "优化性能",
            "action": "优化数据库查询性能，添加缓存层",
            "emoji": "⚡"
        }
    ]
)
```

**用户看到**：
```
✅ [project-a]
完成用户认证模块
- 实现登录/注册
- JWT验证
- 15个测试通过

━━━━━━━━━━━━
📝 详情:
修改文件：auth.py, user.py
测试覆盖率：95%

💡 这些是建议的下一步，你也可以直接发送其他指令

[按钮: 💡 实现权限管理] [按钮: ⚡ 优化性能]
```

#### 2. 遇到错误 - 提供解决方案

```python
telegram_notify_with_actions(
    event="error",
    summary="❌ 导入错误\nModuleNotFoundError: No module named 'jwt'",
    details="缺少 PyJWT 依赖包",
    actions=[
        {
            "text": "自动修复",
            "action": "运行 pip install PyJWT 并重试",
            "emoji": "🔧"
        },
        {
            "text": "添加到依赖",
            "action": "将 PyJWT 添加到 requirements.txt",
            "emoji": "📝"
        },
        {
            "text": "显示错误代码",
            "action": "显示出错位置的代码",
            "emoji": "🔍"
        }
    ]
)
```

#### 3. 需要决策 - 提供选项

```python
telegram_notify_with_actions(
    event="question",
    summary="❓ 数据库选择\n需要选择数据库方案",
    details="方案A：PostgreSQL - 功能强大\n方案B：SQLite - 简单轻量",
    actions=[
        {
            "text": "PostgreSQL（推荐）",
            "action": "使用 PostgreSQL，我会配置 docker-compose",
            "emoji": "1️⃣"
        },
        {
            "text": "SQLite",
            "action": "使用 SQLite，适合小型项目",
            "emoji": "2️⃣"
        }
    ]
)
```

#### 4. 简单通知 - 不提供按钮

```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 文件已保存\nconfig.json 已更新",
    actions=[]  # 不提供按钮
)
```

### 按钮设计原则

#### ✅ 好的按钮设计

1. **明确具体**
   - ✅ "💡 优化这 3 处性能瓶颈"
   - ❌ "优化"

2. **标记推荐**
   - ✅ "💡 使用 PostgreSQL（推荐）"
   - ✅ "⚡ 使用 SQLite"

3. **数量适中**
   - ✅ 2-3 个主要选项
   - ❌ 6-7 个选项

4. **使用 emoji**
   - 💡 = 推荐/建议
   - 🔧 = 修复/解决
   - 📊 = 查看/详情
   - ⚡ = 优化/性能
   - 🔍 = 查看/检查
   - 1️⃣2️⃣3️⃣ = 选项编号

5. **action 具体明确**
   - ✅ "运行 pip install PyJWT 并重新执行导入"
   - ❌ "修复"

---

## 📝 telegram_notify（基础版本）

### 何时使用？

- 简单的状态更新（不需要用户交互）
- 快速通知（无需提供下一步建议）
- 向后兼容旧代码

### 示例

```python
telegram_notify(
    event="completed",
    summary="修复了 auth.py:45 的空指针异常，所有测试通过"
)
```

### 💡 建议

如果可能，优先使用 `telegram_notify_with_actions`，即使不提供按钮：

```python
# 推荐
telegram_notify_with_actions(
    event="completed",
    summary="修复了 auth.py:45 的空指针异常，所有测试通过",
    actions=[]
)

# 而不是
telegram_notify(
    event="completed",
    summary="修复了 auth.py:45 的空指针异常，所有测试通过"
)
```

---

## 🔄 telegram_unattended_mode（无人值守）

### 工作流程

```
1. 执行任务
   ↓
2. 发送结果（使用 telegram_notify_with_actions）
   ↓
3. 调用 telegram_unattended_mode 等待
   ↓
4. 收到指令
   ↓
5. 执行指令，回到步骤 1
```

### 完整示例

```python
# 步骤 1: 执行任务
result = analyze_code()

# 步骤 2: 发送结果（带智能按钮）
telegram_notify_with_actions(
    event="completed",
    summary=f"✅ 代码分析完成\n- 发现 {result.issues} 个问题\n- 代码质量：{result.grade}",
    actions=[
        {"text": "💡 自动修复", "action": "自动修复发现的问题", "emoji": "💡"},
        {"text": "📊 查看详情", "action": "显示详细的分析报告", "emoji": "📊"}
    ]
)

# 步骤 3: 等待下一步指令
next_instruction = telegram_unattended_mode(
    current_status="代码分析完成，等待下一步指令"
)

# 步骤 4: 执行下一步指令
# AI 会根据 next_instruction 继续执行...
```

### 最佳实践

1. **总是先发送结果**
   ```python
   # ✅ 正确
   telegram_notify_with_actions(...)
   telegram_unattended_mode(...)
   
   # ❌ 错误
   telegram_unattended_mode(...)  # 用户不知道发生了什么
   ```

2. **使用智能按钮**
   ```python
   # ✅ 推荐
   telegram_notify_with_actions(
       event="completed",
       summary="任务完成",
       actions=[...]  # 提供下一步建议
   )
   
   # ⚠️ 可以，但不够好
   telegram_notify(
       event="completed",
       summary="任务完成"
   )
   ```

3. **静默等待**
   ```python
   # telegram_unattended_mode 本身不发送消息
   # 用户只看到任务结果，不会看到"等待中..."的提示
   ```

---

## 🎯 决策树：选择合适的工具

```
需要发送通知？
├─ 是 → 需要用户交互？
│  ├─ 是 → 有明确的下一步建议？
│  │  ├─ 是 → telegram_notify_with_actions（带按钮）⭐
│  │  └─ 否 → telegram_notify_with_actions（不带按钮）
│  └─ 否 → telegram_notify 或 telegram_notify_with_actions
│
├─ 需要发送代码？
│  └─ telegram_send_code（仅在必要时）
│
├─ 需要发送文件？
│  └─ telegram_send_file（用户明确要求时）
│
└─ 需要等待回复？
   ├─ 长期无人值守 → telegram_unattended_mode ⭐
   └─ 单次等待 → telegram_wait_reply
```

---

## 📊 使用统计建议

### 推荐比例

- **telegram_notify_with_actions**: 70%（主要工具）
- **telegram_notify**: 20%（简单通知）
- **telegram_send_code**: 5%（仅在必要时）
- **telegram_send_file**: 5%（用户要求时）

### 按钮使用建议

- **任务完成**: 80% 应该提供按钮
- **遇到错误**: 90% 应该提供按钮
- **需要决策**: 100% 应该提供按钮
- **简单更新**: 20% 提供按钮

---

## 🔗 相关文档

- **DYNAMIC_BUTTONS_EXAMPLES.md** - 更多按钮示例
- **BOT_IMPROVEMENTS.md** - 技术实现细节
- **README.md** - 项目主文档

---

**记住**：`telegram_notify_with_actions` 是增强版本，即使不提供按钮也可以使用！⭐
