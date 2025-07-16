#!/usr/bin/env python3
import asyncio
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from utils.logger import get_logger, write_log
from utils.config import get_config
import os

# 初始化全局配置
# 从配置中获取 API_ID 和 API_HASH
config = get_config()  
logger = get_logger(__name__)

# API 配置
API_ID = '13168695'
API_HASH = 'ca833edfad0a8a7c86ead6a55b069cc6'

# 用于存储不同角色的会话路径
SESSION_PATH = 'sessions'

async def login_account(phone, session_name, role):
    """登录主函数：monitor/forward 分支"""
    session_folder = os.path.join(SESSION_PATH, role)  # 根据角色来分配不同的文件夹
    logger.info(f"正在为角色 '{role}' 创建/使用会话存储文件夹: {session_folder}")
    
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)  # 如果文件夹不存在就创建
        logger.info(f"会话文件夹 {session_folder} 不存在，已创建")
    else:
        logger.info(f"会话文件夹 {session_folder} 已存在，无需创建")

    session_path = os.path.join(session_folder, f"{session_name}_session.db")  # 为每个实例使用独立的数据库

    # 检查是否已经存在会话文件
    if os.path.exists(session_path):
        logger.info(f"会话文件 {session_path} 已存在，跳过认证过程")
        client = TelegramClient(session_path, API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            logger.warning(f"未授权账户，开始认证流程")
            await _handle_authentication(client, phone, session_name)
    else:
        logger.info(f"会话文件 {session_path} 不存在，开始认证")
        client = TelegramClient(session_path, API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            logger.warning(f"未授权账户，开始认证流程")
            await _handle_authentication(client, phone, session_name)

    logger.info(f"[{session_name}] ✅ 登录成功")
    write_log(session_name, {'message': '登录成功'}, f"{phone} 登录成功")

    if role == 'monitor':
        from monitor.monitor import MonitorService
        logger.info(f"[{session_name}] 🔁 初始化监听服务 MonitorService")

        monitor = MonitorService([
            (session_name, API_ID, API_HASH)
        ])

        logger.info(f"[{session_name}] 🚀 启动监听器...")
        await monitor.start_all(config['message_pool_id'])
        logger.info(f"[{session_name}] ✅ 监听器启动完毕，保持运行中")

        while True:
            await asyncio.sleep(3600)

    elif role == 'forward':
        from forward.forwarder import Forwarder
        logger.info(f"[{session_name}] 🚚 启动转发服务 Forwarder")

        forwarder = Forwarder(client)
        await forwarder.start()

        logger.info(f"[{session_name}] ✅ 转发服务运行中")
        while True:
            await asyncio.sleep(3600)

async def _handle_authentication(client, phone, session_name):
    """处理登录验证流程"""
    try:
        logger.info(f"[{session_name}] 📩 发送验证码到 {phone}")
        await client.send_code_request(phone)
        code = input(f"请输入 {phone} 的验证码: ")

        try:
            await client.sign_in(phone, code)
            logger.info(f"[{session_name}] ✅ 验证码登录成功")
        except SessionPasswordNeededError:
            logger.warning(f"[{session_name}] 检测到两步验证")
            password = input("请输入二次验证密码: ")
            await client.sign_in(password=password)
            logger.info(f"[{session_name}] ✅ 两步验证登录成功")

    except Exception as e:
        logger.error(f"[{session_name}] ❌ 认证流程失败: {str(e)}")
        raise

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['monitor', 'forward']:
        print("用法: python login.py [monitor|forward]")
        sys.exit(1)

    account_type = f"{sys.argv[1]}ing_accounts"
    accounts = config["accounts"].get(account_type, [])
    logger.info(f"正在加载 {sys.argv[1]} 角色的账号配置：{account_type}")

    if not accounts:
        print(f"没有配置 {sys.argv[1]} 角色账号!")
        sys.exit(1)

    for acc in accounts:
        try:
            logger.info(f"准备登录账号: {acc['phone']} - 会话: {acc['session_name']}")
            asyncio.run(login_account(
                acc["phone"],
                acc["session_name"],
                sys.argv[1]
            ))
        except KeyboardInterrupt:
            logger.info("🔴 用户中断操作")
            break
        except Exception as e:
            logger.error(f"❌ 处理账号失败: {str(e)}")
            continue

if __name__ == '__main__':
    main()
