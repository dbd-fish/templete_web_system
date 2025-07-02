# CLAUDE.md - バックエンド

このファイルは、バックエンドコンテナ（FastAPI + PostgreSQL）のセットアップと開発に関する情報を提供します。
日本語で回答してください。

## バックエンド概要

FastAPI + PostgreSQLを使用したRESTful APIバックエンド環境です。
- **フレームワーク**: FastAPI + uvicorn
- **データベース**: PostgreSQL 13（別コンテナ）
- **ORM**: SQLAlchemy 2.0（非同期）
- **言語**: Python 3.13
- **依存関係管理**: Poetry
- **開発ポート**: 8000

## ディレクトリ構成（段階的移行中）

```
backend/
├── Dockerfile                   # バックエンドコンテナ設定
├── main.py                      # FastAPIアプリケーションエントリーポイント
├── pyproject.toml               # Poetry設定（依存関係・ツール設定）
├── poetry.lock                  # 依存関係ロックファイル
├── alembic.ini                  # Alembicマイグレーション設定
├── alembic/                     # データベースマイグレーション
├── app/                         # メインアプリケーション
│   ├── api/                     # APIバージョニング
│   │   ├── deps.py              # 共通の依存性注入（段階的移行版）
│   │   └── v1/                  # API v1
│   │       ├── routes.py        # v1ルーター統合
│   │       ├── routes/          # v1エンドポイント（FastAPI公式準拠）
│   │       │   ├── auth.py      # 認証API
│   │       │   ├── users.py     # ユーザー管理API
│   │       │   ├── dev.py       # 開発API
│   │       │   └── health.py    # ヘルスチェックAPI
│   │       └── features/        # フィーチャー機能（移動済み）
│   │           ├── feature_auth/ # 認証機能
│   │           └── feature_dev/ # 開発用機能
│   ├── core/                    # 【NEW】FastAPI公式パターン準拠
│   │   ├── config.py            # 統一設定管理（Pydantic BaseSettings）
│   │   ├── db.py                # データベース設定（将来使用予定）
│   │   ├── security.py          # セキュリティ機能集約
│   │   └── compat.py            # 既存コードとの互換性維持
│   ├── common/                  # 【LEGACY】段階的に移行予定
│   │   ├── core/                # コア機能（ログ、エラーハンドリング）
│   │   ├── middleware/          # カスタムミドルウェア
│   │   ├── database.py          # データベース設定（現在使用中）
│   │   └── setting.py           # 設定管理（core/compatを使用）
│   ├── models.py                # 【NEW】SQLModel統合モデル
│   ├── crud.py                  # 【NEW】CRUD操作集約
│   ├── models/                  # SQLAlchemyモデル（将来SQLModelに移行）
│   └── routes.py                # 旧ルーティング（後方互換）
├── tests/                       # テストファイル
├── logs/                        # ログファイル
└── CLAUDE.md                    # このファイル
```

## 開発コマンド

### Docker環境での開発
```bash
# バックエンドコンテナ起動（データベース含む）
docker compose up backend db

# バックエンドコンテナ再ビルド
docker compose build backend

# コンテナ内でシェルアクセス
docker exec -it backend_container bash
```

### Poetry（コンテナ内）
```bash
# 依存関係インストール
poetry install

# 開発環境での起動（自動リロード）
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# テスト実行
poetry run pytest

# 非同期テスト実行
poetry run pytest --asyncio-mode=strict
```

### コード品質ツール
```bash
# リンティング実行
poetry run ruff check

# コードフォーマット
poetry run ruff format

# 型チェック実行
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
```

## 技術スタック詳細

### 主要な依存関係
- **FastAPI**: 高性能なWebAPIフレームワーク
- **uvicorn**: ASGIサーバー
- **SQLAlchemy 2.0**: 非同期ORM
- **asyncpg**: PostgreSQL非同期ドライバー
- **Alembic**: データベースマイグレーション
- **Pydantic**: データバリデーション

### 認証・セキュリティ
- **python-jose**: JWT トークン処理
- **passlib**: パスワードハッシュ化
- **bcrypt**: 暗号化

### 開発ツール
- **Ruff**: 高速リンティング・フォーマット（行長200設定）
- **MyPy**: 静的型チェック
- **pytest**: テストフレームワーク（非同期サポート）
- **structlog**: 構造化ログ出力

## データベース設定

### 接続情報
```python
DATABASE_URL = "postgresql://template_user:template_password@db:5432/template_db"
```

### 環境変数（docker-compose.yml設定済み）
- `POSTGRES_DB`: template_db
- `POSTGRES_USER`: template_user  
- `POSTGRES_PASSWORD`: template_password
- `TZ`: Asia/Tokyo

## APIドキュメント

FastAPIの自動生成ドキュメント：
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### API エンドポイント

#### 認証API（v1） 🟢 推奨
- `POST /api/v1/auth/signup` - ユーザー登録（トークン認証）
- `POST /api/v1/auth/send-verify-email` - 仮登録メール送信
- `POST /api/v1/auth/login` - ログイン処理
- `POST /api/v1/auth/logout` - ログアウト処理
- `POST /api/v1/auth/send-password-reset-email` - パスワードリセットメール送信
- `POST /api/v1/auth/reset-password` - パスワードリセット

#### ユーザー管理API（v1） 🆕 NEW
- `GET /api/v1/users/me` - 現在のユーザー情報取得
- `PATCH /api/v1/users/me` - ユーザー情報更新
- `DELETE /api/v1/users/me` - ユーザーアカウント削除

#### ヘルスチェックAPI（v1） 🆕 NEW
- `GET /api/v1/health/` - 基本ヘルスチェック
- `GET /api/v1/health/db` - データベース接続確認

#### 開発API（v1・開発環境のみ） 🟢 推奨
- `POST /api/v1/dev/clear_data` - 全テーブル削除・再作成
- `POST /api/v1/dev/seed_data` - テストデータ挿入

#### 後方互換API 🚨 非推奨
- `/api/auth/*` - v1移行により非推奨（段階的削除予定）
- `/api/dev/*` - v1移行により非推奨（段階的削除予定）

## アーキテクチャ移行状況

### 🟢 完了済み（Phase 1-4）
- **APIバージョニング**: `/api/v1/` 構造の導入
- **コア設定の統一**: `app/core/config.py` でPydantic BaseSettings使用
- **SQLModel導入**: `app/models.py` でSQLAlchemy + Pydantic統合
- **CRUD層集約**: `app/crud.py` で関数ベースのCRUD操作
- **API構造最適化**: 機能別ルート分離（auth, users, dev, health）
- **後方互換性**: 既存コードの動作を維持しながら段階的移行

### 🟡 進行中（Phase 5）
- **Legacy code整理**: 非推奨マーキングと段階的削除
- **型安全な依存性注入**: `SessionDep`, `CurrentUser`エイリアス使用

### 🔴 将来の予定
- **完全なLegacy削除**: 移行期間完了後
- **パフォーマンス最適化**: データベースクエリとキャッシング
- **テストカバレッジ拡張**: SQLModelベースのテスト

### 新しいAPI構造
```
/api/v1/auth/*     # 認証API（推奨）
/api/v1/users/*    # ユーザー管理API（NEW）
/api/v1/health/*   # ヘルスチェックAPI（NEW）
/api/v1/dev/*      # 開発用API（推奨）

/api/auth/*        # 🚨 非推奨（後方互換）
/api/dev/*         # 🚨 非推奨（後方互換）
```

### 移行方針
FastAPI公式テンプレートに準拠した段階的移行を**完了**。既存のフィーチャードリブン設計と公式推奨パターンのハイブリッド構成を実現。

## 開発時の注意点

### SQLAlchemy 2.0
- 非同期セッション（AsyncSession）を使用
- `await` キーワードが必要なデータベース操作
- `select()` 構文の使用

### ログ設定
- structlog + rich formattingで構造化ログ
- ログファイルは `logs/` ディレクトリに出力

### CORS設定
フロントエンドからのアクセスを許可：
```python
origins = [
    "http://localhost:3000",  # フロントエンド本番用
    "http://localhost:5173",  # フロントエンド開発用
    "http://frontend:5173",   # コンテナ間通信
]
```

### コンテナ間通信
- フロントエンド → バックエンド: `http://backend:8000`
- バックエンド → データベース: `postgresql://db:5432`

## テスト

### テスト構成
- **pytest**: 基本テストフレームワーク
- **pytest-asyncio**: 非同期テスト対応
- **httpx**: 非同期HTTPクライアント（テスト用）

### テスト実行
```bash
# 全テスト実行
poetry run pytest

# 詳細出力
poetry run pytest -v

# カバレッジ付き実行
poetry run pytest --cov=app
```

## トラブルシューティング

### よくある問題
1. **データベース接続エラー**:
   - PostgreSQLコンテナが起動していることを確認
   - `docker compose logs db` でデータベースログ確認

2. **依存関係の問題**:
   - `poetry install` で依存関係再インストール
   - `poetry.lock` が最新かどうか確認

3. **マイグレーションエラー**:
   - `alembic current` で現在のリビジョン確認
   - データベーススキーマとモデルの整合性確認

### パフォーマンス
- SQLAlchemy非同期セッションでコネクションプール利用
- uvicornワーカー数は本番環境で調整
- データベースインデックス設計を考慮

### セキュリティ
- JWT SECRET_KEYは本番環境で必ず変更
- パスワードは必ずbcryptでハッシュ化
- SQLインジェクション対策としてSQLAlchemyのパラメータ化クエリ使用