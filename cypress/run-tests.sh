#!/bin/bash

# Cypressテスト実行スクリプト
# 使用方法:
# - ヘッドレスモードでテスト実行: ./run-tests.sh
# - 特定のテストファイル実行: ./run-tests.sh --spec "cypress/e2e/example.cy.js"

echo "Cypress E2Eテストを実行します..."

# フロントエンドとバックエンドの起動を待つ
echo "フロントエンドとバックエンドサービスの起動を待機中..."
sleep 10

# Cypressテストを実行
if [ $# -eq 0 ]; then
    # 引数がない場合は全テストを実行
    echo "全てのテストを実行します"
    npx cypress run
else
    # 引数がある場合は引数を渡して実行
    echo "指定されたオプションでテストを実行します: $@"
    npx cypress run "$@"
fi

echo "テスト実行完了"