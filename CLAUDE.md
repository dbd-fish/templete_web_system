# CLAUDE.md - Webシステム開発テンプレート（モノレポ版）

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
日本語で回答してください。

## プロジェクト概要

これはDockerベースのWebシステム開発テンプレートで、モノレポ構成を採用しています。
フロントエンド（React Router + Vite）、バックエンド（FastAPI + PostgreSQL）、E2Eテスト（Cypress）を統合管理します。

## ディレクトリ構成

```
templete_web_system/
├── docker-compose.yml          # マルチコンテナオーケストレーション
├── apps/                       # アプリケーションコード（モノレポ）
│   ├── frontend/              # React Router + Vite アプリケーション
│   │   ├── CLAUDE.md          # フロントエンド開発ガイド
│   │   ├── package.json       # Node.js依存関係
│   │   ├── vite.config.ts     # Vite設定
│   │   ├── app/               # Reactアプリケーション
│   │   └── public/            # 静的ファイル
│   ├── backend/               # FastAPI + PostgreSQL アプリケーション
│   │   ├── CLAUDE.md          # バックエンド開発ガイド
│   │   ├── pyproject.toml     # Python依存関係（Poetry）
│   │   ├── main.py            # FastAPIエントリーポイント
│   │   ├── app/               # アプリケーションロジック
│   │   ├── alembic/           # データベースマイグレーション
│   │   └── tests/             # バックエンドテスト
│   └── e2e/                   # Cypress E2Eテスト
│       ├── CLAUDE.md          # E2Eテスト開発ガイド
│       ├── cypress.config.js  # Cypress設定
│       ├── run-tests.sh       # テスト実行スクリプト
│       └── cypress/           # テストファイル
├── infrastructure/             # インフラストラクチャ設定
│   └── docker/                # Dockerfiles
│       ├── frontend.Dockerfile
│       ├── backend.Dockerfile
│       └── e2e.Dockerfile
├── init-scripts/              # データベース初期化スクリプト
├── docs/                      # プロジェクトドキュメント（空）
├── scripts/                   # 開発・デプロイスクリプト（空）
└── CLAUDE.md                  # このファイル（プロジェクト全体）
```

## モノレポの利点

- **統合管理**: 全コンポーネントが単一リポジトリで管理
- **バージョン同期**: フロントエンド・バックエンド・テストの統合
- **統一CI/CD**: 一つのパイプラインで全体テスト
- **開発効率**: セットアップが簡単、クロスコンポーネント開発容易
- **型安全性**: 将来的にTypeScript型定義の共有が可能

## 基本的な開発コマンド

### Docker環境
```bash
# 全サービス起動
docker compose up

# 特定サービス起動
docker compose up frontend
docker compose up backend db
docker compose up e2e

# コンテナ再ビルド
docker compose build

# 全サービス停止
docker compose down
```

### 各アプリケーションの詳細

各アプリケーションの詳細な開発情報は、それぞれのCLAUDE.mdを参照してください：

- **[apps/frontend/CLAUDE.md](./apps/frontend/CLAUDE.md)**: React Router + Vite フロントエンド
- **[apps/backend/CLAUDE.md](./apps/backend/CLAUDE.md)**: FastAPI + PostgreSQL バックエンド  
- **[apps/e2e/CLAUDE.md](./apps/e2e/CLAUDE.md)**: Cypress E2Eテスト

## アーキテクチャ概要

### コンテナ構成
- **フロントエンド**: React Router + Vite（ポート3000/5173）
- **バックエンド**: FastAPI + uvicorn（ポート8000）
- **データベース**: PostgreSQL 13（ポート5432）
- **E2E**: Cypress 13.17.0（継続起動設定）

### ネットワーク構成
- `frontend-network`: フロントエンド ↔ バックエンド ↔ E2E
- `backend-network`: バックエンド ↔ データベース
- セキュリティのためデータベースはフロントエンドから分離

### 主要技術スタック
- **フロントエンド**: React 18 + React Router v7 + Vite + TypeScript + Tailwind CSS
- **バックエンド**: FastAPI + SQLAlchemy 2.0 + Poetry + Python 3.13
- **データベース**: PostgreSQL 13 + asyncpg
- **テスト**: Cypress 13.17.0 + pytest
- **インフラ**: Docker + Docker Compose

## 開発フロー

1. **環境起動**: `docker compose up` で全サービス起動
2. **フロントエンド開発**: `http://localhost:5173` でアクセス
3. **バックエンドAPI**: `http://localhost:8000/docs` でSwagger UI確認
4. **E2Eテスト実行**: `docker exec e2e_container ./run-tests.sh`

## ファイル構成の特徴

### モノレポ構成
- `apps/`: 全アプリケーションコードを集約
- `infrastructure/`: Docker設定を分離
- 各アプリで独立したCLAUDE.mdを維持
- 将来的な共有ライブラリ（`packages/`）の追加に対応

### Docker設定
- 全Dockerfileを`infrastructure/docker/`に集約
- モノレポ対応のbuild contextとCOPY設定
- 開発用ボリュームマウントで効率的なライブリロード

## 重要な注意事項

### 開発時の注意
- 各アプリの詳細開発情報は各ディレクトリの`CLAUDE.md`を参照
- データベース接続は非同期PostgreSQL操作用にasyncpgを使用
- E2Eテストはコンテナネットワーク内で`http://frontend:5173`をターゲット
- 全コンテナはライブ開発用のボリュームマウントを使用

### 今後の拡張性
- `packages/`: 共有ライブラリ・型定義の追加
- `docs/`: プロジェクトドキュメントの充実  
- `scripts/`: 開発・デプロイ自動化スクリプト
- `.github/workflows/`: 統合CI/CDパイプライン
- マルチステージDockerビルドによる本番最適化

## トラブルシューティング

### よくある問題
1. **コンテナ起動エラー**: 
   - `docker compose down` → `docker compose build` → `docker compose up`

2. **ボリュームマウント問題**:
   - パスが`apps/`構成に対応しているか確認

3. **ネットワーク接続問題**:
   - コンテナ間通信でサービス名を使用（例: `http://backend:8000`）

### パフォーマンス最適化
- マルチステージDockerビルドの導入を推奨
- 本番環境用のdocker-compose.prod.ymlの作成
- 依存関係レイヤーキャッシュの最適化