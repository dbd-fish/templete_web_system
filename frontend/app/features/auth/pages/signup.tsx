import {
  useActionData,
  redirect,
  ActionFunction,
  MetaFunction,
} from 'react-router';
import { useState } from 'react';
import SignupForm from '~/features/auth/components/SignupForm';
import GoogleLoginButton from '~/features/auth/components/GoogleLoginButton';
import { sendVerifyEmail } from '~/features/auth/apis/authApi';
import {
  isPasswordValid,
  getAllowedSymbols,
} from '~/features/auth/passwordValidation';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';

/**
 * メタデータ関数:
 * - ページのタイトルとメタデータを設定
 */
export const meta: MetaFunction = () => {
  return [
    { title: 'アカウント登録 | Webシステム開発テンプレート' },
    {
      name: 'description',
      content: '新しいアカウントを作成します。メールアドレス認証が必要です。',
    },
  ];
};

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;
  const confirmPassword = formData.get('confirmPassword') as string;
  const username = formData.get('username') as string;

  try {
    // 入力値バリデーション
    if (!email || !password || !confirmPassword || !username) {
      return new Response(
        JSON.stringify({
          error: 'すべての項目を入力してください。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // パスワード一致チェック
    if (password !== confirmPassword) {
      return new Response(
        JSON.stringify({
          error: 'パスワードが一致しません。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // パスワードバリデーション
    const allowedSymbols = getAllowedSymbols();
    if (!isPasswordValid(password)) {
      return new Response(
        JSON.stringify({
          error: `パスワードが無効です。\n条件を満たしていません。\n\n・ 8文字以上\n・ 大文字・小文字\n・ 数字\n・ 次の記号のいずれかを含む必要があります:\n\t${allowedSymbols}`,
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // ユーザー名の長さチェック
    if (username.length < 2 || username.length > 50) {
      return new Response(
        JSON.stringify({
          error: 'ユーザー名は2文字以上50文字以内で入力してください。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // 会員登録用の確認メール送信
    await sendVerifyEmail(email, password, username);
    return redirect('/send-signup-email');
  } catch (error) {
    console.error('Signup error:', error);
    return new Response(
      JSON.stringify({
        error:
          error instanceof Error && error.message
            ? error.message
            : '会員登録に失敗しました。再度お試しください。',
      }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  }
};

export default function SignupPage() {
  const actionData = useActionData<{ error?: string }>();
  const [googleError, setGoogleError] = useState<string | null>(null);
  const [googleSuccess, setGoogleSuccess] = useState<string | null>(null);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Googleサインアップ成功時の処理
  const handleGoogleSuccess = (message: string) => {
    setGoogleSuccess(message);
    setGoogleError(null);
    // Googleサインアップ成功時、マイページにリダイレクト
    setTimeout(() => {
      window.location.href = '/mypage';
    }, 1000);
  };

  // Googleサインアップエラー時の処理
  const handleGoogleError = (error: string) => {
    setGoogleError(error);
    setGoogleSuccess(null);
  };

  // Googleサインアップ開始時の処理
  const handleGoogleSignupStart = () => {
    setIsGoogleLoading(true);
    setGoogleError(null);
    setGoogleSuccess(null);
  };

  // Googleサインアップ終了時の処理
  const handleGoogleSignupEnd = () => {
    setIsGoogleLoading(false);
  };

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1
            className="text-xl font-semibold text-center mb-6"
            data-cy="signup-title"
          >
            会員登録
          </h1>

          {/* エラーメッセージ表示 */}
          {(actionData?.error || googleError) && (
            <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md whitespace-pre-wrap">
              {actionData?.error || googleError}
            </div>
          )}

          {/* 成功メッセージ表示 */}
          {googleSuccess && (
            <div className="mb-4 text-sm text-green-700 border border-green-300 bg-green-50 p-3 rounded-md">
              {googleSuccess}
            </div>
          )}

          {/* Googleサインアップボタン */}
          <div className="mb-4">
            <GoogleLoginButton
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              onLoginStart={handleGoogleSignupStart}
              onLoginEnd={handleGoogleSignupEnd}
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

          {/* メールサインアップフォーム */}
          <SignupForm />

          {/* フッターリンク */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              既にアカウントをお持ちの方は{' '}
              <a
                href="/login"
                className="text-primary hover:underline"
                data-cy="signup-login-link"
              >
                こちらからログイン
              </a>
            </p>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
