# CLAUDE.md - Webシステム開発テンプレート

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
日本語で回答してください。

機能開発の指示がある場合は下記ドキュメントに準拠してください
- PM役の場合→claude\claude-tmux_pm.md
- メンバー役の場合→claude\claude-tmux_member.md

## プロジェクト概要

これはDockerベースのWebシステム開発テンプレートで、従来型のアプリ直下Dockerfile配置を採用しています。
フロントエンド（React Router + Vite）、バックエンド（FastAPI + PostgreSQL）、E2Eテスト（Cypress）を統合管理します。

## ディレクトリ構成

```
templete_web_system/
├── docker-compose.yml          # マルチコンテナオーケストレーション
├── frontend/                   # React Router v7 + Vite アプリケーション
│   ├── Dockerfile             # フロントエンド用Dockerfile
│   ├── CLAUDE.md              # フロントエンド開発ガイド
│   ├── package.json           # Node.js依存関係
│   ├── vite.config.ts         # Vite設定
│   ├── app/                   # Reactアプリケーション
│   └── public/                # 静的ファイル
├── backend/                    # FastAPI + PostgreSQL アプリケーション
│   ├── Dockerfile             # バックエンド用Dockerfile
│   ├── CLAUDE.md              # バックエンド開発ガイド
│   ├── pyproject.toml         # Python依存関係（Poetry）
│   ├── main.py                # FastAPIエントリーポイント
│   ├── api/                   # アプリケーションロジック
│   ├── alembic/               # データベースマイグレーション
│   └── tests/                 # バックエンドテスト
├── cypress/                    # Cypress E2Eテスト
│   ├── Dockerfile             # Cypress用Dockerfile
│   ├── CLAUDE.md              # Cypressテスト開発ガイド
│   ├── cypress.config.js      # Cypress設定
│   ├── run-tests.sh           # テスト実行スクリプト
│   └── cypress/               # テストファイル
├── init-scripts/              # データベース初期化スクリプト
├── docs/                      # プロジェクトドキュメント（空）
├── scripts/                   # 開発・デプロイスクリプト（空）
├── claude/                    # Claude関連ドキュメント
│   └── temp_doc/              # 設計ドキュメント
│       └── 基本設計/
│           └── 認証・認可システム仕様書.md
└── CLAUDE.md                  # このファイル（プロジェクト全体）
```

## アプリ直下Dockerfile配置の利点

- **直感的理解**: アプリケーションコードとDockerfileが物理的に近接
- **開発者体験**: 各アプリの担当者がDockerfileを見つけやすい
- **マイクロサービス対応**: 各サービスの独立性が高い
- **標準的手法**: Netflix、Uber等多くの企業で採用される構成

## クイックスタートガイド

### 新規開発者向け初期セットアップ
```bash
# 1. リポジトリクローン後の初期セットアップ
git clone <repository-url>
cd templete_web_system

# 2. Docker環境構築・初回ビルド
docker compose build

# 3. 基本サービス起動
docker compose up -d frontend backend db

# 4. 動作確認
# フロントエンド: http://localhost:5173 (dev) / http://localhost:3000 (prod)
# バックエンドAPI: http://localhost:8000/docs
# データベース: localhost:5432
```

### 日常開発コマンド

#### Docker環境管理
```bash
# 基本サービス起動（最も使用頻度が高い）
docker compose up -d frontend backend db

# 開発用ログ確認（リアルタイム）
docker compose logs -f frontend backend

# コンテナ再ビルド（依存関係更新時）
docker compose build

# 全サービス停止・クリーンアップ
docker compose down -v
```

#### 開発・テストコマンド
```bash
# フロントエンド開発
docker compose exec frontend npm run dev          # 開発サーバー起動
docker compose exec frontend npm run typecheck    # 型チェック
docker compose exec frontend npm run lint         # リント実行
docker compose exec frontend npm run format       # フォーマット

# バックエンド開発
docker compose exec backend poetry run pytest            # テスト実行
docker compose exec backend poetry run pytest --cov     # カバレッジ付きテスト
docker compose exec backend poetry run ruff check .     # リント実行
docker compose exec backend poetry run mypy .           # 型チェック

# データベースマイグレーション
docker compose exec backend poetry run alembic upgrade head
docker compose exec backend poetry run alembic revision --autogenerate -m "変更内容"

# E2Eテスト実行（事前にサービス起動が必要）
docker compose --profile test run --rm cypress
```

### 各アプリケーションの詳細

各アプリケーションの詳細な開発情報は、それぞれのCLAUDE.mdを参照してください：

- **[frontend/CLAUDE.md](./frontend/CLAUDE.md)**: React Router v7 + Vite フロントエンド
- **[backend/CLAUDE.md](./backend/CLAUDE.md)**: FastAPI + PostgreSQL バックエンド  
- **[cypress/CLAUDE.md](./cypress/CLAUDE.md)**: Cypress E2Eテスト

## アーキテクチャ概要

### コンテナ構成
- **フロントエンド**: React Router v7 + Vite（ポート3000/5173、HTTP/HTTPS対応）
- **バックエンド**: FastAPI + uvicorn（ポート8000、structlogログ）
- **データベース**: PostgreSQL 13（ポート5432）
- **Cypress**: Cypress 13.17.0（run-and-exit設定、実際のAPI接続）

### ネットワーク構成
- `frontend-network`: フロントエンド ↔ バックエンド ↔ Cypress
- `backend-network`: バックエンド ↔ データベース
- セキュリティのためデータベースはフロントエンドから分離

### 主要技術スタック
- **フロントエンド**: React 18.3 + React Router v7.6 + Vite 5.4 + TypeScript 5.8 + Tailwind CSS 3.4
- **バックエンド**: FastAPI 0.115.5 + SQLAlchemy 2.0 + Poetry + Python 3.13 + structlog
- **データベース**: PostgreSQL 13 + asyncpg
- **セッション管理**: JWT + HttpOnly Cookies（30分/5日期限）
- **テスト**: Cypress 13.17.0 + pytest
- **インフラ**: Docker + Docker Compose

## クイックリファレンス

### サービス一覧とアクセス情報
| サービス | URL | 用途 | ポート |
|---------|-----|------|--------|
| フロントエンド | http://localhost:5173 | 開発サーバー（Vite、HTTPS無効時） | 5173 |
| フロントエンド | https://localhost:5173 | 開発サーバー（Vite、HTTPS有効時） | 5173 |
| フロントエンド | http://localhost:3000 | 本番サーバー | 3000 |
| バックエンドAPI | http://localhost:8000 | FastAPIアプリケーション | 8000 |
| Swagger UI | http://localhost:8000/docs | API仕様書 | 8000 |
| PostgreSQL | localhost:5432 | データベース | 5432 |

### よく使用するコマンド組み合わせ
```bash
# 開発開始
docker compose up -d frontend backend db && docker compose logs -f frontend backend

# 依存関係更新後の再起動
docker compose down && docker compose build && docker compose up -d frontend backend db

# フロントエンド品質チェック
docker compose exec frontend npm run typecheck && docker compose exec frontend npm run lint

# バックエンド品質チェック
docker compose exec backend poetry run pytest --cov && docker compose exec backend poetry run ruff check . && docker compose exec backend poetry run mypy .

# 完全なテストサイクル
docker compose up -d frontend backend db && docker compose --profile test run --rm cypress
```

## 開発フロー

1. **基本環境起動**: `docker compose up -d frontend backend db` で基本サービス起動
2. **フロントエンド開発**: `http://localhost:5173` でアクセス
3. **バックエンドAPI**: `http://localhost:8000/docs` でSwagger UI確認
4. **E2Eテスト実行**: `docker compose --profile test run --rm cypress`

## ファイル構成の特徴

### 従来型アプリ配置
- 各アプリが`frontend/`, `backend/`, `cypress/`として独立
- 各アプリディレクトリ直下にDockerfile配置
- アプリケーションコードとDockerfileの物理的近接性
- マイクロサービスアーキテクチャとの親和性

### Docker設定
- 各Dockerfileが対応するアプリディレクトリに配置
- `docker-compose.yml`で各アプリの`context`と`dockerfile`を指定
- 開発用ボリュームマウントで効率的なライブリロード

## 重要な注意事項

### 開発時の注意
- 各アプリの詳細開発情報は各ディレクトリの`CLAUDE.md`を参照
- データベース接続は非同期PostgreSQL操作用にasyncpgを使用
- Cypressテストはコンテナネットワーク内で`http://frontend:5173`をターゲット（実際のAPI接続）
- フロントエンドはHTTPS/HTTP切り替え可能（`DISABLE_HTTPS=true`でHTTP化）
- 全コンテナはライブ開発用のボリュームマウントを使用
- structlogによる構造化ログ（ensure_ascii=False設定で日本語対応）

### Dockerfile配置の設計思想
- **開発者中心**: アプリ担当者がDockerfileを管理
- **独立性重視**: 各アプリが自己完結型
- **スケーラビリティ**: マイクロサービス化への対応
- **標準準拠**: 業界標準パターンの採用

## 認証・認可システム

### JWT + HttpOnly Cookie認証
- **アクセストークン**: 30分（自動リフレッシュ）
- **リフレッシュトークン**: 5日
- **Cookie設定**: HttpOnly, Secure, SameSite=lax
- **自動トークンリフレッシュ**: 401エラー時に透明な更新

### セキュリティ機能
- **統一エラーハンドリング**: ミドルウェアによる集約処理
- **エラー位置追跡**: 実際のエラー発生箇所をログに記録
- **Cookie抽出**: 必要最小限のCookieのみ送信
- **パスワード暗号化**: bcrypt + ソルト

詳細は**[認証・認可システム仕様書](./claude/temp_doc/基本設計/認証・認可システム仕様書.md)**を参照

## トラブルシューティング

### よくある問題と解決法

#### 1. Docker関連
```bash
# コンテナ起動エラー
docker compose down -v && docker compose build && docker compose up -d frontend backend db

# ポート競合エラー
docker compose down && lsof -ti:5173,3000,8000,5432 | xargs kill -9

# ボリューム関連エラー（node_modules等）
docker compose down -v && docker volume prune -f && docker compose build --no-cache
```

#### 2. フロントエンド開発エラー
```bash
# TypeScript型エラー
docker compose exec frontend npm run typecheck

# ESLintエラー
docker compose exec frontend npm run lint --fix

# 依存関係エラー
docker compose exec frontend npm install
```

#### 3. バックエンド開発エラー
```bash
# Poetryロックエラー
docker compose exec backend poetry lock --no-update && poetry install --no-root

# データベース接続エラー
docker compose exec backend poetry run alembic upgrade head

# テスト失敗
docker compose exec backend poetry run pytest -v --tb=short
```

#### 4. ネットワーク・接続問題
```bash
# サービス間通信確認
docker compose exec frontend ping backend
docker compose exec backend ping db

# ポート確認
docker compose ps
netstat -tulpn | grep :5173
```

#### 5. E2Eテスト関連
```bash
# Cypress実行前チェック
docker compose logs frontend | grep "Local:"
docker compose logs backend | grep "Uvicorn running"

# テスト環境リセット
docker compose --profile test down && docker compose up -d frontend backend db
```

### デバッグコマンド集
```bash
# コンテナ状態確認
docker compose ps -a
docker compose logs frontend backend db

# リソース使用量確認
docker stats

# コンテナ内シェルアクセス
docker compose exec frontend sh
docker compose exec backend bash

# 設定確認
docker compose config
docker compose config --profile test
```

### パフォーマンス最適化
- マルチステージDockerビルドによる本番最適化
- 本番環境用docker-compose.prod.ymlの作成
- 依存関係レイヤーキャッシュの最適化
- セキュリティスキャンの導入

### 環境固有の問題
#### Windows WSL2環境
- ファイル監視の問題: `CHOKIDAR_USEPOLLING=true`環境変数を確認
- パス区切り文字の問題: Unixスタイルパスを使用

#### macOS環境
- Docker Desktop設定でファイル共有を確認
- Rosetta環境でのM1チップ互換性確認

## 品質管理・静的解析

### コード品質ツール（2025-01-27対応済み）
#### フロントエンド
- **ESLint**: 全警告修正済み（useEffect依存配列対応）
- **TypeScript**: strict mode + 型安全性確保
- **Prettier**: 統一されたコードフォーマット

#### バックエンド  
- **Ruff**: 全エラー修正済み（27個のエラー対応）
- **mypy**: 43ファイルの型チェック
- **pytest**: 92テストケース（89%カバレッジ）

### 実施済み品質改善
- **トレーリングカンマ**: COM812エラー対応
- **空白行処理**: W293エラー対応
- **重複定義削除**: F811エラー対応
- **未使用import削除**: 全モジュールで実施

## 最新の改善点（2025-01-27）

### 技術スタック更新
- **React Router**: v7.0 → v7.6（SSR・型生成強化）
- **TypeScript**: v5.1 → v5.8（型システム改善）
- **FastAPI**: 0.115.5（最新安定版）
- **Python**: 3.13（最新バージョン）

### アーキテクチャ改善
1. **統一エラーハンドリング**: ミドルウェアによる集約
2. **日本語ログ対応**: ensure_ascii=False設定
3. **Cookie管理強化**: セキュリティ向上のための抽出機能
4. **モックAPI削除**: Cypressで実際のAPIテスト
5. **静的解析準拠**: Ruff/ESLint全エラー修正

### セキュリティ強化
- **最小権限原則**: 必要なCookieのみ送信
- **エラー位置追跡**: デバッグ効率向上
- **JWT管理**: アクセス/リフレッシュトークンの適切な管理
- **HTTPS対応**: 開発・本番環境での暗号化通信

この構成により、エンタープライズレベルのWebアプリケーション開発が可能な、保守性・スケーラビリティ・セキュリティに優れたテンプレートを提供します。