# 微信 AI 自动回复 - 设计方案

**日期**: 2026-06-01
**状态**: 已批准

---

## 目标

搭建一个微信 AI 自动回复系统，当指定联系人发来消息时，自动调用 Claude API 生成符合用户风格的回复并发送，全程无需手动操作。

---

## 用户需求

- **场景**: 私人社交（朋友、家人的日常聊天）
- **风格**: 接地气的真诚 + 带点自嘲的松弛感，情绪真实不装
- **范围**: 指定联系人列表（10个以内），只对这些联系人开启自动回复

---

## 技术方案

### 核心技术栈

| 组件 | 技术 |
|------|------|
| 消息监听 | wxauto |
| AI 回复生成 | Claude API (Sonnet 4.5) |
| 运行环境 | Windows + Python 3.9+ |

### 架构图

```
微信客户端 ←→ wxauto 监听 ←→ Claude API ←→ 自动发送回复
                              ↑
                        风格提示词
```

---

## 组件设计

### 1. config.py - 配置模块

**职责**: 集中管理所有配置项

**配置项**:
- `API_KEY`: Claude API Key
- `CONTACTS`: 指定联系人列表（好友名称列表）
- `STYLE_PROMPT`: 风格提示词
- `CHECK_INTERVAL`: 消息检查间隔（秒）

**接口**:
```python
def load_config() -> dict
def get_contacts() -> list[str]
def get_style_prompt() -> str
```

---

### 2. wechat_listener.py - 消息监听

**职责**: 监听微信消息，判断是否需要处理

**数据流**:
1. 每隔 N 秒检查微信新消息
2. 获取消息发送者名称
3. 判断是否在指定联系人列表中
4. 如果是，提取消息内容并传递给回复模块

**接口**:
```python
def start_listening(callback: callable)
# callback 接收 (sender, message) 参数
```

---

### 3. claude_replier.py - AI 回复生成

**职责**: 调用 Claude API 生成回复

**Prompt 设计**:
```
你是一个聊天高手，说话风格是：
- 接地气的真诚，带点自嘲的松弛感
- 会吐槽也会关心人，情绪真实不装
- 吐槽但不传递负面情绪，自带乐观松弛感
- 用细节和玩笑照顾对方情绪
- 安慰不空洞、不油腻
- 口语化、短句多，节奏轻快

现在有人对你说："{user_message}"
请用符合上述风格的方式回复。
```

**接口**:
```python
async def generate_reply(message: str, style: str) -> str
```

---

### 4. main.py - 主程序入口

**职责**: 协调各模块运行

**流程**:
1. 加载配置
2. 启动消息监听
3. 收到消息 → 调用 Claude API → 发送回复
4. 循环运行

---

## 数据流完整路径

```
1. wxauto 检测到新消息 (sender="张三", content="在干嘛")
2. 检查 sender 是否在 CONTACTS 列表中
3. 如果是，调用 claude_replier.generate_reply(content, STYLE_PROMPT)
4. Claude API 返回: "刚躺下追剧呢，你咋想起我了"
5. wxauto.SendMsg(回复内容, to="张三")
```

---

## 错误处理策略

| 错误场景 | 处理方式 |
|----------|----------|
| API 调用失败 | 记录日志，跳过本次回复 |
| 网络超时 | 重试1次，仍失败则放弃 |
| 微信未登录 | 打印错误提示，程序退出 |
| 消息发送失败 | 记录日志，不阻塞后续消息 |

---

## 文件结构

```
wechat-ai-reply/
├── config.py          # 配置模块
├── wechat_listener.py # 消息监听
├── claude_replier.py  # AI 回复生成
├── main.py            # 主入口
├── requirements.txt   # 依赖
└── README.md          # 使用说明
```

---

## 依赖项

```
wxauto>=3.9
anthropic>=0.18
```

---

## 待确认事项

- [x] 联系人列表（用户提供）
- [x] API Key（用户提供）
- [x] 风格提示词（已定义）
- [ ] 是否需要日志记录

---

## 后续步骤

1. 创建 `writing-plans` 实现计划
2. 安装依赖 wxauto + anthropic
3. 编写代码
4. 测试运行