# 动态按钮示例 - AI 智能建议

## 🎯 核心理念

按钮是**建议**，不是强制选择。AI 根据具体情况提供 2-4 个最相关的下一步选项，但用户可以：
- 点击按钮快速执行建议的操作
- 忽略按钮，直接发送自己的指令
- 随时切换到其他任务

---

## 📋 场景 1：任务完成 - 提供下一步方向

### 示例 1.1：功能开发完成

```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 完成用户认证模块\n- 实现登录/注册 API\n- JWT token 验证\n- 15个单元测试全部通过",
    details="修改文件：auth.py, user.py, test_auth.py\n新增 API：/login, /register, /refresh\n测试覆盖率：95%",
    actions=[
        {
            "text": "💡 实现权限管理",
            "action": "继续实现权限管理模块，包括角色定义、权限分配和权限检查",
            "emoji": "💡"
        },
        {
            "text": "📝 编写 API 文档",
            "action": "为认证 API 编写详细的文档，包括请求示例和响应格式",
            "emoji": "📝"
        }
    ]
)
```

**用户看到**：
```
✅ [project-a]
完成用户认证模块
- 实现登录/注册 API
- JWT token 验证
- 15个单元测试全部通过

━━━━━━━━━━━━
📝 详情:
修改文件：auth.py, user.py, test_auth.py
新增 API：/login, /register, /refresh
测试覆盖率：95%

💡 这些是建议的下一步，你也可以直接发送其他指令

[按钮: 💡 实现权限管理] [按钮: 📝 编写 API 文档]
```

### 示例 1.2：代码审查完成

```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 完成代码审查\n- 发现 3 个可优化点\n- 1 个潜在 bug\n- 代码质量评分：B+",
    details="可优化点：\n1. auth.py:45 - 可以使用缓存\n2. api.py:123 - 重复代码可提取\n3. db.py:67 - N+1 查询问题\n\n潜在 bug：\n- user.py:89 - 未处理空值情况",
    actions=[
        {
            "text": "💡 自动优化这 3 处",
            "action": "自动优化发现的 3 个可优化点，添加缓存、提取重复代码、修复 N+1 查询",
            "emoji": "💡"
        },
        {
            "text": "🐛 先修复 bug",
            "action": "先修复 user.py:89 的空值处理问题，然后再考虑优化",
            "emoji": "🐛"
        },
        {
            "text": "📊 查看详细分析",
            "action": "显示每个问题的详细代码和建议的修改方案",
            "emoji": "📊"
        }
    ]
)
```

---

## 📋 场景 2：遇到错误 - 提供解决方案

### 示例 2.1：依赖缺失

```python
telegram_notify_with_actions(
    event="error",
    summary="❌ 导入错误\n\n位置：auth.py:45\n错误：ModuleNotFoundError: No module named 'jwt'",
    details="缺少 PyJWT 依赖包\n\n这是实现 JWT token 验证必需的库",
    actions=[
        {
            "text": "🔧 自动安装并重试",
            "action": "运行 pip install PyJWT，然后重新执行导入和测试",
            "emoji": "🔧"
        },
        {
            "text": "📝 添加到 requirements.txt",
            "action": "将 PyJWT==2.8.0 添加到 requirements.txt，方便团队安装",
            "emoji": "📝"
        },
        {
            "text": "🔍 显示错误代码",
            "action": "显示 auth.py 第 40-50 行的代码，让我看看具体情况",
            "emoji": "🔍"
        }
    ]
)
```

### 示例 2.2：测试失败

```python
telegram_notify_with_actions(
    event="error",
    summary="❌ 测试失败\n\n失败：3/15 个测试\n位置：test_auth.py",
    details="失败的测试：\n1. test_login_invalid_password - 断言错误\n2. test_register_duplicate_email - 未抛出异常\n3. test_token_expired - 超时",
    actions=[
        {
            "text": "💡 分析并修复",
            "action": "分析这 3 个失败的测试，找出原因并修复代码",
            "emoji": "💡"
        },
        {
            "text": "🔍 显示失败详情",
            "action": "显示每个失败测试的完整错误信息和堆栈跟踪",
            "emoji": "🔍"
        },
        {
            "text": "⏭️ 先跳过继续",
            "action": "暂时跳过这些测试，继续实现其他功能，稍后再修复",
            "emoji": "⏭️"
        }
    ]
)
```

### 示例 2.3：语法错误

```python
telegram_notify_with_actions(
    event="error",
    summary="❌ 语法错误\n\n位置：api.py:156\n错误：SyntaxError: invalid syntax",
    details="可能原因：\n- 缺少括号或引号\n- 缩进错误\n- 关键字拼写错误",
    actions=[
        {
            "text": "🔧 自动修复",
            "action": "检查 api.py:156 附近的代码，自动修复语法错误",
            "emoji": "🔧"
        },
        {
            "text": "👀 显示问题代码",
            "action": "显示 api.py 第 150-160 行的代码，让我看看问题在哪",
            "emoji": "👀"
        }
    ]
)
```

---

## 📋 场景 3：需要决策 - 提供选项

### 示例 3.1：技术选型

```python
telegram_notify_with_actions(
    event="question",
    summary="❓ 数据库选择\n\n需要为项目选择数据库，发现 3 种可行方案",
    details="方案对比：\n\n1️⃣ PostgreSQL\n✅ 功能强大，支持复杂查询\n✅ 事务支持完善\n❌ 需要额外部署和维护\n\n2️⃣ SQLite\n✅ 零配置，开箱即用\n✅ 轻量级，适合小项目\n❌ 并发性能差\n\n3️⃣ MongoDB\n✅ Schema 灵活\n✅ 横向扩展容易\n❌ 不适合关系型数据",
    actions=[
        {
            "text": "1️⃣ PostgreSQL（推荐）",
            "action": "使用 PostgreSQL，我会配置 docker-compose 和数据库迁移",
            "emoji": "1️⃣"
        },
        {
            "text": "2️⃣ SQLite",
            "action": "使用 SQLite，适合快速开发和小型项目",
            "emoji": "2️⃣"
        },
        {
            "text": "3️⃣ MongoDB",
            "action": "使用 MongoDB，我会调整数据模型为文档型",
            "emoji": "3️⃣"
        }
    ]
)
```

### 示例 3.2：代码风格选择

```python
telegram_notify_with_actions(
    event="question",
    summary="❓ API 设计风格\n\n发现两种常见的 API 设计方式",
    details="选项：\n\n1️⃣ RESTful API\n- 标准化，易于理解\n- 适合 CRUD 操作\n- 示例：GET /users, POST /users\n\n2️⃣ GraphQL\n- 灵活查询，减少请求次数\n- 前端可以精确获取需要的数据\n- 学习曲线较陡",
    actions=[
        {
            "text": "1️⃣ RESTful（推荐）",
            "action": "使用 RESTful API，我会设计标准的 REST 端点",
            "emoji": "1️⃣"
        },
        {
            "text": "2️⃣ GraphQL",
            "action": "使用 GraphQL，我会配置 GraphQL schema 和 resolver",
            "emoji": "2️⃣"
        }
    ]
)
```

---

## 📋 场景 4：进度更新 - 提供控制选项

### 示例 4.1：长时间任务进行中

```python
telegram_notify_with_actions(
    event="progress",
    summary="⏳ 数据库迁移进行中\n\n进度：3/5 (60%)\n\n已完成：\n- ✅ 用户表\n- ✅ 认证表\n- ✅ 权限表\n\n进行中：\n- 🔄 订单表",
    details="预计剩余时间：10 分钟\n\n当前操作：创建索引和外键约束",
    actions=[
        {
            "text": "⏸️ 暂停等待",
            "action": "暂停当前迁移，等待进一步指示",
            "emoji": "⏸️"
        },
        {
            "text": "📊 查看详情",
            "action": "显示已完成表的详细结构和迁移日志",
            "emoji": "📊"
        }
    ]
)
```

### 示例 4.2：批量处理进度

```python
telegram_notify_with_actions(
    event="progress",
    summary="⏳ 重构进行中\n\n进度：45/100 文件 (45%)\n\n已处理：45 个文件\n发现问题：3 处\n自动修复：2 处",
    details="当前处理：src/api/\n\n发现的问题：\n1. 重复代码 - 已提取\n2. 未使用的导入 - 已删除\n3. 命名不规范 - 待确认",
    actions=[
        {
            "text": "✅ 继续处理",
            "action": "继续重构剩余文件，遇到问题时通知我",
            "emoji": "✅"
        },
        {
            "text": "⏸️ 暂停查看",
            "action": "暂停重构，让我先查看已发现的问题",
            "emoji": "⏸️"
        }
    ]
)
```

---

## 📋 场景 5：无需按钮的情况

### 示例 5.1：简单确认

```python
telegram_notify_with_actions(
    event="completed",
    summary="✅ 文件已保存\n\nconfig.json 已更新",
    # 不提供 actions，因为这是简单的确认，没有明显的下一步
)
```

### 示例 5.2：信息通知

```python
telegram_notify_with_actions(
    event="progress",
    summary="⏳ 正在安装依赖...\n\n这可能需要几分钟",
    # 不提供 actions，因为这是自动进行的过程
)
```

---

## 🎯 按钮设计原则总结

### ✅ 好的按钮设计

1. **明确具体**
   - ✅ "💡 优化这 3 处性能瓶颈"
   - ❌ "优化"

2. **提供上下文**
   - ✅ "🔧 自动安装 PyJWT 并重试"
   - ❌ "修复"

3. **标记推荐**
   - ✅ "💡 使用 PostgreSQL（推荐）"
   - ✅ "⚡ 使用 SQLite"

4. **数量适中**
   - ✅ 2-3 个主要选项
   - ❌ 6-7 个选项

5. **可选性**
   - ✅ 添加提示："💡 这些是建议的下一步，你也可以直接发送其他指令"
   - ❌ 强迫用户必须选择

### ❌ 避免的设计

1. **模糊不清**
   - ❌ "继续"
   - ❌ "下一步"
   - ❌ "处理"

2. **选项过多**
   - ❌ 提供 5-6 个按钮

3. **强制选择**
   - ❌ "请选择一个选项"
   - ❌ 不提供其他操作方式

4. **每次都加按钮**
   - ❌ 简单确认也加按钮
   - ❌ 自动进行的过程也加按钮

---

## 💡 AI 决策流程

```
1. 完成任务/遇到问题
   ↓
2. 分析当前情况
   - 有明确的下一步吗？
   - 需要用户决策吗？
   - 有多个可行方案吗？
   ↓
3. 如果有 2-4 个明确的选项
   → 使用 telegram_notify_with_actions
   → 提供动态按钮
   ↓
4. 如果没有明确选项
   → 使用 telegram_notify
   → 不提供按钮
   ↓
5. 添加提示
   → "💡 这些是建议的下一步，你也可以直接发送其他指令"
```

---

**让 AI 根据具体情况智能建议，而不是固定模板！** 🎯
