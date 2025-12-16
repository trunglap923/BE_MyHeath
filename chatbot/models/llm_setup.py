from langchain_deepseek import ChatDeepSeek
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from chatbot.config import DEEPSEEK_API_KEY

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ Thiếu biến môi trường: DEEPSEEK_API_KEY trong file .env")

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.3,
    max_tokens=2048,
    timeout=30,
    max_retries=2,
)

llm_stream = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.3,
    max_tokens=2048,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)

def get_llm(model_name: str = "deepseek-chat", temperature: float = 0.3):
    return ChatDeepSeek(
        model=model_name,
        temperature=temperature,
        max_tokens=2048,
        timeout=30,
        max_retries=2,
    )

__all__ = ["llm", "get_llm"]
