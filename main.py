import asyncio
from account.login import login_account  # 登录相关
from utils.config import get_config  # 获取配置

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
    
    await login_account(phone=phone, session_name=session_name, role='monitor')

if __name__ == "__main__":
    asyncio.run(main())
