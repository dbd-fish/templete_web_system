# Dockerfile for Frontend (React Router)
# アプリ直下配置版 - マルチステージビルド対応

# ===== 開発ステージ =====
FROM node:22 AS development

# 作業ディレクトリを設定
WORKDIR /app

# フロントエンドコードをコピー
COPY . ./frontend/

# フロントエンドディレクトリに移動
WORKDIR /app/frontend

# 依存関係をインストール
RUN npm ci --only=production=false

# ポート3000と5173を公開（本番用と開発用）
EXPOSE 3000 5173

# 開発サーバーを起動
CMD ["npm", "run", "dev"]

# ===== ビルドステージ =====
FROM node:22 AS builder

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# アプリケーションコードをコピー
COPY . .

# ビルド実行
RUN npm run build

# ===== 本番ステージ =====
FROM node:22-slim AS production

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 本番用依存関係のみインストール
RUN npm ci --only=production && npm cache clean --force

# ビルド成果物をコピー
COPY --from=builder /app/build ./build

# 本番用ポート公開
EXPOSE 3000

# 本番サーバーを起動
CMD ["npm", "run", "start"]

# ===== デフォルトステージ（開発用） =====
FROM development AS default

