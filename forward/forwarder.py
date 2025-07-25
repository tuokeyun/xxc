import json
import random
import asyncio
from monitor.redis_handler import get_message_from_redis
from utils.logger import write_log

MIN_DELAY = 1
MAX_DELAY = 3

async def forward_message(client, forward_chat_id, message):
    """执行转发消息的逻辑"""
    try:
        # 延迟处理
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        await asyncio.sleep(delay)

        # 获取消息
        msg = await client.get_messages(message['chat_id'], ids=message['message_id'])
        if msg:
            await client.forward_messages(forward_chat_id, msg)
            # 使用 client.session.filename 获取会话文件路径
            print(f"[{client.session.filename}] ✅ 已转发消息: {message['message'][:50]}")
        else:
            print(f"[{client.session.filename}] ⚠️ 无法获取消息: {message['message'][:50]}")

    except Exception as e:
        error_msg = f"[{client.session.filename}] ❌ 转发失败: {str(e)}"
        print(error_msg)
        write_log(
            session_name=client.session.filename,
            event={'message': '转发失败'},
            message_status=error_msg
        )

async def forward_message_from_redis(client, forward_chat_id):
    """从 Redis 获取消息并转发"""
    try:
        # 从 Redis 获取消息
        message_data = await get_message_from_redis(client)
        if message_data:
            await forward_message(client, forward_chat_id, message_data)
        else:
            # 如果 Redis 队列为空，打印警告
            print(f"[{client.session.filename}] 📦 Redis 队列为空")
    except Exception as e:
        error_msg = f"[{client.session.filename}] ❌ 获取消息失败: {str(e)}"
        print(error_msg)
        write_log(
            session_name=client.session.filename,
            event={'message': '获取消息失败'},
            message_status=error_msg
        )
