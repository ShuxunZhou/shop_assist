import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from agent.sql_graph.env_utils import ZHIPUAI_API_KEY
# from zhipuai import ZhipuAI
from dotenv import load_dotenv
load_dotenv()

# 亲测：智谱AI的国际节点证书配置存在问题。SSL证书expired --> 改用chatgpt
# zhipuai_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

llm = ChatOpenAI(
    temperature=0,
    model='gpt-5.4',
    api_key=os.getenv("OPENAI_API_KEY")
)


# llm = ChatAnthropic(
#     temperature=0,
#     model='claude-sonnet-4-20250514',
#     api_key=os.getenv("ANTHROPIC_API_KEY")
# )