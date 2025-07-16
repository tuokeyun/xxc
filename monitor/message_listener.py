from telethon import events
from utils.logger import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential
import traceback

logger = get_logger(__name__)

class MessageListener:
    def __init__(self, client, redis_handler):
        self.client = client
        self.redis = redis_handler
        self._running = False

    async def start(self, forward_chat_id):
        """启动消息监听"""
        if self._running:
            logger.warning(f"[{self.client.session_name}] ⚠️ 已经在运行中，跳过重复启动")
            return

        @self.client.on(events.NewMessage())
        async def handler(event):
            if event.is_group:
                try:
                    logger.info(f"[{self.client.session_name}] 📥 收到群消息 chat_id={event.chat_id} msg_id={event.id}")
                    await self._process_message(event, forward_chat_id)
                except Exception as e:
                    logger.error(f"[{self.client.session_name}] ❌ 处理消息失败: {e}")
                    logger.debug(traceback.format_exc())

        self._running = True
        logger.info(f"[{self.client.session_name}] ✅ 消息监听器已启动")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _process_message(self, event, forward_chat_id):
        """处理并存储消息"""
        try:
            message_data = {
                'session': self.client.session_name,
                'chat_id': event.chat_id,
                'message_id': event.message.id,
                'text': event.raw_text,
                'timestamp': int(event.date.timestamp()),
                'forward_to': forward_chat_id
            }

            logger.info(f"[{self.client.session_name}] 📤 正在写入 Redis: chat_id={event.chat_id} msg_id={event.message.id}")
            await self.redis.store_message(message_data)
            logger.info(f"[{self.client.session_name}] ✅ 消息已成功写入 Redis")
        except Exception as e:
            logger.error(f"[{self.client.session_name}] ❌ 消息写入 Redis 失败: {e}")
            logger.debug(traceback.format_exc())
            raise  # 必须重新抛出让 retry 生效

    async def stop(self):
        """停止监听"""
        self._running = False
        logger.info(f"[{self.client.session_name}] ⛔️ 停止监听器")
        await self.client.disconnect()