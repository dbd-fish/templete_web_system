# CLAUDE.md - Webシステム開発テンプレート

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
日本語で回答してください。

## プロジェクト概要

これはDockerベースのWebシステム開発テンプレートで、従来型のアプリ直下Dockerfile配置を採用しています。
フロントエンド（React Router + Vite）、バックエンド（FastAPI + PostgreSQL）、E2Eテスト（Cypress）を統合管理します。

## ディレクトリ構成

```
templete_web_system/
├── docker-compose.yml          # マルチコンテナオーケストレーション
├── frontend/                   # React Router + Vite アプリケーション
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
│   ├── app/                   # アプリケーションロジック
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
└── CLAUDE.md                  # このファイル（プロジェクト全体）
```

## アプリ直下Dockerfile配置の利点

- **直感的理解**: アプリケーションコードとDockerfileが物理的に近接
- **開発者体験**: 各アプリの担当者がDockerfileを見つけやすい
- **マイクロサービス対応**: 各サービスの独立性が高い
- **標準的手法**: Netflix、Uber等多くの企業で採用される構成

## 基本的な開発コマンド

### Docker環境
```bash
# 全サービス起動
docker compose up

# 特定サービス起動
docker compose up frontend
docker compose up backend db
docker compose up cypress

# コンテナ再ビルド
docker compose build

# 全サービス停止
docker compose down
```

### 各アプリケーションの詳細

各アプリケーションの詳細な開発情報は、それぞれのCLAUDE.mdを参照してください：

- **[frontend/CLAUDE.md](./frontend/CLAUDE.md)**: React Router + Vite フロントエンド
- **[backend/CLAUDE.md](./backend/CLAUDE.md)**: FastAPI + PostgreSQL バックエンド  
- **[cypress/CLAUDE.md](./cypress/CLAUDE.md)**: Cypress E2Eテスト

## アーキテクチャ概要

### コンテナ構成
- **フロントエンド**: React Router + Vite（ポート3000/5173）
- **バックエンド**: FastAPI + uvicorn（ポート8000）
- **データベース**: PostgreSQL 13（ポート5432）
- **Cypress**: Cypress 13.17.0（継続起動設定）

### ネットワーク構成
- `frontend-network`: フロントエンド ↔ バックエンド ↔ Cypress
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
4. **Cypressテスト実行**: `docker exec cypress_container ./run-tests.sh`

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
- Cypressテストはコンテナネットワーク内で`http://frontend:5173`をターゲット
- 全コンテナはライブ開発用のボリュームマウントを使用

### Dockerfile配置の設計思想
- **開発者中心**: アプリ担当者がDockerfileを管理
- **独立性重視**: 各アプリが自己完結型
- **スケーラビリティ**: マイクロサービス化への対応
- **標準準拠**: 業界標準パターンの採用

## トラブルシューティング

### よくある問題
1. **コンテナ起動エラー**: 
   - `docker compose down` → `docker compose build` → `docker compose up`

2. **Dockerfileパス問題**:
   - 各アプリディレクトリ直下に正しくDockerfileが配置されているか確認

3. **ネットワーク接続問題**:
   - コンテナ間通信でサービス名を使用（例: `http://backend:8000`）

### 最適化の提案
- マルチステージDockerビルドによる本番最適化
- 本番環境用docker-compose.prod.ymlの作成
- 依存関係レイヤーキャッシュの最適化
- セキュリティスキャンの導入