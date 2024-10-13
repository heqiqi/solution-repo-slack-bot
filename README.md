# Solution repo slack bot 介绍
基于slack的API, 创建的app. 主要功能是方面创建基于AWS人工智能服务的chat bot.

- web api使用了flask框架
- LLM使用了AWS bedrock的 Claude3 sonnet
- RAG使用的是AWS bedrock knowledgebase
    - embedding model: multilangv3
    - vector DB: opensearch vector
    - generate model: sonnect 3.5

## 使用方式:
    1. 在aws bedrock 创建知识库
    2. 根据上一步启动的KB,配置./config.json文件中的kb_id 和 kb_configs字段
    3. 在env-export.sh文件中,配置slack相关token和key
    4. pip install requirements.txt
    5. 配置能够调用bedrock的账号的AK,SK `aws configure`
    6. 启动: bash app_start.sh

