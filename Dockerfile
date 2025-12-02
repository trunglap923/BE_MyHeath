FROM python:3.10-slim

# Tắt cache HF để tránh lỗi nặng
ENV HF_HOME=/cache/huggingface
RUN mkdir -p /cache/huggingface

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose cổng 7860 (HF Spaces yêu cầu)
EXPOSE 7860

# Chạy FastAPI
CMD ["uvicorn", "start:app", "--host", "0.0.0.0", "--port", "7860"]
