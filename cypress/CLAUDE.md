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

## 開発コマンド（Cypress公式推奨）

### テスト実行（推奨方法）
```bash
# 基本サービス起動（フロントエンド・バックエンド・データベース）
docker compose up frontend backend db

# E2Eテスト実行（Cypress公式推奨: run-and-exit）
docker compose --profile test run --rm cypress

# 特定テストファイルのみ実行
docker compose --profile test run --rm cypress --spec "cypress/e2e/example.cy.js"

# 異なるブラウザでテスト実行
docker compose --profile test run --rm cypress --browser chrome
```

### 開発時デバッグ用
```bash
# Cypressコンテナ内でシェルアクセス（デバッグ用）
docker compose --profile test run --rm cypress sh

# ワンショット実行（プロファイル不使用）
docker compose run --rm cypress
```

### CI/CD統合
```bash
# CI/CDパイプライン用（ヘッドレス実行）
docker compose --profile test run --rm cypress --config video=false
```

### 従来の手動実行（デバッグ時のみ）
```bash
# シェルアクセス後の手動実行
docker compose --profile test run --rm cypress sh
# コンテナ内で:
npx cypress run
npx cypress run --browser chrome
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

### Dockerfile（Cypress公式推奨）
- **ベースイメージ**: `cypress/included:13.17.0`
- **作業ディレクトリ**: `/e2e`
- **エントリーポイント**: `ENTRYPOINT ["npx", "cypress", "run"]`

### コンテナの特徴（run-and-exitパターン）
- **ヘッドレス実行**: GUI不要でCI/CD対応
- **Run-and-Exit**: テスト完了後に自動終了（Cypress公式推奨）
- **ボリュームマウント**: ホストとテストファイル同期
- **プロファイル使用**: `--profile test` でテスト時のみ起動

### ネットワーク構成
- **frontend-network**: フロントエンド、バックエンド、Cypressが接続
- **テスト対象**: `http://frontend:5173`（コンテナ間通信）

## Docker Compose プロファイル使用法

### プロファイルのメリット
- **依存関係の明確化**: テスト実行時のみCypressコンテナが起動
- **リソース効率**: 不要時はCypressコンテナが起動しない
- **Cypress公式推奨**: run-and-exitパターンに準拠
- **CI/CD対応**: 自動化パイプラインに最適

### 基本的な使用方法
```bash
# ステップ1: 基本サービス起動
docker compose up -d frontend backend db

# ステップ2: テスト実行
docker compose --profile test run --rm cypress

# ステップ3: 基本サービス停止
docker compose down
```

## 開発時の注意点

### テスト対象URL
- **コンテナ内**: `http://frontend:5173`
- **ローカル開発**: `http://localhost:5173`（必要に応じて設定変更）

### テスト実行タイミング（重要）
- **事前起動必須**: フロントエンドとバックエンドを事前に起動
- **依存関係**: `depends_on` は起動順序のみ制御（起動完了は保証しない）
- **推奨手順**: 
  1. `docker compose up -d frontend backend db`
  2. 各サービスの起動完了を確認
  3. `docker compose --profile test run --rm cypress`

### ファイル同期
- `./cypress:/e2e` でボリュームマウント
- ホストでテストファイル編集 → コンテナ内で即座に反映

## トラブルシューティング

### よくある問題
1. **テスト対象に接続できない**:
   - 事前にフロントエンド・バックエンドが起動しているか確認
   - `docker compose logs frontend` でフロントエンドログ確認
   - ネットワーク接続確認: `docker compose --profile test run --rm cypress sh -c "ping frontend"`

2. **プロファイルが見つからない**:
   - `--profile test` オプションを忘れていないか確認
   - `docker compose config --profile test` で設定確認

3. **テストファイルが見つからない**:
   - ボリュームマウントが正しく設定されているか確認
   - `docker compose --profile test run --rm cypress sh -c "ls /e2e"` でファイル確認

### デバッグ
```bash
# Cypressデバッグモード
DEBUG=cypress:* npx cypress run

# ブラウザのコンソールログ表示
npx cypress run --browser chrome --headed

# スクリーンショット確認
# テスト失敗時に自動でスクリーンショット保存される
```

### CI/CD連携（Cypress公式推奨パターン）
```yaml
# GitHub Actions 例
- name: Run E2E Tests
  run: |
    docker compose up -d frontend backend db
    docker compose --profile test run --rm cypress --config video=false
    docker compose down
```

対応CI/CDツール：
- GitHub Actions
- GitLab CI
- Jenkins
- その他のCI/CDツール

### プロファイル使用のメリット
- **公式推奨**: Cypressの run-and-exit 哲学に準拠
- **効率的**: テスト時のみリソース使用
- **明確**: テスト実行意図が明確
- **自動化対応**: CI/CDパイプラインに最適

### パフォーマンス最適化
- ビデオ録画無効で高速化
- 必要最小限のviewport設定
- テスト並列実行の検討（`--parallel`オプション）