import asyncio
from telethon import TelegramClient
from utils.config import get_config
from utils.logger import write_log

class AccountManager:
    def __init__(self):
        self.config = get_config()  # 获取配置
        self.clients = {}  # 存储每个账号的 TelegramClient 实例

    async def login(self, phone, session_name):
        """登录到 Telegram 客户端"""
        api_id = self.config['api_id']
        api_hash = self.config['api_hash']
        
        client = TelegramClient(session_name, api_id, api_hash)

        await client.connect()
        
        # 登录过程
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await client.sign_in(phone, input('请输入验证码: '))
        
        self.clients[session_name] = client
        write_log(session_name=session_name, event={'message': '登录成功'}, message_status=f'登录成功，账号: {phone}')

    async def logout(self, session_name):
        """退出账号"""
        client = self.clients.get(session_name)
        if client:
            await client.log_out()
            del self.clients[session_name]
            write_log(session_name=session_name, event={'message': '退出登录'}, message_status=f'退出成功，账号: {session_name}')
        else:
            write_log(session_name=session_name, event={'message': '退出失败'}, message_status=f'未找到账号: {session_name}')
    
    async def login_all(self):
        """登录所有账号"""
        accounts = self.config['accounts']['monitoring_accounts'] + self.config['accounts']['forwarding_accounts']
        for account in accounts:
            await self.login(account['phone'], account['session_name'])
    
    async def logout_all(self):
        """退出所有账号"""
        for session_name in self.clients.keys():
            await self.logout(session_name)

    def get_clients(self):
        """获取所有登录的客户端"""
        return self.clients
