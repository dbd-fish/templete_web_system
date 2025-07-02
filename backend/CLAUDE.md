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

## ディレクトリ構成

```
backend/
├── Dockerfile                   # バックエンドコンテナ設定
├── main.py                      # FastAPIアプリケーションエントリーポイント
├── pyproject.toml               # Poetry設定（依存関係・ツール設定）
├── poetry.lock                  # 依存関係ロックファイル
├── alembic.ini                  # Alembicマイグレーション設定
├── alembic/                     # データベースマイグレーション
├── app/                         # メインアプリケーション
│   ├── core/                    # コア機能（設定、セキュリティ等）
│   ├── models/                  # SQLAlchemyモデル
│   ├── schemas/                 # Pydanticスキーマ
│   ├── api/                     # APIエンドポイント
│   ├── crud/                    # CRUD操作
│   ├── services/                # ビジネスロジック
│   └── utils/                   # ユーティリティ関数
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