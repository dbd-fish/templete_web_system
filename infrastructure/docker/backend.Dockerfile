# Dockerfile for Backend (FastAPI)
# モノレポ対応版

# ベースイメージとして公式のPythonイメージを使用
FROM python:3.13

# 作業ディレクトリを設定
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# poetryインストール
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# コンテナ内で仮想環境の作成を無効
RUN poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project true

# バックエンドコードをコピー
COPY apps/backend/ ./backend/

# バックエンドディレクトリに移動
WORKDIR /app/backend

# 依存関係をインストール
RUN poetry install --no-interaction --no-root

# 環境変数の設定
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="/app/backend"

# ポート8000を公開
EXPOSE 8000

# FastAPIアプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]