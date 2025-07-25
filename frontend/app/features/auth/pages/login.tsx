import { ActionFunction, redirect, Link, MetaFunction } from 'react-router';
import { useActionData } from 'react-router';
import { useState } from 'react';
import LoginForm from '~/features/auth/components/LoginForm';
import GoogleLoginButton from '~/features/auth/components/GoogleLoginButton';
import { login } from '~/features/auth/apis/authApi';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';

/**
 * メタデータ関数:
 * - ページのタイトルとメタデータを設定
 */
export const meta: MetaFunction = () => {
  return [
    { title: 'ログイン | Webシステム開発テンプレート' },
    {
      name: 'description',
      content:
        'アカウントへログインします。メールアドレスとパスワードを入力してください。',
    },
  ];
};

// アクション関数
export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    // バリデーション
    if (!email || !password) {
      return { error: 'メールアドレスとパスワードを入力してください' };
    }

    // authApi.tsのlogin関数を使用して統一性を確保
    const response = await login(email, password);

    const responseData = await response.json();
    console.log('ログイン成功:', responseData);

    // 認証成功時はマイページにリダイレクト
    // HttpOnly Cookieはサーバー側で設定される
    return redirect('/mypage');
  } catch (error) {
    console.error('ログインエラー:', error);

    // ApiErrorの場合はエラーメッセージを使用
    if (error instanceof Error && 'detail' in error) {
      const apiError = error as Error & { detail?: string };
      return { error: apiError.detail || error.message };
    }

    return {
      error:
        'ログインに失敗しました。メールアドレスまたはパスワードが正しくありません。',
    };
  }
};

// LoginPage コンポーネント
export default function LoginPage() {
  const actionData = useActionData<{ error?: string }>();
  const [googleError, setGoogleError] = useState<string | null>(null);
  const [googleSuccess, setGoogleSuccess] = useState<string | null>(null);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Googleログイン成功時の処理
  const handleGoogleSuccess = (message: string) => {
    setGoogleSuccess(message);
    setGoogleError(null);
    // Googleログイン成功時、マイページにリダイレクト
    setTimeout(() => {
      window.location.href = '/mypage';
    }, 1000);
  };

  // Googleログインエラー時の処理
  const handleGoogleError = (error: string) => {
    setGoogleError(error);
    setGoogleSuccess(null);
  };

  // Googleログイン開始時の処理
  const handleGoogleLoginStart = () => {
    setIsGoogleLoading(true);
    setGoogleError(null);
    setGoogleSuccess(null);
  };

  // Googleログイン終了時の処理
  const handleGoogleLoginEnd = () => {
    setIsGoogleLoading(false);
  };

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1
            className="text-xl font-semibold text-center mb-6"
            data-cy="login-title"
          >
            ログイン
          </h1>

          {/* エラーメッセージ表示 */}
          {(actionData?.error || googleError) && (
            <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md">
              {actionData?.error || googleError}
            </div>
          )}

          {/* 成功メッセージ表示 */}
          {googleSuccess && (
            <div className="mb-4 text-sm text-green-700 border border-green-300 bg-green-50 p-3 rounded-md">
              {googleSuccess}
            </div>
          )}

          {/* Googleログインボタン */}
          <div className="mb-4">
            <GoogleLoginButton
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              onLoginStart={handleGoogleLoginStart}
              onLoginEnd={handleGoogleLoginEnd}
              disabled={isGoogleLoading}
            />
          </div>

          {/* 区切り線 */}
          <div className="relative mb-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-2 text-gray-500">または</span>
            </div>
          </div>

          {/* メールログインフォーム */}
          <LoginForm />

          {/* フッターリンク */}
          <div className="mt-6 text-center space-y-2">
            <Link
              to="/send-reset-password-email"
              className="text-muted-foreground hover:underline text-sm block"
              data-cy="forgot-password-link"
            >
              パスワードを忘れた場合はこちら
            </Link>
            <Link
              to="/signup"
              className="text-muted-foreground hover:underline text-sm block"
              data-cy="signup-link"
            >
              新規会員登録はこちら
            </Link>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
