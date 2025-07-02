# Dockerfile for Frontend (React Router)
# モノレポ対応版

# ベースイメージとしてNode.jsを使用
FROM node:22

# 作業ディレクトリを設定
WORKDIR /app

# フロントエンドコードをコピー
COPY apps/frontend/ ./frontend/

# フロントエンドディレクトリに移動
WORKDIR /app/frontend

# 依存関係をインストール
RUN npm install

# ポート3000と5173を公開（本番用と開発用）
EXPOSE 3000 5173

# 開発サーバーを起動（--hostオプションでコンテナ外からアクセス可能にする）
CMD ["npm", "run", "dev"]

