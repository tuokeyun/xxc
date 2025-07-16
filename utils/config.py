# /www/wwwroot/person_pool_v2/utils/config.py
import os

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  # 确保端口是整数
REDIS_DB = int(os.getenv("REDIS_DB", 0))  # 确保DB是整数

# 其他配置
API_ID = '13168695'
API_HASH = 'ca833edfad0a8a7c86ead6a55b069cc6'

# 账号配置
ACCOUNT_CONFIG = {
    "monitoring_accounts": [
        {
            "phone": "+258869890823",
            "session_name": "user001",
            "role": "monitor"
        }
    ],
    "forwarding_accounts": [
        {
            "phone": "+573016091880",
            "session_name": "user003",
            "role": "forward",
            "forward_chat_id": -1002818021602
        }
    ]
}

MESSAGE_POOL_ID = -1002818021602
KEYWORDS = ["洗款", "赚u", "项目", "赚钱"]
MIN_DELAY = 1
MAX_DELAY = 3
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_config():
    """获取全局配置"""
    return {
        "redis": {
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "db": REDIS_DB
        },
        "accounts": ACCOUNT_CONFIG,
        "message_pool_id": MESSAGE_POOL_ID,
        "keywords": KEYWORDS,
        "delay": {
            "min": MIN_DELAY,
            "max": MAX_DELAY
        },
        "log_level": LOG_LEVEL
    }