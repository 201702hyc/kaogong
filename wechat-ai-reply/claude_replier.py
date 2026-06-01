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