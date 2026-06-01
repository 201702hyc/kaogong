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