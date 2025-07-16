# /www/wwwroot/person_pool_v2/utils/logger.py
import logging
import os
from datetime import datetime
from utils.config import get_config

config = get_config()

def get_logger(name):
    """创建并配置日志记录器"""
    # 创建日志目录
    log_dir = os.path.join(config.get('log_dir', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 添加成功日志方法
def write_log(session_name, event, message_status):
    logger = get_logger(session_name)
    logger.info(f"{event['message']} - {message_status}")