from langchain_community.embeddings import HuggingFaceEmbeddings
import threading

embeddings_model = None

def load_model():
    global embeddings_model
    print("🚀 Start loading model...")  # In ra lúc bắt đầu load
    embeddings_model = HuggingFaceEmbeddings(
        model_name="Alibaba-NLP/gte-multilingual-base",
        model_kwargs={"trust_remote_code": True}
    )
    print("✅ Model loaded!")  # In ra khi load xong

# Hàm gọi khi startup FastAPI
def start_background_model():
    threading.Thread(target=load_model).start()
