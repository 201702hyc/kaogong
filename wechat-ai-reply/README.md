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