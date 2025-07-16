import asyncio
import random

MIN_DELAY = 1
MAX_DELAY = 3

async def delay():
    """设置随机延迟，避免频繁操作"""
    delay_time = random.uniform(MIN_DELAY, MAX_DELAY)
    await asyncio.sleep(delay_time)
    print(f"延迟 {delay_time:.2f} 秒")
