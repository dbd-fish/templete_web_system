# CLAUDE.md - Cypress E2E テスト

このファイルは、CypressコンテナでのE2Eテストのセットアップと実行に関する情報を提供します。
日本語で回答してください。

## Cypress E2E テスト概要

Cypress 13.17.0を使用したエンドツーエンドテスト環境です。
- **テストフレームワーク**: Cypress 13.17.0
- **実行環境**: cypress/included Dockerイメージ
- **ベースイメージ**: ヘッドレスブラウザ対応
- **テスト対象**: フロントエンド（React Router + Vite）

## ディレクトリ構成

```
cypress/
├── Dockerfile                   # Cypressコンテナ設定
├── cypress.config.js            # Cypress設定ファイル
├── run-tests.sh                 # テスト実行スクリプト
├── cypress/                     # Cypressテストファイル
│   └── support/                 # サポートファイル
│       ├── commands/            # カスタムコマンド
│       │   ├── login.js         # ログイン関連コマンド
│       │   └── logout.js        # ログアウト関連コマンド
│       ├── errorHandling.js     # エラーハンドリング
│       └── index.js             # サポートファイルのエントリーポイント
└── CLAUDE.md                    # このファイル
```

## 開発コマンド

### Docker環境でのテスト実行
```bash
# Cypressコンテナを含む全サービス起動
docker compose up

# Cypressコンテナのみ起動
docker compose up cypress

# Cypressコンテナ再ビルド
docker compose build cypress

# コンテナ内でシェルアクセス
docker exec -it cypress_container sh
```

### テスト実行
```bash
# 全テストをヘッドレスモードで実行
docker exec cypress_container ./run-tests.sh

# 特定のテストファイル実行
docker exec cypress_container ./run-tests.sh --spec "cypress/e2e/example.cy.js"

# カスタムオプション付きでテスト実行
docker exec cypress_container ./run-tests.sh --browser chrome --headed
```

### Cypressコンテナ内での直接実行
```bash
# コンテナ内でテスト実行
npx cypress run

# ヘッドレスでブラウザ指定
npx cypress run --browser chrome

# 特定のテストファイル実行
npx cypress run --spec "cypress/e2e/**/*.cy.js"
```

## Cypress設定詳細

### 基本設定（cypress.config.js）
```javascript
{
  e2e: {
    baseUrl: 'http://frontend:5173',  // コンテナ間通信
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,                     # ビデオ録画無効
    screenshotOnRunFailure: true      # 失敗時スクリーンショット
  }
}
```

### 環境変数
- `CYPRESS_baseUrl`: `http://frontend:5173`（docker-compose.yml設定）

## テスト構成

### テストディレクトリ
テストファイルは以下のように配置します：
```
cypress/
├── e2e/                         # E2Eテスト（ローカル環境用）
│   └── **/*.cy.js
└── front_st/                    # 画面単位テスト
    └── **/*.cy.js
```

### カスタムコマンド
事前定義されたカスタムコマンド：
- **login.js**: ログイン処理の自動化
- **logout.js**: ログアウト処理の自動化
- **errorHandling.js**: エラーハンドリング

使用例：
```javascript
// ログインコマンド使用
cy.login('username', 'password')

// ログアウトコマンド使用  
cy.logout()
```

## コンテナ設定詳細

### Dockerfile
- **ベースイメージ**: `cypress/included:13.17.0`
- **作業ディレクトリ**: `/e2e`
- **継続起動**: `CMD ["sh", "-c", "while true; do sleep 3600; done"]`

### コンテナの特徴
- **ヘッドレス実行**: GUI不要でCI/CD対応
- **継続起動**: テスト完了後もコンテナが起動し続ける
- **ボリュームマウント**: ホストとテストファイル同期

### ネットワーク構成
- **frontend-network**: フロントエンド、バックエンド、Cypressが接続
- **テスト対象**: `http://frontend:5173`（コンテナ間通信）

## テスト実行スクリプト（run-tests.sh）

### 基本使用方法
```bash
# 全テスト実行
./run-tests.sh

# 特定ファイル実行
./run-tests.sh --spec "cypress/e2e/login.cy.js"

# 複数オプション
./run-tests.sh --browser chrome --spec "cypress/e2e/**/*.cy.js"
```

### スクリプトの機能
- フロントエンド・バックエンドの起動待機（10秒）
- 引数なしの場合は全テスト実行
- 引数ありの場合はオプション渡し
- テスト完了メッセージ表示

## 開発時の注意点

### テスト対象URL
- **コンテナ内**: `http://frontend:5173`
- **ローカル開発**: `http://localhost:5173`（必要に応じて設定変更）

### テスト実行タイミング
- フロントエンドとバックエンドが完全に起動してから実行
- `depends_on` でコンテナ起動順序を制御済み

### ファイル同期
- `./cypress:/e2e` でボリュームマウント
- ホストでテストファイル編集 → コンテナ内で即座に反映

## トラブルシューティング

### よくある問題
1. **テスト対象に接続できない**:
   - フロントエンドコンテナが起動していることを確認
   - `docker compose logs frontend` でフロントエンドログ確認
   - ネットワーク接続確認: `docker exec cypress_container ping frontend`

2. **テストファイルが見つからない**:
   - ボリュームマウントが正しく設定されているか確認
   - `docker exec cypress_container ls /e2e` でファイル確認

3. **権限エラー**:
   - `run-tests.sh` に実行権限があるか確認
   - `chmod +x run-tests.sh` で権限付与

### デバッグ
```bash
# Cypressデバッグモード
DEBUG=cypress:* npx cypress run

# ブラウザのコンソールログ表示
npx cypress run --browser chrome --headed

# スクリーンショット確認
# テスト失敗時に自動でスクリーンショット保存される
```

### CI/CD連携
このCypress設定はヘッドレス実行対応のため、CI/CDパイプラインで使用可能：
- GitHub Actions
- GitLab CI
- Jenkins
- その他のCI/CDツール

### パフォーマンス最適化
- ビデオ録画無効で高速化
- 必要最小限のviewport設定
- テスト並列実行の検討（`--parallel`オプション）