# CLAUDE.md - フロントエンド開発ガイド

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
日本語で回答してください。
提供するコードはnpm run typecheck, npm run lint, npm run formatを満たすようにして。

## フロントエンド開発環境

React Router v7 + Vite + TypeScript + Tailwind CSS + shadcn/ui を使用したモダンWebアプリケーション。
Feature-based Architecture採用でスケーラブルな設計を実現。

## 開発コマンド

```bash
# 開発サーバー起動（HTTPS対応）
npm run dev          # https://localhost:5173

# 本番ビルド
npm run build

# 本番サーバー起動  
npm run start

# 型チェック（React Router型生成 + TypeScript）
npm run typecheck    # react-router typegen && tsc

# リント（ESLint）
npm run lint

# フォーマット（Prettier）
npm run format
npm run format:check
```

## 技術スタック

### **フロントエンド**
- **React 18.3** + **React Router v7.6**（SSR対応）
- **Vite 5.4**（高速開発サーバー・ビルドツール）
- **TypeScript 5.8**（strict mode有効）
- **Tailwind CSS 3.4** + **shadcn/ui**（12コンポーネント実装済み・最新版）

### **開発ツール**
- **ESLint 8.57** + **@typescript-eslint 8.36**
- **Prettier**（コードフォーマット）
- **MSW 2.10**（モックサーバー）
- **ts-node**（TypeScript実行環境）

### **要求環境**
- **Node.js >= 20.0.0**
- **Docker & Docker Compose**

## アーキテクチャ

### **Feature-based Architecture（命名規則統一済み）**

```
app/
├── components/                 # 共通UIコンポーネント
│   ├── common/                # 汎用コンポーネント（3ファイル）
│   │   ├── ErrorMessage.tsx   # エラーメッセージ表示
│   │   ├── SimpleCard.tsx     # シンプルカード
│   │   └── SiteTitle.tsx      # サイトタイトル
│   ├── layout/                # レイアウト関連（6ファイル）
│   │   ├── Footer.tsx         # フッター
│   │   ├── Header.tsx         # ヘッダー制御
│   │   ├── Layout.tsx         # 基本レイアウト
│   │   ├── LoggedInHeader.tsx # ログイン時ヘッダー
│   │   ├── LoggedOutHeader.tsx # ログアウト時ヘッダー
│   │   └── Main.tsx           # メインエリア
│   └── ui/                    # shadcn/ui コンポーネント（12ファイル）
│       ├── accordion.tsx      # アコーディオン
│       ├── badge.tsx          # バッジ
│       ├── button.tsx         # ボタン
│       ├── card.tsx           # カード
│       ├── checkbox.tsx       # チェックボックス
│       ├── input.tsx          # 入力フィールド
│       ├── radio-group.tsx    # ラジオグループ
│       ├── select.tsx         # セレクト
│       ├── sheet.tsx          # シート
│       ├── switch.tsx         # スイッチ
│       ├── tabs.tsx           # タブ
│       └── textarea.tsx       # テキストエリア
├── features/                  # 機能別モジュール（命名規則統一済み）
│   ├── auth/                  # 認証機能（完全実装）
│   │   ├── actions/           # React Router アクション
│   │   │   └── logoutAction.tsx
│   │   ├── apis/              # API関数
│   │   │   └── authApi.ts     # 統合認証API
│   │   ├── components/        # 認証コンポーネント（5ファイル）
│   │   │   ├── LoginForm.tsx
│   │   │   ├── ProfileCard.tsx
│   │   │   ├── ResetPasswordForm.tsx
│   │   │   ├── SendResetPasswordForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── errors/            # 認証エラークラス
│   │   │   └── AuthenticationError.tsx
│   │   ├── loaders/           # React Router ローダー（2ファイル）
│   │   │   ├── authTokenLoader.tsx
│   │   │   └── userDataLoader.tsx
│   │   ├── pages/             # ページコンポーネント（9ファイル）
│   │   │   ├── home.tsx       # ホームページ
│   │   │   ├── login.tsx      # ログインページ
│   │   │   ├── mypage.tsx     # マイページ
│   │   │   ├── signup.tsx     # サインアップ
│   │   │   ├── send-signup-email.tsx
│   │   │   ├── signup-vertify-complete.tsx
│   │   │   ├── send-reset-password-email.tsx
│   │   │   ├── send-reset-password-email-complete.tsx
│   │   │   ├── reset-password.tsx
│   │   │   └── reset-password-complete.tsx
│   │   ├── types.ts           # 認証専用型定義
│   │   ├── cookies.ts         # Cookie管理
│   │   └── passwordValidation.ts # パスワードバリデーション
│   └── pages/                 # 静的ページ群
│       └── pages/             # 静的ページ（6ファイル）
│           ├── NotFound.tsx   # 404ページ
│           ├── aboutUs.tsx    # 運営者情報
│           ├── contact.tsx    # お問い合わせ
│           ├── eCommerceLaw.tsx # 特定商取引法
│           ├── privacyPolicy.tsx # プライバシーポリシー
│           └── termsOfService.tsx # 利用規約
├── hooks/                     # カスタムフック（1ファイル）
│   └── useClickOutside.tsx    # 外部クリック検出
├── lib/                       # 自動生成されるshadcn/ui専用ユーティリティ
│   └── utils.ts               # cn関数（clsx + tailwind-merge）
├── mocks/                     # MSW モックAPI
│   ├── data/                  # モックデータ（2ファイル）
│   │   ├── auth.ts           # 認証関連データ
│   │   └── users.ts          # ユーザーデータ
│   ├── handlers/              # MSWハンドラー（1ファイル）
│   │   └── authHandlers.ts   # 認証APIハンドラー
│   ├── utils/                 # モックユーティリティ（1ファイル）
│   │   └── mockHelpers.ts    # ヘルパー関数
│   ├── browser.ts             # ブラウザ用MSW設定
│   └── server.ts              # サーバー用MSW設定
├── utils/                     # アプリケーションユーティリティ（2ファイル）
│   ├── apiErrorHandler.ts     # API エラーハンドリング
│   └── types.ts               # 共通型定義
├── entry.client.tsx           # クライアントエントリーポイント
├── entry.server.tsx           # サーバーエントリーポイント
├── root.tsx                   # ルートコンポーネント
├── routes.ts                  # ルーティング設定（15ルート）
└── tailwind.css               # Tailwind CSS
```

### **ルーティング設定（React Router v7）**

```typescript
// routes.ts - 設定ベースルーティング（最新版）
export default [
  // ホーム
  index('./features/auth/pages/home.tsx'),
  
  // 認証関連（8ルート）
  route('login', './features/auth/pages/login.tsx'),
  route('mypage', './features/auth/pages/mypage.tsx'),
  route('signup', './features/auth/pages/signup.tsx'),
  route('send-signup-email', './features/auth/pages/send-signup-email.tsx'),
  route('signup-vertify-complete', './features/auth/pages/signup-vertify-complete.tsx'),
  route('send-reset-password-email', './features/auth/pages/send-reset-password-email.tsx'),
  route('send-reset-password-email-complete', './features/auth/pages/send-reset-password-email-complete.tsx'),
  route('reset-password', './features/auth/pages/reset-password.tsx'),
  route('reset-password-complete', './features/auth/pages/reset-password-complete.tsx'),
  
  // 静的ページ（5ルート）
  route('privacy-policy', './features/pages/pages/privacyPolicy.tsx'),
  route('terms-of-service', './features/pages/pages/termsOfService.tsx'),
  route('e-commerce-law', './features/pages/pages/eCommerceLaw.tsx'),
  route('about-us', './features/pages/pages/aboutUs.tsx'),
  route('contact', './features/pages/pages/contact.tsx'),
  
  // 404ページ
  route('*', './features/pages/pages/NotFound.tsx'),
] satisfies RouteConfig;
```

## 命名規則（統一済み）

### **実施済み命名規則統一**
✅ **features ディレクトリ**: 
- `feature_auth/` → `auth/` (feature prefix削除)
- `feature_pages/` → `pages/` (feature prefix削除)

✅ **components ディレクトリ統合**:
- `header/` → `layout/` に統合（2ファイルをlayoutに移動）

✅ **typo修正**:
- `LoggedInHeade.tsx` → `LoggedInHeader.tsx`

✅ **shadcn/ui コンポーネント**:
- デフォルトの小文字形式を維持（`button.tsx`, `accordion.tsx`, `radio-group.tsx` など）
- **重要**: shadcn/ui の公式命名規則のため変更禁止

### **型定義の再編成**
✅ **Feature-based 型定義**:
- `app/utils/types.ts`: アプリケーション共通型のみ
- `app/features/auth/types.ts`: 認証機能専用型
- 機能固有の型定義を各featureディレクトリに分離

## 重要な設定

### **HTTPS開発環境**
```typescript
// vite.config.ts
server: {
  host: true,
  port: 5173,
  https: {
    key: './certs/key.pem',
    cert: './certs/cert.pem',
  }
}
```
- 開発サーバーはHTTPS対応（`https://localhost:5173`）
- 証明書は`certs/`ディレクトリに配置

### **TypeScript設定**
```json
// tsconfig.json
{
  "include": [".react-router/types/**/*"], // React Router型生成ファイル
  "compilerOptions": {
    "types": ["@react-router/node", "vite/client", "node"],
    "moduleResolution": "Bundler",
    "strict": true,
    "baseUrl": ".",
    "paths": { "~/*": ["./app/*"] }, // パスエイリアス
    "rootDirs": [".", "./.react-router/types"]
  }
}
```

### **React Router v7の特徴**
- **SSR対応**（react-router.config.ts で `ssr: true`）
- **自動型生成**（`.react-router/types/` ディレクトリ）
- **設定ベースルーティング**（routes.ts）
- **Loader/Action パターン**によるデータ取得

### **shadcn/ui設定**
```json
// components.json
{
  "aliases": {
    "components": "~/components",
    "utils": "~/lib/utils",
    "ui": "~/components/ui"
  }
}
```

### **shadcn/ui ユーティリティ（`app/lib/utils.ts`）**

#### **`cn`関数 - Tailwind CSS クラス統合の核心**
```typescript
// app/lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

#### **機能と使用例**

**1. 基本的なクラス結合**
```typescript
cn("p-4", "bg-blue-500", "text-white")
// → "p-4 bg-blue-500 text-white"
```

**2. 条件付きクラス**
```typescript
cn("btn", {
  "bg-red-500": isError,      // true なら適用
  "bg-gray-400": isLoading,   // false なら無視
  "opacity-50": disabled      // 条件による適用
})
```

**3. Tailwind重複クラス自動解決**
```typescript
// 通常の文字列結合（問題あり）
"p-4 p-2" // → 両方残る（無効なCSS）

// cn関数使用（自動解決）
cn("p-4", "p-2") // → "p-2" (後のクラスが優先)
cn("bg-red-500 p-4", "bg-blue-500 m-2") 
// → "p-4 bg-blue-500 m-2" (bg-red-500は自動削除)
```

**4. shadcn/uiコンポーネントでの実際の使用**
```typescript
// app/components/ui/button.tsx
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);
```

#### **依存ライブラリ**
- **`clsx`**: 条件付きクラス名処理
- **`tailwind-merge`**: Tailwind CSS重複クラス解決

#### **自動生成について**
このファイルは **shadcn/ui初期化時に自動生成** されます：
```bash
npx shadcn-ui@latest init  # 初期化時に作成
npx shadcn-ui@latest add button  # コンポーネント追加時も参照
```

#### **重要性**
- **全shadcn/uiコンポーネントの依存関係**
- **TypeScriptエラーの主要原因**（`Cannot find module '~/lib/utils'`）
- **カスタムコンポーネント作成時の必須ツール**

## モックAPI システム（MSW）

### **開発環境での自動モック**
```typescript
// app/entry.client.tsx
if (process.env.NODE_ENV === 'development') {
  const { worker } = await import('./mocks/browser');
  await worker.start({ onUnhandledRequest: 'warn' });
}
```

### **認証モックデータ**
```typescript
// 開発時に使用可能な認証情報
const MOCK_CREDENTIALS = {
  USER: {
    email: 'testuser@example.com',
    username: 'testuser', 
    password: 'Password123456+-',
  },
  ADMIN: {
    email: 'admin@example.com',
    username: 'admin',
    password: 'adminpassword',
  }
};
```

### **モックAPIエンドポイント**
- `POST /api/v1/auth/login` - ログイン
- `POST /api/v1/auth/logout` - ログアウト
- `POST /api/v1/auth/me` - ユーザー情報取得
- `POST /api/v1/auth/signup` - ユーザー登録
- `POST /api/v1/auth/send-verify-email` - 認証メール送信
- `POST /api/v1/auth/send-password-reset-email` - パスワードリセットメール
- `POST /api/v1/auth/reset-password` - パスワードリセット

## コード品質・型安全性

### **ESLint設定（最新対応済み）**
```javascript
// .eslintrc.cjs
{
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react', 'react-hooks'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/no-explicit-any': 'error', // any型禁止
    'no-useless-catch': 'off' // catch句での適切な処理
  },
  settings: {
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json'
      }
    }
  }
}
```

### **型安全性の確保**
- **strict mode**有効（TypeScript）
- **未使用変数エラー**の適切な処理
- **any型の使用禁止** → `unknown`型の積極活用
- **catch句での型安全な処理**
- **Feature-based 型定義**: 機能ごとに型を分離

## 開発時の注意点

### **React Router v7 開発パターン**
```typescript
// Loader使用例
export async function loader({ request }: LoaderFunctionArgs) {
  return await getUser(request);
}

// Action使用例  
export async function action({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  return await login(formData.get('email'), formData.get('password'));
}

// Component使用例
export default function Login() {
  const user = useLoaderData<typeof loader>();
  return <LoginForm />;
}
```

### **認証システム**
- **Cookie ベース認証**（httpOnly、secure対応）
- **AuthenticationError**による統一エラーハンドリング
- **userDataLoader**による認証状態管理

### **スタイリング（cn関数の活用）**
```typescript
// app/lib/utils.ts の cn関数使用例
import { cn } from '~/lib/utils';

// 基本的な使用パターン
<button className={cn(
  "px-4 py-2 rounded-md font-medium",  // ベースクラス
  { 
    "bg-red-500 text-white": isError,      // エラー時
    "bg-blue-500 text-white": !isError,   // 通常時
    "opacity-50 cursor-not-allowed": disabled  // 無効時
  },
  "transition-colors duration-200",      // 追加クラス
  customClassName                        // プロパティから渡されたクラス
)} />

// shadcn/ui パターン（バリアント + カスタム）
<Card className={cn(
  "border rounded-lg p-6",  // デフォルトスタイル
  {
    "border-red-500 bg-red-50": hasError,
    "border-green-500 bg-green-50": isSuccess
  },
  className  // 外部から渡されるカスタムクラス
)} />
```

### **型安全なAPI呼び出し**
```typescript
// app/features/auth/apis/authApi.ts
export const login = async (email: string, password: string) => {
  const response = await apiFormRequest(`${apiUrl}/api/v1/auth/login`, {
    username: email, // OAuth2形式
    password: password,
  });
  return response;
};
```

## GitHub Actions対応

### **TypeScriptエラー解決**
```yaml
# .github/workflows/github-actions_frontend_prettier_eslint.yml
- name: Run TypeScript Type Check
  run: docker compose run --rm frontend npm run typecheck
```

- **パスエイリアス解決**: tsconfig.jsonで`~/*`設定
- **React Router型生成**: `react-router typegen`で自動生成
- **Node.js型定義**: `types: ["node"]`で対応
- **CI環境対応**: shadcn/ui デフォルト命名維持でLinux/Windows互換性確保

### **型チェックコマンド**
```json
{
  "scripts": {
    "typecheck": "react-router typegen && tsc"
  }
}
```
1. React Router型ファイル生成（`.react-router/types/`）
2. TypeScript型チェック実行

## トラブルシューティング

### **よくある問題**

#### **`Cannot find module '~/lib/utils'`**
- **原因**: 
  1. パスエイリアス設定の問題
  2. `app/lib/utils.ts`ファイル不存在
  3. shadcn/ui未初期化
- **解決方法**:
  ```bash
  # 1. tsconfig.jsonのpaths設定確認
  {
    "paths": { "~/*": ["./app/*"] }
  }
  
  # 2. shadcn/ui初期化（utils.ts自動生成）
  npx shadcn-ui@latest init
  
  # 3. 手動でutils.ts作成する場合
  mkdir -p app/lib
  echo 'import { type ClassValue, clsx } from "clsx";
  import { twMerge } from "tailwind-merge";
  
  export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
  }' > app/lib/utils.ts
  
  # 4. 依存関係インストール
  npm install clsx tailwind-merge
  ```

#### **CI環境でのshadcn/ui コンポーネントエラー**
- **原因**: ファイルシステムの大文字小文字区別（Windows vs Linux）
- **解決**: shadcn/ui デフォルトの小文字命名を維持
- **重要**: `app/components/ui/` 内のファイル名は変更禁止

#### **React Router型生成エラー**
- **原因**: `.react-router`ディレクトリ不在
- **解決**: `npm run typecheck`で型生成実行

#### **MSWモックが効かない**
- **原因**: public/mockServiceWorker.js不在
- **解決**: `npx msw init public/`で初期化

### **Docker環境の問題**
```bash
# コンテナ再ビルド
docker compose build frontend

# 依存関係再インストール  
docker compose run --rm frontend npm install

# キャッシュクリア
docker compose run --rm frontend npm run dev -- --force
```

## パフォーマンス

### **最適化機能**
- **React Router v7 SSR**（サーバーサイドレンダリング）
- **Vite HMR**（Hot Module Replacement）
- **Tailwind CSS最適化**（未使用クラス削除）
- **shadcn/ui Tree Shaking**（使用コンポーネントのみ）

### **ビルド最適化**
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [reactRouter(), tsconfigPaths()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router']
        }
      }
    }
  }
});
```

## 拡張性

### **新機能追加パターン**
```
app/features/新機能/
├── actions/     # React Router アクション
├── apis/        # API関数
├── components/  # 機能専用コンポーネント  
├── loaders/     # React Router ローダー
├── pages/       # ページコンポーネント
├── types.ts     # 機能専用型定義
└── utils/       # 機能専用ユーティリティ
```

### **shadcn/ui コンポーネント追加**
```bash
# 新しいUIコンポーネント追加
npx shadcn-ui@latest add [component-name]
```
**重要**: 追加されたコンポーネントのファイル名は変更禁止（デフォルト命名維持）

## 最新の改善点

### **✅ 実施済み改善**
1. **命名規則統一**: feature prefix削除、header統合、typo修正
2. **型定義再編成**: Feature-based architecture に沿った型分離
3. **CI環境対応**: shadcn/ui デフォルト命名維持で互換性確保
4. **ディレクトリ構造最適化**: より保守しやすい構造に統一
5. **依存関係最適化**: 未使用ライブラリ削除と最新バージョン更新

### **🔄 最新の依存関係最適化**
**削除した未使用ライブラリ**:
- `@headlessui/react` - 未使用UIライブラリ
- `@heroicons/react` - 未使用アイコンライブラリ（lucide-react使用）
- `eslint-config-react-app` - 未使用ESLint設定

**最新バージョン更新**:
- React Router: v7.0 → v7.6（SSR・型生成機能強化）
- Radix UI: 全コンポーネント最新版（shadcn/ui基盤強化）
- TypeScript: v5.1 → v5.8（型システム改善）
- MSW: v2.7 → v2.10（モック機能向上）

このアーキテクチャにより、大規模Webアプリケーションでも保守しやすく、型安全で高性能なフロントエンドを構築できます。