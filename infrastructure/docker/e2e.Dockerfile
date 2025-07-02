# Dockerfile for E2E Testing (Cypress)
# モノレポ対応版

# ベースイメージとして cypress/included を使用
FROM cypress/included:13.17.0

# 必要なパッケージは cypress/included に含まれているため、追加のインストールは不要

# 作業ディレクトリを設定
WORKDIR /e2e

# E2Eテストコードをコピー
COPY apps/e2e/ ./

# コンテナを継続起動させるための設定
CMD ["sh", "-c", "while true; do sleep 3600; done"]