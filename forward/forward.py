import asyncio
from telethon import TelegramClient
from forwarder import forward_message_from_redis
from config import get_config

# 获取配置
config = get_config()

# 转发功能
async def start_forwarding(client, forward_chat_id):
    """启动转发任务"""
    while True:
        try:
            await forward_message_from_redis(client, forward_chat_id)
        except Exception as e:
            print(f"[{client.session_name}] ❌ 转发任务异常: {str(e)}")
        await asyncio.sleep(1)

# 启动转发
async def forward(client, forward_chat_id):
    """启动转发小号任务"""
    print(f"[{client.session_name}] 🚀 启动转发任务")
    await start_forwarding(client, forward_chat_id)

