# Google OAuth認証 設定ガイド

このドキュメントでは、フロントエンドアプリケーションでGoogle OAuth認証を設定する方法について説明します。

## 概要

本システムでは、従来のメールアドレス・パスワード認証に加えて、Google OAuth 2.0認証による単一サインオン（SSO）機能を提供しています。

## 機能一覧

- ✅ Google OAuth 2.0認証によるログイン・サインアップ
- ✅ メールアドレス認証との統合UI
- ✅ 自動ユーザー登録（初回Google認証時）
- ✅ 統一された認証状態管理
- ✅ セキュアなHttpOnlyCookie認証

## 設定手順

### 1. Google Cloud Console設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成、または既存のプロジェクトを選択
3. APIとサービス > 認証情報 に移動
4. 「認証情報を作成」> 「OAuth 2.0 クライアントID」を選択
5. アプリケーションの種類で「ウェブアプリケーション」を選択
6. 以下の設定を行う：

**承認済みのJavaScript生成元**
```
http://localhost:3000
http://localhost:5173
https://yourdomain.com
```

**承認済みのリダイレクトURI**
```
http://localhost:8000/api/v1/auth/google/callback
https://yourdomain.com/api/v1/auth/google/callback
```

7. 「作成」をクリックしてクライアントIDとクライアントシークレットを取得

### 2. 環境変数設定

`.env`ファイルに以下の設定を追加：

```env
# Google OAuth 2.0設定
GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### 3. フロントエンド設定更新

`frontend/app/utils/googleAuth.ts`のGoogle設定を更新：

```typescript
const GOOGLE_CONFIG = {
  CLIENT_ID: 'your-actual-google-client-id.apps.googleusercontent.com',
};
```

## 使用方法

### 1. ログインページ

```typescript
import GoogleLoginButton from '~/features/auth/components/GoogleLoginButton';

// 使用例
<GoogleLoginButton
  onSuccess={(message) => {
    console.log('Google認証成功:', message);
    // リダイレクト処理
  }}
  onError={(error) => {
    console.error('Google認証エラー:', error);
    // エラー処理
  }}
  disabled={false}
/>
```

### 2. 認証状態管理

```typescript
import { useAuth } from '~/hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, logout } = useAuth();

  if (isAuthenticated) {
    return (
      <div>
        <p>ようこそ、{user?.username}さん</p>
        <button onClick={logout}>ログアウト</button>
      </div>
    );
  }

  return <LoginForm />;
}
```

## 認証フロー

### Googleログイン・サインアップフロー

1. **フロントエンド**: GoogleLoginButtonクリック
2. **Google**: Identity Servicesによる認証画面表示
3. **Google**: ユーザー認証後、IDトークンを返却
4. **フロントエンド**: IDトークンをバックエンドAPI `/api/v1/auth/google-login` に送信
5. **バックエンド**: IDトークンを検証
6. **バックエンド**: 既存ユーザーの場合はログイン、新規ユーザーの場合は自動登録
7. **バックエンド**: JWTトークンペアを生成し、HttpOnlyCookieに設定
8. **フロントエンド**: 認証完了、マイページにリダイレクト

### メール認証との統合

- ログイン・サインアップページでは、Googleボタンとメールフォームが並列表示
- 「または」の区切り線でUI的に分離
- どちらの方法でも同様の認証状態に移行

## セキュリティ考慮事項

### バックエンド検証項目

- ✅ GoogleのIDトークン署名検証
- ✅ issuer (`accounts.google.com`) 確認
- ✅ audience (Client ID) 確認
- ✅ email_verified フィールド確認
- ✅ トークン有効期限確認

### フロントエンド セキュリティ

- ✅ HttpOnlyCookie による XSS 攻撃防止
- ✅ Secure属性による HTTPS 強制（本番環境）
- ✅ SameSite=Lax による CSRF 攻撃軽減
- ✅ Google Identity Services の最新版使用

## トラブルシューティング

### よくある問題

#### 1. 「Google OAuth設定が不完全です」エラー

**原因**: Google Client IDが設定されていない、または初期値のまま

**解決方法**:
```typescript
// frontend/app/utils/googleAuth.ts を確認
const GOOGLE_CONFIG = {
  CLIENT_ID: 'your-actual-google-client-id.apps.googleusercontent.com', // 実際のIDに変更
};
```

#### 2. 「Google認証サービスが利用できません」エラー

**原因**: Google Identity Services スクリプトの読み込み失敗

**解決方法**:
- ネットワーク接続を確認
- ブラウザの JavaScript 有効化を確認
- 広告ブロッカーが Google スクリプトをブロックしていないか確認

#### 3. 「無効なクライアントIDです」エラー

**原因**: Google Cloud Consoleの設定不備

**解決方法**:
- Google Cloud Console で承認済みドメインを確認
- Client ID とバックエンドの設定が一致しているか確認

#### 4. CORS エラー

**原因**: フロントエンドのドメインが Google Cloud Console で許可されていない

**解決方法**:
- Google Cloud Console > 認証情報 > OAuth 2.0 クライアント
- 「承認済みのJavaScript生成元」に使用中のドメインを追加

### デバッグ方法

#### 1. コンソールログ確認

```javascript
// ブラウザの開発者ツール > Console で以下を確認
console.log('Google script loaded:', !!window.google?.accounts?.id);
```

#### 2. ネットワークタブ確認

- `/api/v1/auth/google-login` リクエストの内容を確認
- レスポンスステータスとエラーメッセージを確認

#### 3. 認証状態確認

```javascript
// 認証状態の確認
console.log('Auth state:', useAuth());
```

## 開発・テスト環境

### ローカル開発

```bash
# フロントエンド起動
cd frontend
npm run dev
# http://localhost:5173

# バックエンド起動  
cd backend
docker compose up -d backend db
# http://localhost:8000
```

### 本番環境移行

1. **Google Cloud Console設定更新**
   - 本番ドメインを承認済みドメインに追加
   - 本番環境用のリダイレクトURIを設定

2. **環境変数更新**
   ```env
   GOOGLE_CLIENT_ID=production-client-id
   GOOGLE_CLIENT_SECRET=production-client-secret
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
   ```

3. **セキュリティ設定**
   - HTTPS必須（Secure Cookie）
   - 適切なCORS設定
   - CSP (Content Security Policy) 設定

## API仕様

### Google認証エンドポイント

**POST** `/api/v1/auth/google-login`

**リクエスト**:
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**レスポンス (成功)**:
```json
{
  "success": true,
  "message": "Googleログインに成功しました"
}
```

**레スポンス (失敗)**:
```json
{
  "success": false,
  "detail": "認証エラー: メールアドレスが認証されていません"
}
```

## サポート

質問や問題が発生した場合：

1. このドキュメントのトラブルシューティングを確認
2. Google OAuth 2.0の[公式ドキュメント](https://developers.google.com/identity/protocols/oauth2)を参照
3. プロジェクトの Issue を作成

---

最終更新: 2025年7月23日