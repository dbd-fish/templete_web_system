]# CLAUDE.md - フロントエンド開発ガイド

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
日本語で回答してください。
提供するコードはnpm run typecheck, npm run lint, npm run formatを満たすようにして。


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
├── components/                 # UIコンポーネント
│   ├── common/                # 共通UIコンポーネント
│   │   ├── ErrorMessage.tsx   # エラーメッセージ
│   │   ├── NotFound.tsx       # 404ページ
│   │   ├── SimpleCard.tsx     # シンプルカード
│   │   └── SiteTitle.tsx      # サイトタイトル
│   ├── header/                # ヘッダー関連
│   │   ├── LoggedInHeader.tsx # ログイン時ヘッダー
│   │   └── LoggedOutHeader.tsx # ログアウト時ヘッダー
│   ├── layout/                # レイアウト関連
│   │   ├── Footer.tsx         # フッター
│   │   ├── Header.tsx         # ヘッダー制御
│   │   ├── Layout.tsx         # 基本レイアウト
│   │   └── Main.tsx           # メインエリア
│   └── ui/                    # shadcn/ui コンポーネント
│       ├── button.tsx         # ボタン
│       ├── card.tsx           # カード
│       ├── input.tsx          # 入力フィールド
│       └── ...                # その他UIコンポーネント
├── features/                  # 機能別モジュール（Feature-based Architecture）
│   ├── feature_auth/          # 認証機能
│   │   ├── actions/           # React Router アクション
│   │   ├── apis/              # API関数
│   │   ├── components/        # 認証関連コンポーネント
│   │   ├── loaders/           # React Router ローダー
│   │   ├── pages/             # ページコンポーネント
│   │   ├── cookies.ts         # Cookie管理
│   │   └── passwordValidation.ts # バリデーション
│   └── feature_pages/         # 静的ページ群
│       └── routes/            # 静的ページルート
│           ├── aboutUs.tsx    # 運営者情報
│           ├── contact.tsx    # お問い合わせ
│           ├── eCommerceLaw.tsx # 特定商取引法
│           ├── privacyPolicy.tsx # プライバシーポリシー
│           └── termsOfService.tsx # 利用規約
├── hooks/                     # カスタムフック
│   └── useClickOutside.tsx    # 外部クリック検出
├── lib/                       # shadcn/ui専用ユーティリティ
│   └── utils.ts               # cn関数（clsx + tailwind-merge）
├── mocks/                     # MSW モックAPI
│   ├── data/                  # モックデータ
│   │   ├── auth.ts           # 認証関連データ
│   │   └── users.ts          # ユーザーデータ
│   ├── handlers/              # MSWハンドラー
│   │   └── authHandlers.ts   # 認証APIハンドラー
│   ├── utils/                 # モックユーティリティ
│   │   └── mockHelpers.ts    # ヘルパー関数
│   ├── browser.ts             # ブラウザ用MSW設定
│   └── server.ts              # サーバー用MSW設定
├── utils/                     # アプリケーションユーティリティ
│   ├── errors/                # エラークラス
│   │   └── AuthenticationError.tsx # 認証エラー
│   ├── apiErrorHandler.ts     # API エラーハンドリング
│   └── types.ts               # 型定義
├── entry.client.tsx           # クライアントエントリーポイント
├── entry.server.tsx           # サーバーエントリーポイント
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
- 例: `import Layout from '~/components/layout/Layout'`

#### React Router v7の特徴
- SSR対応（react-router.config.ts で `ssr: true`）
- 設定ベースルーティング（routes.ts で設定）
- Loader/Action パターンによるデータ取得

## モックAPI と 本番API の使用方法

### 概要

開発環境では **MSW（Mock Service Worker）** を使用してモックAPIを提供し、本番環境では実際のバックエンドAPIと連携します。

### 開発環境（モックAPI）

#### MSW設定
```typescript
// app/entry.client.tsx
if (process.env.NODE_ENV === 'development') {
  const { worker } = await import('./mocks/browser');
  await worker.start({
    onUnhandledRequest: 'warn',
  });
}
```

#### モックデータ構成
```
app/mocks/
├── data/
│   ├── auth.ts           # 認証関連のモックデータ
│   └── users.ts          # ユーザーのモックデータ
├── handlers/
│   └── authHandlers.ts   # 認証APIのモックハンドラー
└── utils/
    └── mockHelpers.ts    # モック用ヘルパー関数
```

#### モック認証情報
```typescript
// 開発時に使用可能な認証情報
const CREDENTIALS = {
  USER: {
    email: 'testuser@example.com',
    username: 'testuser',
    password: 'Password123456+-',
  },
  ADMIN: {
    email: 'admin@example.com',
    username: 'admin',
    password: 'adminpassword',
  },
};
```

#### モックAPI例
```typescript
// app/mocks/handlers/authHandlers.ts
export const loginHandler = http.post(
  'http://localhost:5173/api/v1/auth/login',
  async ({ request }) => {
    // モック認証処理
    const user = authenticateUser(username, password);
    if (user) {
      return HttpResponse.json(
        { success: true, data: user },
        { 
          headers: { 
            'Set-Cookie': `authToken=${MOCK_ACCESS_TOKEN}; HttpOnly; Secure; SameSite=Lax; Path=/` 
          } 
        }
      );
    }
    return new HttpResponse(null, { status: 401 });
  }
);
```

### 本番環境（実API）

#### 環境変数設定
```bash
# .env
ENV_MODE='production'
API_URL=http://backend:8000
```

#### API関数例
```typescript
// app/features/feature_auth/apis/authApi.ts
export const login = async (email: string, password: string) => {
  const apiUrl = process.env.API_URL;
  
  const response = await apiFormRequest(
    `${apiUrl}/api/v1/auth/login`,
    {
      username: email,
      password: password,
    }
  );
  
  return response;
};
```

### 環境切り替え

#### 開発環境 → 本番環境
1. **環境変数変更**
   ```bash
   # .env
   ENV_MODE='development' → ENV_MODE='production'
   API_URL=http://localhost:5173 → API_URL=http://backend:8000
   ```

2. **MSW無効化**
   ```typescript
   // MSWは自動的にNODE_ENV=productionで無効化される
   ```

3. **認証フロー変更**
   - 開発: action関数内で直接認証 → API経由認証
   - 本番: authApi.ts の関数を使用

#### API呼び出しパターン

**開発環境（モック）:**
```typescript
// ページのaction関数内で直接処理
export const action: ActionFunction = async ({ request }) => {
  const user = authenticateUser(email, password); // モック関数
  if (user) {
    return redirect('/mypage', {
      headers: { 'Set-Cookie': cookieString },
    });
  }
};
```

**本番環境（実API）:**
```typescript
// API関数を経由
export const action: ActionFunction = async ({ request }) => {
  const response = await login(email, password); // API関数
  const responseCookieHeader = response.headers.get('set-Cookie');
  return redirect('/mypage', {
    headers: { 'Set-Cookie': responseCookieHeader },
  });
};
```

## 機能別モジュール構成

### feature_auth（認証機能）
- **apis/**: バックエンドAPI呼び出し関数
- **components/**: 認証関連コンポーネント（LoginForm, SignupForm等）
- **loaders/**: React Router のローダー関数
- **actions/**: React Router のアクション関数
- **pages/**: ページコンポーネント

### feature_pages（静的ページ）
- **routes/**: 法的文書、企業情報等の静的ページ

## UI コンポーネント

### shadcn/ui コンポーネント群
- **Form系**: Input, Select, Checkbox, RadioGroup, Switch, Textarea
- **表示系**: Card, Badge, Accordion, Tabs
- **インタラクション**: Button, Sheet

### カスタムコンポーネント
- **Layout**: ヘッダー・フッター・メインエリアの基本構造
- **SimpleCard**: 認証フォーム等で使用するシンプルなカード
- **ErrorMessage**: 統一されたエラー表示

## 開発時の注意点

### React Router v7
- Loader/Action パターンでデータ取得・状態管理を行う
- SSR対応のためクライアント専用コードは適切に分離
- routes.ts でルーティングを集中管理

### 認証システム
- Cookie ベースの認証
- AuthenticationError による統一エラーハンドリング
- userDataLoader でユーザー情報取得

### スタイリング
- Tailwind CSS + shadcn/ui の組み合わせ
- レスポンシブデザイン対応
- カスタムCSS は tailwind.css に追加
- `cn` 関数（lib/utils.ts）でクラス名統合

### 型安全性
- TypeScript strict モード有効
- React Router の型生成機能使用
- パスエイリアス（~/*）でインポート統一

### モック開発
- MSWで本番環境と同等のAPI体験
- 認証フローを含む完全なモック環境
- 開発専用の認証情報でテスト可能

## コンテナ連携

### 開発環境
- フロントエンド: `https://localhost:5173`（HTTPS）
- バックエンドAPI: `http://localhost:8000`
- モックAPI: MSWが自動処理

### 本番環境
- フロントエンド: `http://frontend:5173`（コンテナ内通信）
- バックエンドAPI: `http://backend:8000`（コンテナ内通信）
- 外部アクセス: nginx経由でポート公開

## デバッグ・トラブルシューティング

### 認証関連
- ブラウザの開発者ツールでCookie確認
- MSWのログでモックAPI呼び出し確認
- React Router のローダー・アクションのログ確認

### スタイリング
- Tailwind CSS クラスの重複は `cn` 関数で解決
- shadcn/ui コンポーネントのカスタマイズは公式ドキュメント参照

### パフォーマンス
- React Router v7 のSSR機能でサーバーサイドレンダリング
- Vite の高速ビルドでHMR（Hot Module Replacement）