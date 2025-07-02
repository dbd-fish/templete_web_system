# Dockerfile for E2E Testing (Cypress)
# Cypress公式推奨構成: run-and-exitパターン

# ベースイメージとして cypress/included を使用
FROM cypress/included:13.17.0

# 必要なパッケージは cypress/included に含まれているため、追加のインストールは不要

# 作業ディレクトリを設定
WORKDIR /e2e

# E2Eテストコードをコピー
COPY . ./

# Cypress公式推奨: デフォルトでテスト実行（run-and-exit）
# 設定ファイルをチェックしてからテスト実行
ENTRYPOINT ["npx", "cypress", "run"]