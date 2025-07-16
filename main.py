import asyncio
from account.login import login_account  # 登录相关
from monitor.monitor import start_monitoring  # 启动监控
from config import get_config  # 获取配置

async def main():
    # 获取配置
    config = get_config()
    
    # 取出监控账号信息
    monitoring_accounts = config['accounts']['monitoring_accounts']
    if not monitoring_accounts:
        print("没有找到监控账号配置")
        return

    # 假设选择第一个监控账号
    account = monitoring_accounts[0]
    phone = account['phone']
    session_name = account['session_name']
    
    # 启动登录
    client = await login_account(phone=phone, session_name=session_name)  # 调用登录函数
    if client:
        # 获取监控群组ID
        forward_chat_id = account.get('forward_chat_id', None)
        if forward_chat_id is None:
            print(f"未配置 {session_name} 的目标群主 ID")
            return
        await start_monitoring(client, forward_chat_id)  # 启动监控

if __name__ == "__main__":
    asyncio.run(main())
