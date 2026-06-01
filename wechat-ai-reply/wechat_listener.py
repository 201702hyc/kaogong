"""
微信 AI 自动回复 - 消息监听模块
使用 pywinauto 进行 Windows UI 自动化
"""

import logging
import time
import threading
from collections import deque
from typing import Callable, Optional
from config import get_contacts, is_contact, CHECK_INTERVAL

# pywinauto 导入
try:
    from pywinauto import Application, timings
    PYWINATAU_AVAILABLE = True
except ImportError:
    PYWINATAU_AVAILABLE = False

logger = logging.getLogger(__name__)


class WeChatListener:
    """微信消息监听器 - 使用 pywinauto 实现"""

    def __init__(self, check_interval: int = CHECK_INTERVAL):
        self.check_interval = check_interval
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._app = None
        self._wechat_window = None
        self._callback: Optional[Callable] = None
        self._callback_lock = threading.Lock()
        self._seen_messages = deque(maxlen=100)  # 记录最近处理的消息，避免重复

    def _init_wechat(self):
        """初始化微信客户端"""
        if not PYWINATAU_AVAILABLE:
            raise ImportError("请先安装 pywinauto: pip install pywinauto")

        try:
            # 尝试连接已运行的微信
            self._app = Application(backend="uia").connect(title="微信", timeout=5)
            logger.info("成功连接到微信窗口")
        except Exception:
            # 如果没有找到，尝试启动微信
            try:
                self._app = Application(backend="uia").start(r"C:\Program Files\Tencent\WeChat\WeChat.exe")
                logger.info("已启动微信")
            except Exception as e:
                raise RuntimeError(f"无法连接或启动微信: {e}")

        self._wechat_window = self._app.window(title="微信")
        self._wechat_window.wait('visible', timeout=10)

    def _get_friend_name(self) -> Optional[str]:
        """获取当前聊天窗口的联系人名称"""
        try:
            # 微信窗口顶部标题通常就是联系人名称
            title = self._wechat_window.window_text()
            # 标题格式可能是 "微信 - 王思乃" 或直接是联系人名
            if " - " in title:
                return title.split(" - ")[-1].strip()
            elif title != "微信":
                return title.strip()
        except Exception:
            pass
        return None

    def _get_latest_messages(self) -> list:
        """获取最新消息"""
        messages = []
        try:
            # 查找消息列表区域
            # 使用 Rust 版本的 UI 自动化，更稳定
            msg_list = self._wechat_window.child_window(
                class_name="RustHtmlView"
            )
            if msg_list.exists(timeout=2):
                # 获取文本内容
                texts = msg_list.texts()
                for text in texts:
                    if text and text.strip():
                        messages.append(text.strip())
        except Exception as e:
            logger.debug(f"获取消息失败: {e}")
        return messages

    def _read_chat_messages(self) -> list:
        """读取聊天消息列表"""
        messages = []
        try:
            # 查找消息区域 - 多个可能的选择器
            selectors = [
                {"class_name": "RustHtmlView"},
                {"class_name": "WebView"},
                {"title": "消息"},
            ]

            msg_area = None
            for sel in selectors:
                try:
                    msg_area = self._wechat_window.child_window(**sel)
                    if msg_area.exists(timeout=1):
                        break
                except Exception:
                    continue

            if msg_area:
                # 获取所有文本
                all_text = msg_area.texts()
                # 过滤出实际消息（通常是较短的文本行）
                for text in all_text:
                    if text and len(text) < 500 and len(text) > 0:
                        # 简单过滤
                        messages.append(text)
        except Exception as e:
            logger.debug(f"读取消息失败: {e}")
        return messages

    def set_callback(self, callback: Callable):
        """设置消息回调函数"""
        with self._callback_lock:
            self._callback = callback

    def _process_messages(self):
        """处理新消息"""
        if self._wechat_window is None:
            self._init_wechat()

        try:
            # 获取当前联系人名称
            sender = self._get_friend_name()
            if not sender or not is_contact(sender):
                return

            # 获取消息
            messages = self._get_latest_messages()
            for msg in messages:
                # 避免重复处理
                msg_hash = hash((sender, msg))
                if msg_hash in self._seen_messages:
                    continue
                self._seen_messages.add(msg_hash)

                with self._callback_lock:
                    callback = self._callback
                if callback:
                    try:
                        callback(sender, msg)
                    except Exception as e:
                        logger.error("处理消息失败: %s", e)
        except Exception as e:
            logger.error("处理消息异常: %s", e)

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

    def send_message(self, text: str):
        """发送消息"""
        try:
            # 查找输入框
            input_box = self._wechat_window.child_window(
                class_name="Edit",
                title="Type a message"
            )
            if not input_box.exists():
                # 尝试其他选择器
                input_box = self._wechat_window.child_window(class_name="RichEdit20W")
            if not input_box.exists():
                input_box = self._wechat_window.child_window(class_name="Edit")

            if input_box.exists():
                input_box.set_edit_text(text)
                # 按回车发送
                input_box.type_keys('{ENTER}')
                logger.info("消息已发送: %s", text[:20])
                return True
            else:
                logger.error("未找到输入框")
                return False
        except Exception as e:
            logger.error("发送消息失败: %s", e)
            return False


def test_listener():
    """测试监听器基本功能"""
    listener = WeChatListener()

    def on_message(sender: str, message: str):
        print(f"收到消息 - 发送者: {sender}, 内容: {message}")

    listener.set_callback(on_message)
    return listener