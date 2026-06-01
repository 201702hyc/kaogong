"""
微信 AI 自动回复 - 主入口
协调各模块运行
"""

import sys
import time
import wxauto
from config import load_config, get_contacts
from wechat_listener import WeChatListener
from claude_replier import generate_reply_sync


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
            reply = generate_reply_sync(message)
            print(f"生成回复: {reply}")

            # 发送回复
            self._send_reply(sender, reply)
            self._reply_count += 1
            print(f"已回复 ({self._reply_count})")

        except Exception as e:
            print(f"生成回复失败: {e}")

    def _send_reply(self, sender: str, reply: str):
        """发送回复（需要微信客户端保持运行）"""
        wx = wxauto.WeChat()
        wx.SendMsg(reply, to=sender)

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