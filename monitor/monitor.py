#!/usr/bin/env python3
import asyncio
import sys
import time  # 引入时间模块来实现延迟
from telethon import TelegramClient
from .message_listener import MessageListener
from .redis_handler import RedisHandler
from utils.logger import get_logger
import traceback
import os

# 从配置文件中获取 API_ID 和 API_HASH
API_ID = '13168695'
API_HASH = 'ca833edfad0a8a7c86ead6a55b069cc6'

logger = get_logger(__name__)

class MonitorService:
    def __init__(self, client_configs):
        # 通过拼接的方式，为每个 client 配置独立的会话文件夹
        self.clients = [
            # 每个客户端会话存储路径不同，避免冲突
            TelegramClient(
                os.path.join('sessions', 'monitor', f'{name}_session'),  # 使用独立的 session 文件
                API_ID,
                API_HASH
            ) 
            for name, api_id, api_hash in client_configs
        ]
        self.redis = RedisHandler()
        self.listeners = []
        self._running = False
        logger.info("🔌 MonitorService 初始化完成，已创建客户端实例")

    async def start_all(self, forward_chat_id):
        """启动所有监听器实例"""
        try:
            # 尝试连接 Redis
            await self.redis.connect()
            logger.info(f"🔌 Redis 初始化完成")
        except Exception as e:
            logger.error(f"❌ Redis 连接失败，监听器无法启动: {e}")
            logger.debug(traceback.format_exc())  # 打印详细错误栈
            return

        logger.info(f"🚀 即将启动 {len(self.clients)} 个 TelegramClient 客户端")

        # 启动所有客户端
        for idx, client in enumerate(self.clients):
            try:
                # 为每个客户端添加延迟，避免同时启动
                await asyncio.sleep(2)  # 延迟 1 秒，避免多个客户端同时访问数据库
                logger.info(f"[Client-{idx}] 启动客户端 {client.session_name}")

                # 启动客户端
                await client.start()
                logger.info(f"[Client-{idx}] ✅ 客户端连接成功: {client.session_name}")

                # 创建 MessageListener 实例并启动
                listener = MessageListener(client, self.redis)
                self.listeners.append(listener)

                # 启动每个监听器
                await listener.start(forward_chat_id)
                logger.info(f"[Client-{idx}] 🎧 监听器启动完成")

            except Exception as e:
                # 如果某个客户端启动失败，记录失败信息
                logger.error(f"[Client-{idx}] ❌ 启动失败: {e}")
                logger.debug(traceback.format_exc())  # 打印详细错误栈

        # 所有客户端启动完毕
        self._running = True
        logger.info(f"✅ 所有监听器已完成启动")

    async def stop_all(self):
        """优雅关闭所有监听器"""
        logger.info("🛑 正在关闭所有监听器...")

        # 停止所有监听器
        for listener in self.listeners:
            try:
                await listener.stop()
                logger.info("✅ 监听器停止成功")
            except Exception as e:
                logger.error(f"❌ 关闭监听器失败: {e}")
                logger.debug(traceback.format_exc())  # 打印详细错误栈

        # 清理 Redis 连接
        await self.redis.cleanup()
        logger.info("✅ 所有监听器与 Redis 已关闭")

        # 结束运行标志
        self._running = False
