# 微信 AI 自动回复 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建微信 AI 自动回复系统，对指定联系人发来的消息自动调用 Claude API 生成符合用户风格的回复并发送

**Architecture:** 使用 wxauto 监听微信消息，通过 anthropic SDK 调用 Claude API 生成回复，再由 wxauto 发送。分为 config、listener、replier 三个模块，职责清晰分离。

**Tech Stack:** Python 3.9+ | wxauto | anthropic SDK

---

## 文件结构

```
wechat-ai-reply/
├── config.py           # 配置模块 - API Key、联系人列表、风格提示词
├── wechat_listener.py  # 消息监听模块 - 监听微信消息、判断联系人
├── claude_replier.py   # AI 回复模块 - 调用 Claude API 生成回复
├── main.py             # 主入口 - 协调各模块运行
├── requirements.txt    # 依赖列表
└── README.md           # 使用说明
```

---

## Task 1: 创建配置模块 config.py

**Files:**
- Create: `wechat-ai-reply/config.py`

- [ ] **Step 1: 创建 config.py**

```python
"""
微信 AI 自动回复 - 配置模块
集中管理 API Key、联系人列表、风格提示词等配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# ============== 配置项 ==============

# Claude API Key - 需要用户自行填写
API_KEY = os.getenv("CLAUDE_API_KEY", "sk-ant-your-key-here")

# 指定联系人列表（好友名称，精确匹配）
CONTACTS = [
    "张三",
    "李四",
    "王五",
    # 在此添加更多联系人
]

# 消息检查间隔（秒）
CHECK_INTERVAL = 2

# ============== 风格提示词 ==============

STYLE_PROMPT = """你是一个聊天高手，说话风格是：
- 接地气的真诚，带点自嘲的松弛感
- 会吐槽也会关心人，情绪真实不装
- 吐槽但不传递负面情绪，自带乐观松弛感
- 用细节和玩笑照顾对方情绪
- 安慰不空洞、不油腻
- 口语化、短句多，节奏轻快，聊天无压力

现在有人对你说："{message}"
请用符合上述风格的方式回复，只返回回复内容，不要加引言或其他解释。"""


# ============== 配置函数 ==============

def load_config():
    """加载并返回完整配置"""
    return {
        "api_key": API_KEY,
        "contacts": CONTACTS,
        "check_interval": CHECK_INTERVAL,
        "style_prompt": STYLE_PROMPT,
    }


def get_contacts():
    """获取指定联系人列表"""
    return CONTACTS


def get_style_prompt(message: str) -> str:
    """生成带消息内容的完整提示词"""
    return STYLE_PROMPT.format(message=message)


def is_contact(name: str) -> bool:
    """检查是否在指定联系人列表中"""
    return name in CONTACTS


def get_api_key():
    """获取 API Key"""
    if API_KEY == "sk-ant-your-key-here":
        raise ValueError("请先在 config.py 中设置你的 Claude API Key")
    return API_KEY
```

- [ ] **Step 2: 提交**

```bash
git add wechat-ai-reply/config.py
git commit -m "feat: add config module"
```

---

## Task 2: 创建 AI 回复模块 claude_replier.py

**Files:**
- Create: `wechat-ai-reply/claude_replier.py`

- [ ] **Step 1: 创建 claude_replier.py**

```python
"""
微信 AI 自动回复 - Claude 回复模块
调用 Claude API 生成符合用户风格的回复
"""

import anthropic
from config import get_api_key, get_style_prompt


# Claude API Client
_client = None


def get_client():
    """获取或创建 Claude API Client（单例模式）"""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=get_api_key())
    return _client


async def generate_reply(message: str) -> str:
    """
    根据用户消息生成符合风格的回复

    Args:
        message: 用户发送的消息内容

    Returns:
        str: 生成的回复内容

    Raises:
        Exception: API 调用失败时抛出异常
    """
    client = get_client()
    prompt = get_style_prompt(message)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text.strip()


def generate_reply_sync(message: str) -> str:
    """同步版本的 generate_reply"""
    import asyncio
    return asyncio.run(generate_reply(message))
```

- [ ] **Step 2: 提交**

```bash
git add wechat-ai-reply/claude_replier.py
git commit -m "feat: add Claude reply module"
```

---

## Task 3: 创建消息监听模块 wechat_listener.py

**Files:**
- Create: `wechat-ai-reply/wechat_listener.py`

- [ ] **Step 1: 创建 wechat_listener.py**

```python
"""
微信 AI 自动回复 - 消息监听模块
监听微信消息，判断是否需要处理
"""

import time
import threading
from typing import Callable, Optional
from config import get_contacts, is_contact, CHECK_INTERVAL

# wxauto 导入
try:
    import wxauto
    WXAUTO_AVAILABLE = True
except ImportError:
    WXAUTO_AVAILABLE = False


class WeChatListener:
    """微信消息监听器"""

    def __init__(self, check_interval: int = CHECK_INTERVAL):
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._wx = None
        self._callback: Optional[Callable] = None

    def _init_wechat(self):
        """初始化微信客户端"""
        if not WXAUTO_AVAILABLE:
            raise ImportError("请先安装 wxauto: pip install wxauto")
        self._wx = wxauto.WeChat()

    def set_callback(self, callback: Callable):
        """
        设置消息回调函数

        Args:
            callback: 回调函数，签名为 (sender: str, message: str) -> None
        """
        self._callback = callback

    def _process_messages(self):
        """处理新消息"""
        if self._wx is None:
            self._init_wechat()

        # 获取最新消息
        messages = self._wx.GetListenMessage()

        for msg in messages:
            sender = msg[0]  # 发送者名称
            content = msg[1]  # 消息内容

            # 只处理指定联系人的消息
            if is_contact(sender) and self._callback:
                try:
                    self._callback(sender, content)
                except Exception as e:
                    print(f"处理消息失败: {e}")

    def _listen_loop(self):
        """监听循环"""
        while self._running:
            try:
                self._process_messages()
            except Exception as e:
                print(f"监听异常: {e}")
            time.sleep(self.check_interval)

    def start(self):
        """启动监听"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print(f"微信监听已启动，检查间隔 {self.check_interval} 秒")

    def stop(self):
        """停止监听"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("微信监听已停止")


def test_listener():
    """测试监听器基本功能"""
    listener = WeChatListener()

    def on_message(sender: str, message: str):
        print(f"收到消息 - 发送者: {sender}, 内容: {message}")

    listener.set_callback(on_message)
    return listener
```

- [ ] **Step 2: 提交**

```bash
git add wechat-ai-reply/wechat_listener.py
git commit -m "feat: add WeChat listener module"
```

---

## Task 4: 创建主入口 main.py

**Files:**
- Create: `wechat-ai-reply/main.py`

- [ ] **Step 1: 创建 main.py**

```python
"""
微信 AI 自动回复 - 主入口
协调各模块运行
"""

import sys
import asyncio
from config import load_config, get_contacts
from wechat_listener import WeChatListener
from claude_replier import generate_reply


class AutoReplier:
    """自动回复器"""

    def __init__(self):
        self.listener = WeChatListener()
        self._reply_count = 0

    def _handle_message(self, sender: str, message: str):
        """处理收到的消息"""
        print(f"\n收到消息 from {sender}: {message}")

        # 调用 Claude API 生成回复
        try:
            reply = asyncio.run(generate_reply(message))
            print(f"生成回复: {reply}")

            # 发送回复
            self._send_reply(sender, reply)
            self._reply_count += 1
            print(f"已回复 ({self._reply_count})")

        except Exception as e:
            print(f"生成回复失败: {e}")

    def _send_reply(self, sender: str, reply: str):
        """发送回复（需要微信客户端保持运行）"""
        import wxauto
        wx = wxauto.WeChat()
        wx.SendMsg(reply, to(sender))

    def run(self):
        """启动自动回复"""
        print("=" * 50)
        print("微信 AI 自动回复启动")
        print(f"监听联系人: {get_contacts()}")
        print("按 Ctrl+C 停止")
        print("=" * 50)

        self.listener.set_callback(self._handle_message)
        self.listener.start()

        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止...")
            self.listener.stop()
            print("已停止")


def main():
    """主函数"""
    try:
        replier = AutoReplier()
        replier.run()
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 提交**

```bash
git add wechat-ai-reply/main.py
git commit -m "feat: add main entry point"
```

---

## Task 5: 创建依赖文件

**Files:**
- Create: `wechat-ai-reply/requirements.txt`
- Create: `wechat-ai-reply/README.md`

- [ ] **Step 1: 创建 requirements.txt**

```
wxauto>=3.9
anthropic>=0.18.0
```

- [ ] **Step 2: 创建 README.md**

```markdown
# 微信 AI 自动回复

自动回复微信消息，使用 Claude AI 生成符合你风格的回复。

## 功能

- 监听指定联系人的微信消息
- 调用 Claude API 生成符合你风格的回复
- 自动发送回复，无需手动操作

## 安装

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.py`，填入以下配置：

1. **API Key**: 在 [anthropic.com](https://anthropic.com) 获取
2. **联系人列表**: 在 `CONTACTS` 列表中添加要自动回复的人

## 使用

1. 确保微信电脑端已登录
2. 运行程序：

```bash
python main.py
```

3. 按 `Ctrl+C` 停止

## 注意事项

- 需要保持微信电脑端处于登录状态
- 程序会每隔几秒检查新消息
- API 有免费额度，用完会收费
```

- [ ] **Step 3: 提交**

```bash
git add wechat-ai-reply/requirements.txt wechat-ai-reply/README.md
git commit -m "feat: add requirements and README"
```

---

## Task 6: 安装依赖测试

**Files:**
- Modify: `wechat-ai-reply/config.py` (填写 API Key)

- [ ] **Step 1: 安装依赖**

```bash
cd wechat-ai-reply
pip install -r requirements.txt
```

- [ ] **Step 2: 验证安装**

```bash
python -c "import wxauto; import anthropic; print('依赖安装成功')"
```

- [ ] **Step 3: 配置 API Key**

编辑 `config.py`，将 `API_KEY` 改为你自己的 key

- [ ] **Step 4: 提交配置**

```bash
git add wechat-ai-reply/config.py
git commit -m "chore: add API key placeholder"
```

---

## Task 7: 完整测试

**Files:**
- Test: `wechat-ai-reply/main.py`

- [ ] **Step 1: 启动测试**

确保微信电脑端已登录，运行：

```bash
cd wechat-ai-reply
python main.py
```

- [ ] **Step 2: 验证功能**

1. 向指定联系人发送消息
2. 观察程序是否收到消息
3. 检查是否生成并发送了回复

- [ ] **Step 3: 提交测试结果**

```bash
git add .
git commit -m "test: complete integration test"
```

---

## 验证检查清单

- [ ] 所有文件已创建
- [ ] config.py 中 API Key 已配置
- [ ] 联系人列表已填写
- [ ] 依赖已安装
- [ ] 程序可正常启动
- [ ] 可以接收并回复消息