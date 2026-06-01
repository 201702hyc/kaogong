"""
微信 AI 自动回复 - 消息监听模块
监听微信消息，判断是否需要处理
"""

import logging
import time
import threading
from collections import namedtuple
from typing import Callable, Optional
from config import get_contacts, is_contact, CHECK_INTERVAL

# wxauto 导入
try:
    import wxauto
    WXAUTO_AVAILABLE = True
except ImportError:
    WXAUTO_AVAILABLE = False

# 消息命名元组
WeChatMessage = namedtuple("WeChatMessage", ["sender", "content"])

logger = logging.getLogger(__name__)


class WeChatListener:
    """微信消息监听器"""

    def __init__(self, check_interval: int = CHECK_INTERVAL):
        self.check_interval = check_interval
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._wx = None
        self._callback: Optional[Callable] = None
        self._callback_lock = threading.Lock()

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
        with self._callback_lock:
            self._callback = callback

    def _process_messages(self):
        """处理新消息"""
        if self._wx is None:
            self._init_wechat()

        # 获取最新消息
        messages = self._wx.GetListenMessage()

        for msg in messages:
            wx_msg = WeChatMessage(sender=msg[0], content=msg[1])

            # 只处理指定联系人的消息
            if is_contact(wx_msg.sender):
                with self._callback_lock:
                    callback = self._callback
                if callback:
                    try:
                        callback(wx_msg.sender, wx_msg.content)
                    except Exception as e:
                        logger.error("处理消息失败: %s", e)

    def _listen_loop(self):
        """监听循环"""
        while self._running.is_set():
            try:
                self._process_messages()
            except Exception as e:
                logger.error("监听异常: %s", e)
            time.sleep(self.check_interval)

    def is_running(self) -> bool:
        """检查监听器是否正在运行"""
        return self._running.is_set()

    def start(self):
        """启动监听"""
        if self._running.is_set():
            return

        self._running.set()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("微信监听已启动，检查间隔 %d 秒", self.check_interval)

    def stop(self):
        """停止监听"""
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("微信监听已停止")


def test_listener():
    """测试监听器基本功能"""
    listener = WeChatListener()

    def on_message(sender: str, message: str):
        print(f"收到消息 - 发送者: {sender}, 内容: {message}")

    listener.set_callback(on_message)
    return listener