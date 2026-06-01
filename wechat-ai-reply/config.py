"""
微信 AI 自动回复 - 配置模块
集中管理 API Key、联系人列表、风格提示词等配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# ============== 配置项 ==============

# ============== 通义千问 API 配置 ==============

# 阿里云 DashScope API Key - 需要用户自行填写
# 申请地址: https://dashscope.console.aliyun.com/
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-2b4319a2015a460497ef9d47c38057e2")

# 模型选择: qwen-turbo (快速) / qwen-plus (更强)
MODEL_NAME = "qwen-plus"

# 指定联系人列表（好友名称，精确匹配）
CONTACTS = [
    "王思乃",
    "文艺",
    "妈妈",
    "夏瑶",
    "胡明灿",
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
        "api_key": DASHSCOPE_API_KEY,
        "contacts": CONTACTS,
        "check_interval": CHECK_INTERVAL,
        "style_prompt": STYLE_PROMPT,
        "model_name": MODEL_NAME,
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
    if DASHSCOPE_API_KEY == "your-api-key-here":
        raise ValueError("请先在 config.py 中设置你的 DashScope API Key")
    return DASHSCOPE_API_KEY
