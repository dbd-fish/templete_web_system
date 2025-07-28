# CLAUDE.md - Cypress E2E テスト

このファイルは、CypressコンテナでのE2Eテストのセットアップと実行に関する情報を提供します。
日本語で回答してください。

## Cypress E2E テスト概要
注意：Cypressテスト未完成！！


Cypress 13.17.0を使用したエンドツーエンドテスト環境です。
- **テストフレームワーク**: Cypress 13.17.0
- **実行環境**: cypress/included Dockerイメージ
- **ベースイメージ**: ヘッドレスブラウザ対応
- **テスト対象**: フロントエンド（React Router + Vite）
- **接続方式**: 実際のAPIテスト（モックAPI削除済み）
- **テスト方針**: 画面操作中心のE2Eテスト（API直接呼び出し禁止）

## ディレクトリ構成

```
cypress/
├── Dockerfile                   # Cypressコンテナ設定
├── cypress.config.js            # Cypress設定ファイル
├── run-tests.sh                 # テスト実行スクリプト
├── cypress/                     # Cypressテストファイル
│   ├── e2e/                     # E2Eテスト
│   │   ├── auth/                # 認証機能の基本動作テスト（API単位）
│   │   │   ├── login.cy.js          # ログイン機能基本テスト
│   │   │   └── token-refresh.cy.js  # トークンリフレッシュ基本テスト
│   │   └── user-scenarios/          # 顧客操作シナリオベースE2Eテスト
│   │       ├── user-journey.cy.js         # ユーザージャーニー全体テスト
│   │       ├── authentication-flow.cy.js  # 認証フロー顧客シナリオ
│   │       └── error-recovery.cy.js       # エラー対応・復旧シナリオ
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
docker compose up -d frontend backend db

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
├── e2e/                         # E2Eテスト
│   ├── auth/                    # 認証機能の基本動作テスト（API単位）
│   │   ├── login.cy.js          # ログイン機能基本テスト
│   │   └── token-refresh.cy.js  # トークンリフレッシュ基本テスト
│   └── user-scenarios/          # 顧客操作シナリオベースE2Eテスト
│       ├── user-journey.cy.js         # ユーザージャーニー全体テスト
│       ├── authentication-flow.cy.js  # 認証フロー顧客シナリオ
│       └── error-recovery.cy.js       # エラー対応・復旧シナリオ
└── front_st/                    # 画面単位テスト（将来拡張用）
    └── **/*.cy.js
```

### テストの種類と目的（2025-01-27更新）
- **auth/**: 個別機能の基本動作確認（画面操作ベースの動作テスト）
- **user-scenarios/**: 顧客の実際の操作シナリオをベースとしたE2Eテスト
  - ユーザージャーニー、認証フロー、エラー復旧など実際の顧客体験を重視
- **画面操作によるテスト**: APIの直接呼び出しではなく、ユーザーの実際の操作をテスト
- **実際のAPIとの統合**: フロントエンド操作を通じて実際のバックエンドAPIをテスト

### カスタムコマンド（2025-07-28更新）
事前定義されたカスタムコマンド：
- **login.js**: 画面操作によるログイン処理の自動化（APIの直接呼び出し禁止）
- **logout.js**: 画面操作によるログアウト処理の自動化
- **errorHandling.js**: エラーハンドリング

使用例：
```javascript
// ログインコマンド使用（画面操作版のみ）
cy.login('targetuser@example.com', 'Password123456+-')  // フォーム入力からログインボタンクリックまで

// フォーム経由ログインコマンド（推奨）
cy.loginViaForm('targetuser@example.com', 'Password123456+-')

// 管理者ログイン
cy.loginAsAdmin()  // admin@example.com でログイン

// 一般ユーザーログイン 
cy.loginAsUser()   // targetuser@example.com でログイン

// ログアウトコマンド使用（画面操作版）
cy.logout()  // ユーザーメニューからログアウトボタンクリックまで
```

### 利用可能なテストアカウント
```javascript
// 一般ユーザー
email: 'targetuser@example.com'
password: 'Password123456+-'
role: 2 (無料会員)

// 管理者ユーザー
email: 'admin@example.com' 
password: 'adminpassword'
role: 4 (管理者)
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
- **API接続**: 実際のバックエンドAPI（`http://backend:8000`）を使用

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

### API接続（2025-01-27更新）
- **統合テスト**: フロントエンド ↔ バックエンド ↔ データベースの完全な統合テスト
- **認証テスト**: 実際のJWTトークン、Cookieを使用した認証フロー
- **画面操作中心**: APIの直接呼び出しではなく、実際のユーザー操作をシミュレート

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

4. **API接続エラー**:
   - バックエンドサービスが正常に起動しているか確認
   - `docker compose logs backend` でバックエンドログ確認
   - データベース接続確認: `docker compose logs db`

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

## E2Eテスト戦略（2025-01-27更新）

### 顧客シナリオベーステスト
1. **user-journey.cy.js**:
   - 新規ユーザーの初回訪問から会員登録、ログイン、主要機能利用まで
   - 実際の顧客体験に沿ったフルジャーニーテスト

2. **authentication-flow.cy.js**:
   - ログイン・ログアウト・パスワードリセットのフローテスト
   - トークンリフレッシュ、セッション管理のテスト

3. **error-recovery.cy.js**:
   - ネットワークエラー、サーバーエラー時の復旧シナリオ
   - ユーザーが困った時の対処法テスト

### 実際のAPIとの統合
- **JWT認証**: 実際のトークン生成・検証
- **Cookie管理**: HttpOnlyクッキーの実際の動作確認
- **データベース**: 実際のPostgreSQLとの連携テスト
- **エラーハンドリング**: 実際のAPIエラーレスポンス確認

## 最新の改善点（2025-07-28）

### data-cy属性による要素特定の最適化
1. **data-cy属性の統一実装**: 全主要コンポーネントにテスト用の要素識別子を追加
2. **安定したテスト実行**: CSSクラスやIDに依存しない安定した要素選択
3. **保守性向上**: UI変更に影響されにくい堅牢なテスト設計
4. **テスト可読性**: 明確な意図を持つ要素識別が可能

### 実装済みdata-cy属性一覧

#### ログイン・認証関連
```javascript
// ログインページ
'[data-cy="login-title"]'          // ログインページタイトル
'[data-cy="login-form"]'           // ログインフォーム
'[data-cy="email-input"]'          // メールアドレス入力
'[data-cy="password-input"]'       // パスワード入力
'[data-cy="login-submit-button"]'  // ログインボタン
'[data-cy="google-login-button"]'  // Googleログインボタン
'[data-cy="forgot-password-link"]' // パスワード忘れリンク
'[data-cy="signup-link"]'          // 新規登録リンク

// サインアップページ
'[data-cy="signup-title"]'              // サインアップページタイトル
'[data-cy="signup-form"]'               // サインアップフォーム
'[data-cy="signup-username-input"]'     // ユーザー名入力
'[data-cy="signup-email-input"]'        // メールアドレス入力
'[data-cy="signup-password-input"]'     // パスワード入力
'[data-cy="signup-confirm-password-input"]' // パスワード確認入力
'[data-cy="signup-submit-button"]'      // 登録ボタン
'[data-cy="signup-login-link"]'         // ログインページリンク

// パスワードリセット
'[data-cy="reset-password-form"]'       // リセット申請フォーム
'[data-cy="reset-email-input"]'         // メール入力
'[data-cy="reset-submit-button"]'       // 送信ボタン
'[data-cy="new-password-form"]'         // 新パスワードフォーム
'[data-cy="new-password-input"]'        // 新パスワード入力
'[data-cy="confirm-new-password-input"]' // 新パスワード確認入力
'[data-cy="new-password-submit-button"]' // パスワード更新ボタン
```

#### マイページ・ユーザー管理
```javascript
// 一般ユーザーマイページ
'[data-cy="mypage-title"]'          // マイページタイトル
'[data-cy="user-profile"]'          // ユーザープロフィール
'[data-cy="user-menu"]'             // ユーザーメニュー
'[data-cy="logout-form-button"]'    // ログアウトボタン（フォーム）
'[data-cy="delete-account-button"]' // アカウント削除ボタン
'[data-cy="upgrade-button"]'        // アップグレードボタン

// 管理者マイページ
'[data-cy="admin-mypage-title"]'      // 管理者ページタイトル
'[data-cy="user-management-toggle"]'  // ユーザー管理パネル切替
'[data-cy="user-management-panel"]'   // ユーザー管理パネル
'[data-cy="users-table"]'             // ユーザー一覧テーブル
'[data-cy="edit-user-button"]'        // ユーザー編集ボタン
'[data-cy="delete-user-button"]'      // ユーザー削除ボタン
'[data-cy="restore-user-button"]'     // ユーザー復活ボタン
'[data-cy="admin-account-management"]' // 管理者アカウント管理
'[data-cy="admin-logout-button"]'     // 管理者ログアウトボタン
```

#### ヘッダー・ナビゲーション
```javascript
// ログイン後ヘッダー
'[data-cy="user-menu-button"]'     // ユーザーメニューボタン
'[data-cy="user-avatar"]'          // ユーザーアバター
'[data-cy="logout-button"]'        // ログアウトボタン（ヘッダー）
'[data-cy="mypage-link"]'          // マイページリンク
'[data-cy="home-link"]'            // ホームリンク
'[data-cy="settings-link"]'        // 設定リンク
```

#### ホームページ
```javascript
'[data-cy="main-content"]'     // メインコンテンツエリア
'[data-cy="home-title"]'       // ホームページタイトル
'[data-cy="home-description"]' // ホームページ説明
```

### 画面操作中心のテスト設計
1. **ユーザー体験重視**: API直接呼び出しではなく実際のユーザー操作をシミュレート
2. **真のE2Eテスト**: フロントエンド操作 → バックエンドAPI → データベースの完全なフロー
3. **実際の動作確認**: 画面からの操作で発見できるUIとAPIの統合問題を検出
4. **保守性向上**: APIの内部仕様変更に影響されにくいテスト設計

### テスト設計の改善
- **画面操作コマンド**: `cy.login()`, `cy.logout()`は全て画面操作ベース
- **エンドツーエンド**: フォーム入力 → ボタンクリック → レスポンス → 画面遷移の完全フロー
- **ユーザー中心**: 顧客が実際に行う操作パターンに基づくテストケース
- **統合品質**: フロントエンド・バックエンド・データベースの真の統合テスト

### 現在のテスト状況（2025-07-28）
- **実装完了**: 主要コンポーネントのdata-cy属性追加
- **テスト成功率**: login.cy.js で12テスト中4つが合格
- **基本機能**: ページ表示、フォーム要素、Google認証ボタンは正常動作
- **課題**: 実際のAPIログイン処理で8テストが失敗（継続調査中）

### E2Eテストの価値向上
- **顧客視点**: 実際のユーザー体験をテスト
- **品質向上**: 画面操作レベルでの品質保証
- **回帰防止**: UI変更時の既存機能影響確認
- **信頼性向上**: 実際のユーザー操作での動作保証