# ベースイメージとして cypress/included を使用
FROM cypress/included:13.17.0

# 必要なパッケージは cypress/included に含まれているため、追加のインストールは不要

# 作業ディレクトリを設定
WORKDIR /e2e

# プロジェクトのソースコード全体をコピー
COPY . .

# 依存関係をインストール（Cypressは既にインストール済みなので追加の依存関係がある場合のみ）
# RUN npm install

# Cypress の動作確認（cypress/included はインストール済みなので基本的に不要ですが、問題がある場合は有効化）
# RUN npx cypress verify

# コンテナを継続起動させるための設定
CMD ["sh", "-c", "while true; do sleep 3600; done"]
