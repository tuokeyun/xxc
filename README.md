# 项目说明：Telegram 接听与转发系统

## 项目概述

该项目是一个基于 Telegram 的自动化接听与转发系统，分为两个主要模块：

- **接听模块 (Monitor)**：用于监听 Telegram 群组中的新消息，并筛选出符合条件的消息，将其存入 Redis 队列。
- **转发模块 (Forward)**：用于从 Redis 队列中提取消息并将其转发到指定的 Telegram 群组。

通过这个系统，我们可以实现多个小号分别用于接听群消息、筛选并存储符合条件的消息，然后再通过另一些小号进行消息的转发。

## 技术栈

- **语言**：Python 3.8+
- **框架**：
  - **Telethon**：用于与 Telegram API 交互，执行消息的发送、接收、转发等操作。
  - **Redis**：用于存储匹配到的消息，方便转发模块进行批量处理。
- **开发工具**：
  - **asyncio**：Python 内建的异步编程库，用于处理异步任务（如：监听消息、转发消息等）。
  - **日志模块**：用于记录系统日志，便于开发和调试。

## 项目结构
person_pool_v2/
├── account/
│ ├── login.py # 登录模块，负责登录并根据角色执行不同任务
│ ├── account_manager.py # 管理 Telegram 账号的登录、退出等操作
├── monitor/
│ ├── message_listener.py # 监听消息并筛选符合关键词的消息
│ ├── monitor.py # 启动接听任务，调用 message_listener.py
│ └── redis_handler.py # 处理与 Redis 的交互，存储和获取消息
├── forward/
│ ├── forward.py # 转发任务模块，负责从 Redis 获取消息并转发
│ ├── forwarder.py # 执行具体的消息转发逻辑
│ ├── delay_manager.py # 控制转发延迟，避免过于频繁的操作
├── utils/
│ ├── config.py # 配置文件，包含 Redis 配置、API ID、账号配置等
│ ├── logger.py # 日志记录模块
├── main.py # 主程序入口，根据不同角色启动不同模块
├── requirements.txt # 项目依赖文件
└── README.md # 项目说明文件

## 业务逻辑

### 1. 角色区分与登录

系统支持两种角色：**接听小号** 和 **转发小号**。

- **接听小号 (Monitor)**：该角色用于监听 Telegram 群组中的新消息，并筛选出符合条件的消息（例如：匹配关键词）。接收到符合条件的消息后，将这些消息存储到 Redis 中，以便转发模块使用。
- **转发小号 (Forward)**：该角色用于从 Redis 中获取存储的消息，并将其转发到指定的 Telegram 群组。

#### 登录流程

1. **接听小号登录**：执行命令 `python3 account/login.py monitor` 登录接听小号，该账号登录后会开始监听群消息并根据配置的关键词筛选消息，符合条件的消息将存储到 Redis。
2. **转发小号登录**：执行命令 `python3 account/login.py forward` 登录转发小号，该账号登录后会从 Redis 中提取消息，并将其转发到目标群组。

### 2. 监听模块 (Monitor)

- 登录成功的接听小号将自动开始 **监听模块**，该模块会持续监听 Telegram 群组中的新消息。
- 当接收到一条新消息时，系统会检查消息是否包含关键词，如果包含，就会将这条消息存储到 Redis。
- **关键词筛选**：通过在配置文件中配置 `KEYWORDS` 列表，系统可以筛选出符合条件的消息。例如：`["洗款", "赚u", "项目", "赚钱"]` 等。

### 3. 转发模块 (Forward)

- 登录成功的转发小号将自动开始 **转发模块**，该模块会从 Redis 中提取存储的消息。
- **轮询转发**：系统会轮流使用不同的小号从 Redis 提取消息并转发到指定的目标群组。
- **转发延迟**：为了避免过于频繁的转发操作，系统会控制转发的延迟时间，避免触发 Telegram 的风控机制。

### 4. Redis 数据存储

- 系统使用 Redis 来存储符合条件的消息。消息将以 JSON 格式存储，包含以下字段：
  - `chat_id`: 消息来源群组 ID
  - `message_id`: 消息 ID
  - `message`: 消息内容
  - `session`: 登录的小号会话名
  - `forward_chat_id`: 转发目标群组 ID

### 5. 系统流程

1. **接听小号** 登录后开始监听指定群组，筛选并存储符合条件的消息。
2. **转发小号** 登录后开始从 Redis 中提取消息，并将这些消息转发到目标群组。
3. 系统通过轮询转发，每个转发小号负责转发一部分消息，避免过度频繁操作导致封号。

## 如何使用

1. 克隆或下载项目文件。
2. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
3.配置 config.py：
   设置 API ID 和 API HASH。
   配置 Telegram 账号和角色。
   配置需要监听的关键词。
   配置 Redis 的连接信息。
4.启动监听小号  
   python3 account/login.py monitor
5.启动转发小号
   python3 account/login.py forward
