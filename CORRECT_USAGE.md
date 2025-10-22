# ✅ 正确使用示例

## 🎯 重要说明

**Telegram MCP Server 不是通用的 Telegram 操作工具！**

这个 MCP 服务器的目的是：
- ✅ 让 AI 编程助手（Claude Code/Gemini/Codex）通过 Telegram 与用户远程交互
- ✅ AI 完成任务后，发送结果到用户的 Telegram
- ✅ 用户在 Telegram 中发送指令，AI 收到并执行
- ❌ 不是用来发送消息到任意 Telegram 用户/群组/频道

---

## ✅ 正确的使用方式

### 场景 1: 用户说"进入无人值守模式"

#### ❌ 错误理解
```
AI: 我需要知道发送到哪个聊天...
```

#### ✅ 正确理解
```
AI: 好的，我会：
1. 执行你的任务
2. 通过 Telegram 发送结果给你
3. 等待你在 Telegram 中发送下一步指令
4. 收到指令后继续执行

请告诉我要执行什么任务？
```

### 场景 2: 用户说"进入无人值守模式，任务：分析项目结构"

#### ✅ 正确的执行流程

```python
# 步骤 1: 执行任务
files = list_directory()
analysis = analyze_structure(files)

# 步骤 2: 发送结果到 Telegram（用户会在 Telegram 中收到）
telegram_notify_with_actions(
    event="completed",
    summary=f"✅ 项目结构分析完成\n- 发现 {len(files)} 个文件\n- 3 个主要模块",
    details=f"详细信息：\n{analysis}",
    actions=[
        {"text": "💡 优化结构", "action": "优化项目结构，提高可维护性", "emoji": "💡"},
        {"text": "📊 查看详情", "action": "显示每个模块的详细分析", "emoji": "📊"}
    ]
)

# 步骤 3: 等待用户在 Telegram 中发送下一步指令
result = telegram_unattended_mode(
    current_status="项目结构分析完成，等待下一步指令"
)

# 步骤 4: 收到指令，继续执行
# result 包含用户在 Telegram 中发送的指令
# 例如："优化性能" 或点击了按钮
```

---

## 📋 完整示例

### 示例 1: 代码审查任务

**用户在 Claude Code 中说**：
```
进入无人值守模式。任务：审查 src/ 目录下的所有 Python 文件，找出可优化的地方
```

**AI 应该这样做**：

```python
# 1. 执行审查
issues = review_code("src/")

# 2. 发送结果到 Telegram
telegram_notify_with_actions(
    event="completed",
    summary=f"✅ 代码审查完成\n- 检查了 {len(files)} 个文件\n- 发现 {len(issues)} 个可优化点",
    details=f"主要问题：\n{format_issues(issues)}",
    actions=[
        {"text": "💡 自动优化", "action": "自动优化所有发现的问题", "emoji": "💡"},
        {"text": "📊 查看详情", "action": "显示每个问题的详细说明", "emoji": "📊"},
        {"text": "⏭️ 跳过继续", "action": "跳过优化，继续其他任务", "emoji": "⏭️"}
    ]
)

# 3. 等待用户指令
next_instruction = telegram_unattended_mode(
    current_status="代码审查完成，等待下一步指令"
)

# 4. 执行用户指令
# next_instruction 可能是：
# - "自动优化所有发现的问题"（用户点击了按钮）
# - "先优化性能相关的"（用户直接发送的）
# - "退出"（用户想退出无人值守模式）
```

### 示例 2: 遇到错误

**AI 执行任务时遇到错误**：

```python
try:
    result = execute_task()
except ImportError as e:
    # 发送错误通知
    telegram_notify_with_actions(
        event="error",
        summary=f"❌ 导入错误\n{str(e)}",
        details="缺少依赖包",
        actions=[
            {"text": "🔧 自动修复", "action": "安装缺失的依赖并重试", "emoji": "🔧"},
            {"text": "📝 添加到依赖", "action": "将依赖添加到 requirements.txt", "emoji": "📝"},
            {"text": "🔍 显示错误", "action": "显示完整的错误堆栈", "emoji": "🔍"}
        ]
    )
    
    # 等待用户决定如何处理
    next_instruction = telegram_unattended_mode(
        current_status="遇到错误，等待处理方案"
    )
    
    # 根据用户指令处理...
```

---

## ❌ 常见误解

### 误解 1: "进入无人值守模式"是一个独立的操作

**错误**：
```
用户: 进入无人值守模式
AI: 好的，我已经进入无人值守模式了
```

**正确**：
```
用户: 进入无人值守模式
AI: 好的，请告诉我要执行什么任务？
    我会执行任务，然后通过 Telegram 发送结果给你，
    并等待你在 Telegram 中发送下一步指令。
```

### 误解 2: telegram_unattended_mode 用于发送消息

**错误**：
```python
# 想发送消息到 Telegram
telegram_unattended_mode(message="Hello")  # ❌ 错误！
```

**正确**：
```python
# 发送消息到 Telegram
telegram_notify_with_actions(
    event="completed",
    summary="Hello"
)

# 然后等待回复
telegram_unattended_mode()
```

### 误解 3: 这是通用的 Telegram Bot 工具

**错误**：
```
用户: 进入无人值守模式，发送消息到 @某个用户
AI: 好的，发送到哪个聊天？
```

**正确**：
```
AI: 抱歉，Telegram MCP Server 只能发送通知到你配置的 Telegram Bot。
    如果你想操作 Telegram，需要使用其他工具。
    
    我可以做的是：
    1. 执行编程任务
    2. 通过 Telegram 发送结果给你
    3. 等待你在 Telegram 中发送下一步指令
```

---

## 📖 正确的对话示例

### 示例 1: 完整的无人值守流程

**用户**：
```
进入无人值守模式。任务：分析项目结构并提供优化建议
```

**AI**：
```
好的，我会：
1. 分析项目结构
2. 通过 Telegram 发送分析结果给你
3. 等待你在 Telegram 中发送下一步指令

开始分析...
```

**AI 执行**：
```python
# 1. 分析项目
structure = analyze_project()

# 2. 发送结果
telegram_notify_with_actions(
    event="completed",
    summary="✅ 项目结构分析完成\n- 15 个 Python 文件\n- 3 个主要模块",
    actions=[
        {"text": "💡 优化结构", "action": "优化项目结构"},
        {"text": "📊 查看详情", "action": "显示详细分析"}
    ]
)

# 3. 等待指令
telegram_unattended_mode()
```

**用户在 Telegram 中**：
```
点击按钮：💡 优化结构
```

**AI 收到指令并继续**：
```python
# 收到指令："优化项目结构"
optimize_structure()

# 发送结果
telegram_notify_with_actions(
    event="completed",
    summary="✅ 结构优化完成\n- 重构了 5 个文件\n- 提高了可维护性"
)

# 继续等待
telegram_unattended_mode()
```

---

## 🎯 关键要点

1. **Telegram MCP Server 是双向通信工具**
   - AI → Telegram: 发送任务结果
   - Telegram → AI: 发送下一步指令

2. **不是通用的 Telegram 操作工具**
   - 不能发送消息到任意用户
   - 不能管理群组或频道
   - 只能与配置的 Bot 交互

3. **无人值守模式 = 任务循环**
   - 执行任务 → 发送结果 → 等待指令 → 执行指令 → 循环

4. **用户在 Telegram 中控制 AI**
   - 不是 AI 控制 Telegram
   - 是用户通过 Telegram 控制 AI

---

**记住**：这是一个让用户通过 Telegram 远程控制 AI 编程助手的工具，不是通用的 Telegram Bot 工具！
