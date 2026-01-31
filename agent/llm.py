from langchain_core.messages import HumanMessage, AIMessage
import dashscope
import os

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def call_qwen(messages):
    """
    messages: List[BaseMessage]
    return: AIMessage
    """
    prompt = "\n".join(
        [
            f"{m.type.upper()}: {m.content}"
            for m in messages
        ]
    )

    response = dashscope.Generation.call(
        model="qwen-turbo",
        prompt=prompt,
        result_format="message"
    )

    content = response["output"]["choices"][0]["message"]["content"]
    return AIMessage(content=content)
