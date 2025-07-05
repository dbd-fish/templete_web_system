# CLAUDE.md - バックエンド開発ガイド

このファイルは、FastAPI + PostgreSQL バックエンドの開発に関する包括的な情報を提供します。
日本語で回答してください。
また提供するコーディングはRuffやmypyに準拠したコーディングを提供してください。

## 🏗️ プロジェクト概要

FastAPI + PostgreSQL を使用した高性能RESTful APIバックエンドです。

### 基本技術スタック
- **フレームワーク**: FastAPI 0.115.5 + uvicorn
- **データベース**: PostgreSQL 13（非同期接続）
- **ORM**: SQLAlchemy 2.0（非同期モード）
- **言語**: Python 3.13
- **依存関係管理**: Poetry（package-mode = false）
- **開発ポート**: 8000

## 📁 ディレクトリ構成

```
backend/
├── Dockerfile                   # バックエンドコンテナ設定
├── main.py                      # FastAPI アプリケーションエントリーポイント
├── pyproject.toml               # Poetry 設定（package-mode = false）
├── poetry.lock                  # 依存関係ロックファイル
├── alembic.ini                  # データベースマイグレーション設定
├── alembic/                     # Alembic マイグレーション
│   ├── env.py                   # Alembic 環境設定
│   ├── script.py.mako           # マイグレーションテンプレート
│   └── versions/                # マイグレーションファイル
├── api/                         # メインアプリケーション
│   ├── common/                  # 共通機能
│   │   ├── core/                # コア機能
│   │   │   ├── log_config.py    # ログ設定（structlog + rich）
│   │   │   ├── http_exception_handler.py
│   │   │   └── request_validation_error.py
│   │   ├── middleware/          # カスタムミドルウェア
│   │   │   ├── add_userIP_middleware.py
│   │   │   └── error_handler_middleware.py
│   │   ├── database.py          # データベース接続設定
│   │   ├── setting.py           # 設定管理（Pydantic BaseSettings）
│   │   ├── exception_handlers.py # 統一エラーハンドリング
│   │   ├── response_schemas.py  # レスポンス統一スキーマ
│   │   └── test_data.py         # テストデータ生成
│   ├── v1/                      # API v1
│   │   └── features/            # 機能別モジュール
│   │       ├── feature_auth/    # 認証機能
│   │       │   ├── models/      # データモデル
│   │       │   ├── schemas/     # Pydantic スキーマ
│   │       │   ├── crud.py      # CRUD 操作
│   │       │   ├── route.py     # API エンドポイント
│   │       │   ├── security.py  # セキュリティ機能
│   │       │   ├── send_verification_email.py
│   │       │   └── send_reset_password_email.py
│   │       └── feature_dev/     # 開発用機能
│   │           ├── route.py     # 開発API
│   │           ├── seed_data.py # シードデータ
│   │           └── seed_user.py # ユーザーシードデータ
│   └── tests/                   # テストコード
│       ├── conftest.py          # pytest 設定
│       ├── fixtures/            # テストフィクスチャ
│       └── v1/features/         # 機能別テスト
├── logs/                        # ログファイル（日付別）
├── certs/                       # SSL証明書（必要に応じて）
└── CLAUDE.md                    # このファイル
```

## 🚀 開発コマンド

### Docker環境での開発
```bash
# バックエンド + データベース起動
docker compose up -d backend db

# バックエンドコンテナ再ビルド
docker compose build backend

# コンテナ内でシェルアクセス
docker exec -it backend_container bash

# ログ確認
docker logs backend_container
docker logs postgres_db
```

### Poetry（コンテナ内）
```bash
# 依存関係インストール
poetry install --no-root

# 開発サーバー起動（ホットリロード）
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# アプリケーション情報確認
poetry show
poetry --version
```

### テスト実行
```bash
# 全テスト実行（35テストケース）
poetry run pytest

# カバレッジ付きテスト実行
poetry run pytest --cov=api --cov-report=term-missing

# 詳細出力でテスト実行
poetry run pytest -v

# 特定のテストファイル実行
poetry run pytest api/tests/v1/features/feature_auth/test_auth_controller.py
```

### コード品質ツール
```bash
# リンティング実行
poetry run ruff check .

# 自動修正付きリンティング
poetry run ruff check . --fix

# コードフォーマット
poetry run ruff format .

# 型チェック実行（43ファイル対象）
poetry run mypy .
```

### データベースマイグレーション
```bash
# マイグレーションファイル生成
poetry run alembic revision --autogenerate -m "メッセージ"

# マイグレーション実行
poetry run alembic upgrade head

# マイグレーション履歴確認
poetry run alembic history

# 現在のリビジョン確認
poetry run alembic current
```

## 🔧 技術仕様詳細

### 主要依存関係
```toml
# Web フレームワーク
fastapi = {extras = ["all"], version = "^0.115.5"}
uvicorn = {extras = ["standard"], version = "^0.32.0"}

# データベース（非同期）
sqlalchemy = "^2.0.36"
asyncpg = "^0.30.0"
alembic = "^1.14.0"
databases = "^0.9.0"

# 認証・セキュリティ
pyjwt = {extras = ["crypto"], version = "^2.8.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
bcrypt = "==4.0.1"

# 設定管理
pydantic-settings = "^2.6.1"

# ログ・監視
structlog = "^24.4.0"
rich = "^13.9.4"

# 開発・テスト
pytest = "^8.3.3"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.27.2"  # テスト用非同期HTTPクライアント

# コード品質
ruff = "^0.7.2"
mypy = "^1.13.0"
```

### データベース設定
```python
# 接続情報
DATABASE_URL = "postgresql://template_user:template_password@db:5432/template_db"

# 環境変数（docker-compose.yml 設定済み）
POSTGRES_DB = "template_db"
POSTGRES_USER = "template_user"
POSTGRES_PASSWORD = "template_password"
TZ = "Asia/Tokyo"
```

### ログ設定
- **ライブラリ**: structlog + rich
- **出力先**: `logs/server/app/app_YYYY-MM-DD.log`
- **SQL ログ**: `logs/server/sql/sqlalchemy_YYYY-MM-DD.log`
- **コンソール出力**: 開発時のみ有効

## 📚 API ドキュメント

### 自動生成ドキュメント
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### API エンドポイント

#### 🔐 認証API（v1）
```
POST /api/v1/auth/signup              # ユーザー登録（トークン認証）
POST /api/v1/auth/send-verify-email   # 仮登録メール送信
POST /api/v1/auth/login               # ログイン処理
POST /api/v1/auth/logout              # ログアウト処理
POST /api/v1/auth/send-password-reset-email  # パスワードリセットメール
POST /api/v1/auth/reset-password      # パスワードリセット
PATCH /api/v1/auth/update-user-info   # ユーザー情報更新
```

#### 🛠️ 開発API（v1・開発環境のみ）
```
POST /api/v1/dev/clear_data           # 全テーブル削除・再作成
POST /api/v1/dev/seed_data            # テストデータ挿入
POST /api/v1/dev/reset_password_test  # パスワードリセットテスト
GET  /api/v1/dev/health               # 基本ヘルスチェック
GET  /api/v1/dev/health_db            # データベース接続確認
```

### レスポンス形式

#### 成功レスポンス
```json
{
  "success": true,
  "message": "操作が正常に完了しました",
  "data": { ... },
  "timestamp": "2025-07-05T12:00:00Z"
}
```

#### エラーレスポンス
```json
{
  "success": false,
  "message": "エラーの説明",
  "error_code": "VALIDATION_ERROR",
  "details": { ... },
  "timestamp": "2025-07-05T12:00:00Z"
}
```

## 🧪 テスト構成

### テスト統計
- **総テストケース数**: 35件
- **カバレッジ**: 78%
- **テスト実行時間**: 約13秒

### テスト分類
```
api/tests/v1/features/feature_auth/
├── test_auth_controller.py          # 認証API統合テスト（20件）
└── unit/
    ├── test_email_sending.py        # メール送信単体テスト（6件）
    └── test_security.py             # セキュリティ単体テスト（9件）
```

### テストフィクスチャ
```python
# api/tests/fixtures/
authenticate_fixture.py    # 認証済みクライアント
db_fixture.py             # データベーステスト環境
mock_email_fixture.py     # メール送信モック
logging_fixture.py       # ログ設定
```

### テスト実行環境
- **データベース**: PostgreSQL（実際のDB使用）
- **メール送信**: モック化（ENABLE_EMAIL_SENDING=false）
- **ログ出力**: テスト専用ディレクトリ

## 🔒 セキュリティ機能

### 認証方式
- **JWT トークン**: HS256 アルゴリズム
- **クッキー認証**: HttpOnly, Secure, SameSite=lax
- **トークン有効期限**: 240分（4時間）

### パスワード処理
- **ハッシュ化**: bcrypt（ソルト付き）
- **強度チェック**: パスワード複雑性要求
- **リセット機能**: トークンベースのリセット

### データベースセキュリティ
- **SQLインジェクション対策**: SQLAlchemy パラメータ化クエリ
- **論理削除**: 物理削除ではなく deleted_at フラグ使用
- **データ復旧**: 論理削除されたデータの復元機能

## 🌐 CORS設定

```python
origins = [
    "http://localhost:3000",     # フロントエンド本番用
    "http://localhost:5173",     # フロントエンド開発用（Vite）
    "http://frontend:5173",      # コンテナ間通信
]
```

## 🔧 開発ツール設定

### Ruff設定（pyproject.toml）
```toml
[tool.ruff]
line-length = 200                    # 行長制限
target-version = "py313"             # Python 3.13対応
lint.select = ["F", "E", "W", "I", "B", "UP"]  # 適用ルール

# 除外パス
exclude = [
    "**/migrations/**",
    "**/__pycache__/**",
    "alembic/versions/**"
]
```

### pytest設定
```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"              # 非同期テスト厳密モード
asyncio_default_fixture_loop_scope = "session"
```

### MyPy設定
- **チェック対象**: 43ファイル
- **型チェック**: strict モード
- **除外**: alembic/versions/

## 🐳 Docker構成

### コンテナ情報
- **ベースイメージ**: python:3.13
- **作業ディレクトリ**: /app/backend
- **ポート**: 8000
- **ボリューム**: ホットリロード対応

### コンテナ間通信
```
frontend_container → backend_container:8000
backend_container → postgres_db:5432
```

### 環境変数
```bash
DATABASE_URL="postgresql://template_user:template_password@db:5432/template_db"
PYTEST_MODE=false
ENABLE_EMAIL_SENDING=false
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. データベース接続エラー
```bash
# PostgreSQL の起動確認
docker compose logs db
docker exec postgres_db pg_isready -U template_user

# 解決方法
docker compose down
docker compose up -d db backend
```

#### 2. 依存関係の問題
```bash
# poetry.lock の問題
docker exec backend_container poetry lock
docker exec backend_container poetry install --no-root

# コンテナ再ビルド
docker compose build backend --no-cache
```

#### 3. マイグレーションエラー
```bash
# 現在のリビジョン確認
poetry run alembic current

# データベースリセット
poetry run alembic downgrade base
poetry run alembic upgrade head
```

#### 4. テスト失敗
```bash
# 詳細ログでテスト実行
poetry run pytest -v --tb=short

# カバレッジで問題箇所特定
poetry run pytest --cov=api --cov-report=html
```

#### 5. ログの確認
```bash
# アプリケーションログ
tail -f backend/logs/server/app/app_$(date +%Y-%m-%d).log

# SQLログ
tail -f backend/logs/server/sql/sqlalchemy_$(date +%Y-%m-%d).log
```

### パフォーマンス最適化

#### データベース
- **接続プール**: SQLAlchemy の非同期接続プール使用
- **インデックス**: 適切なデータベースインデックス設計
- **クエリ最適化**: N+1問題の回避

#### アプリケーション
- **非同期処理**: uvicorn + asyncio の活用
- **レスポンス圧縮**: gzip 圧縮有効化
- **キャッシュ**: 必要に応じてRedis導入検討

## 📈 CI/CD対応

### GitHub Actions
- **テスト自動実行**: 35テストケース
- **コード品質チェック**: Ruff + MyPy
- **カバレッジレポート**: pytest-cov
- **依存関係管理**: Poetry + package-mode = false

### デプロイ準備
- **Docker対応**: マルチステージビルド対応
- **環境分離**: 開発・ステージング・本番環境対応
- **ヘルスチェック**: /api/v1/dev/health エンドポイント

## 📝 開発における注意事項

### SQLAlchemy 2.0
- **非同期セッション**: `AsyncSession` 必須
- **await構文**: データベース操作時は `await` 必須
- **select構文**: 新しい `select()` 構文を使用

### Poetry設定
- **package-mode = false**: アプリケーション開発モード
- **--no-root**: プロジェクトパッケージはインストールしない

### コード品質
- **行長制限**: 200文字
- **型ヒント**: MyPy での型チェック必須
- **テストカバレッジ**: 78%以上を維持

この構成により、高品質で保守性の高いFastAPIバックエンドアプリケーションの開発が可能です。