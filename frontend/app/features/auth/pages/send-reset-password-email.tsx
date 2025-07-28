import { useActionData, redirect, ActionFunction } from 'react-router';
import SendResetPasswordForm from '~/features/auth/components/SendResetPasswordForm';
import { sendPasswordResetEmail } from '~/features/auth/apis/authApi';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;

  try {
    // 入力値バリデーション
    if (!email) {
      return new Response(
        JSON.stringify({
          error: 'メールアドレスを入力してください。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // メールアドレス形式チェック
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return new Response(
        JSON.stringify({
          error: '有効なメールアドレスを入力してください。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // パスワードリセットメール送信処理
    await sendPasswordResetEmail(email);
    return redirect('/send-reset-password-email-complete');
  } catch (error) {
    console.error('Send password reset email error:', error);
    return new Response(
      JSON.stringify({
        error:
          error instanceof Error && error.message
            ? error.message
            : 'パスワードリセットメールの送信に失敗しました。再度お試しください。',
      }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  }
};

export default function SendResetPasswordEmail() {
  const actionData = useActionData<{ error?: string }>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-xl font-semibold text-center mb-4">
            パスワードリセット
          </h1>
          <div className="mb-4 text-center">
            <p className="text-sm text-muted-foreground">
              ご登録のメールアドレスを入力してください。
              <br />
              パスワード再設定用のURLをお送りします。
            </p>
          </div>
          {actionData?.error && (
            <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md">
              {actionData.error}
            </div>
          )}
          <SendResetPasswordForm />
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              ログインページに戻る場合は{' '}
              <a href="/login" className="text-primary hover:underline">
                こちら
              </a>
            </p>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
