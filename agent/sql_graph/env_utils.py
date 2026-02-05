import os
from dotenv import load_dotenv

load_dotenv(override = True)

def get_env(key: str, required: bool = False) -> str | None:
    """读取环境变量，可选择是否必须存在"""
    value = os.getenv(key)

    if required and value is None:
        raise ValueError(f"Environment variable {key} is not set")

    return value

# ===== 阿里千问 =====
ALIBABA_API_KEY = get_env("ALIBABA_API_KEY")
ALIBABA_BASE_URL = os.getenv("ALIBABA_BASE_URL")

# ===== DeepSeek =====
DEEPSEEK_API_KEY = get_env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# ===== OpenAI =====
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# ===== 智谱 AI =====
ZHIPUAI_API_KEY = get_env("ZHIPUAI_API_KEY")
ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL")
