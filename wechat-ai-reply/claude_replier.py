"""
微信 AI 自动回复 - 通义千问回复模块
调用阿里云 DashScope API 生成符合用户风格的回复
"""

import os
from config import get_api_key, get_style_prompt

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# DashScope API Client
_client = None


def get_client():
    """获取或创建 DashScope API Client（单例模式）"""
    global _client
    if _client is None:
        if not OPENAI_AVAILABLE:
            raise ImportError("请先安装 openai: pip install openai")
        _client = openai.OpenAI(
            api_key=get_api_key(),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
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
    from config import load_config
    config = load_config()
    model_name = config.get("model_name", "qwen-plus")

    client = get_client()
    prompt = get_style_prompt(message)

    response = client.chat.completions.create(
        model=model_name,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()


def generate_reply_sync(message: str) -> str:
    """同步版本的 generate_reply"""
    import asyncio
    return asyncio.run(generate_reply(message))