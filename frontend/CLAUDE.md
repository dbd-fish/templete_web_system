# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## フロントエンド開発環境

React Router v7 + Vite + TypeScript + Tailwind CSS + shadcn/ui を使用したフロントエンドアプリケーション。

## 開発コマンド

```bash
# 開発サーバー起動（HTTPS対応）
npm run dev

# 本番ビルド
npm run build

# 本番サーバー起動
npm run start

# 型チェック
npm run typecheck

# リント
npm run lint

# フォーマット
npm run format
npm run format:check
```

## アーキテクチャ

### ディレクトリ構造

```
app/
├── commons/                    # 共通コンポーネント・ユーティリティ
│   ├── components/             # 共通UIコンポーネント
│   │   ├── header/            # ヘッダー関連
│   │   ├── ErrorMessage.tsx   # エラーメッセージ
│   │   ├── Layout.tsx         # レイアウト
│   │   └── ...
│   ├── hooks/                 # カスタムフック
│   ├── routes/                # 静的ページ（利用規約など）
│   └── utils/                 # ユーティリティ
│       ├── errors/            # エラー関連
│       └── types.ts           # 型定義
├── components/                # shadcn/ui コンポーネント
│   └── ui/                    # UIコンポーネント
├── features/                  # 機能別モジュール
│   └── feature_auth/          # 認証機能
│       ├── actions/           # アクション
│       ├── apis/              # API関数
│       ├── components/        # コンポーネント
│       ├── loaders/           # ローダー
│       └── routes/            # ルート
├── mocks/                     # MSW モック
├── root.tsx                   # ルートコンポーネント
├── routes.ts                  # ルーティング設定
└── tailwind.css               # Tailwind CSS
```

### 技術スタック

- **React Router v7**: SSR対応のルーティング（react-router.config.ts で設定）
- **Vite**: 高速な開発サーバー・ビルドツール
- **TypeScript**: 型安全性の確保
- **Tailwind CSS**: ユーティリティファーストCSS
- **shadcn/ui**: Radix UI ベースのコンポーネントライブラリ
- **MSW**: モックサーバー（開発・テスト用）
- **ESLint + Prettier**: コード品質・フォーマット

### 重要な設定

#### HTTPS開発環境
- 開発サーバーはHTTPS対応（certs/ディレクトリの証明書使用）
- `npm run dev` でhttps://localhost:5173 でアクセス

#### パスエイリアス
- `~/*` → `./app/*` （tsconfig.jsonで設定）
- 例: `import Layout from '~/commons/components/Layout'`

#### React Router v7の特徴
- SSR対応（react-router.config.ts で `ssr: true`）
- ファイルベースルーティング（routes.ts で設定）
- Loader/Action パターンによるデータ取得

### 機能別モジュール構成

#### feature_auth（認証機能）
- **apis/**: バックエンドAPI呼び出し関数
- **components/**: 認証関連コンポーネント（LoginForm, SignupForm等）
- **loaders/**: React Router のローダー関数
- **actions/**: React Router のアクション関数
- **routes/**: ルートコンポーネント（ページ）

### UI コンポーネント

shadcn/ui を使用したコンポーネント群:
- Form系: Input, Select, Checkbox, RadioGroup, Switch, Textarea
- 表示系: Card, Badge, Accordion, Tabs
- インタラクション: Button, Sheet

### 開発時の注意点

#### React Router v7
- Loader/Action パターンでデータ取得・状態管理を行う
- SSR対応のためクライアント専用コードは適切に分離
- routes.ts でルーティングを集中管理

#### 認証システム
- Cookie ベースの認証
- AuthenticationError による統一エラーハンドリング
- userDataLoader でユーザー情報取得

#### スタイリング
- Tailwind CSS + shadcn/ui の組み合わせ
- レスポンシブデザイン対応
- カスタムCSS は tailwind.css に追加

#### 型安全性
- TypeScript strict モード有効
- React Router の型生成機能使用
- パスエイリアス（~/*）でインポート統一

### コンテナ連携

- バックエンドAPI: `http://backend:8000`（コンテナ内通信）
- 開発時フロントエンド: `https://localhost:5173`
- 本番フロントエンド: `http://frontend:5173`（コンテナ内通信）