from langchain_community.chat_models import ChatOpenAI
from agent.sql_graph.env_utils import ZHIPUAI_API_KEY
from zhipuai import ZhipuAI

zhipuai_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

llm = ChatOpenAI(
    temperature=0,
    model='glm-4-air-250414',
    api_key="0c60b921bc834455911d3900c5554c1b.DkQt80SF6J8EqHGf",
    base_url="https://api.zhipu.ai/",
)