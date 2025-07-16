import json
import traceback
import aioredis
from utils.logger import get_logger
from utils.config import get_config
from tenacity import retry, stop_after_attempt, wait_random

logger = get_logger(__name__)

class RedisHandler:
    def __init__(self):
        self.config = get_config()['redis']
        self.client = None

    async def connect(self):
        """异步初始化 Redis 连接"""
        try:
            self.client = aioredis.from_url(
                f"redis://{self.config['host']}:{self.config['port']}/{self.config['db']}",
                decode_responses=False,
                socket_timeout=5
            )
            logger.info("✅ Redis 已连接")
        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {str(e)}")
            logger.debug(traceback.format_exc())
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=5))
    async def store_message(self, message_data):
        """将消息写入 Redis Stream"""
        try:
            if not self.client:
                logger.warning("⚠️ Redis 未初始化，自动连接中...")
                await self.connect()

            await self.client.xadd(
                "telegram_messages",
                {"data": json.dumps(message_data)},
                maxlen=10000
            )
            logger.info("📥 Redis 写入成功")

        except Exception as e:
            logger.error(f"❌ Redis 写入失败: {str(e)}")
            logger.debug(traceback.format_exc())
            raise

    async def cleanup(self):
        """关闭 Redis 连接"""
        try:
            if self.client:
                await self.client.close()
                logger.info("🔌 Redis 已关闭连接")
        except Exception as e:
            logger.error(f"❌ Redis 关闭连接异常: {str(e)}")