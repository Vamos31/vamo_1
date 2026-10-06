FROM python:3.12-slim
WORKDIR /backend

# uv 本体は公式イメージからバイナリだけコピーする
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

# 依存だけ先に入れてレイヤーキャッシュを効かせる
COPY requirements.txt ./
RUN uv pip install --no-cache -r requirements.txt

COPY . ./

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
