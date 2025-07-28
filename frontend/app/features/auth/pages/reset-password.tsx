import {
  useActionData,
  redirect,
  ActionFunction,
  LoaderFunction,
} from 'react-router';
import ResetPasswordForm from '~/features/auth/components/ResetPasswordForm';
import { resetPassword } from '~/features/auth/apis/authApi';
import {
  isPasswordValid,
  getAllowedSymbols,
} from '~/features/auth/passwordValidation';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';

// ローダー関数: URLクエリからトークンを取得
export const loader: LoaderFunction = async ({ request }) => {
  const url = new URL(request.url);
  const token = url.searchParams.get('token');
  if (!token) {
    throw new Response('トークンが見つかりません。', { status: 400 });
  }
  return { token };
};

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const newPassword = formData.get('newPassword') as string;
  const confirmPassword = formData.get('confirmPassword') as string;

  // URLクエリからトークンを取得
  const url = new URL(request.url);
  const token = url.searchParams.get('token');

  try {
    // トークン存在チェック
    if (!token) {
      return new Response(
        JSON.stringify({
          error:
            'リセット用トークンが見つかりません。リンクが正しいか確認してください。',
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // 入力値バリデーション
    if (!newPassword || !confirmPassword) {
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
    if (newPassword !== confirmPassword) {
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

    // パスワード強度バリデーション
    const allowedSymbols = getAllowedSymbols();
    if (!isPasswordValid(newPassword)) {
      return new Response(
        JSON.stringify({
          error: `新しいパスワードが無効です。\n条件を満たしていません。\n\n・ 8文字以上\n・ 大文字・小文字\n・ 数字\n・ 次の記号のいずれかを含む必要があります:\n\t${allowedSymbols}`,
        }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    // パスワードリセット処理
    await resetPassword(token, newPassword);
    return redirect('/reset-password-complete');
  } catch (error) {
    console.error('Reset password error:', error);
    return new Response(
      JSON.stringify({
        error:
          error instanceof Error && error.message
            ? error.message
            : 'パスワードリセットに失敗しました。トークンが無効または期限切れの可能性があります。',
      }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  }
};

export default function ResetPasswordPage() {
  const actionData = useActionData<{ error?: string }>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-xl font-semibold text-center mb-4">
            新しいパスワードを設定
          </h1>
          <div className="mb-4 text-center">
            <p className="text-sm text-muted-foreground">
              新しいパスワードを入力してください。
              <br />
              セキュリティのため、強力なパスワードを設定してください。
            </p>
          </div>
          {actionData?.error && (
            <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md whitespace-pre-wrap">
              {actionData.error}
            </div>
          )}
          <ResetPasswordForm />
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              リセットをキャンセルする場合は{' '}
              <a href="/login" className="text-primary hover:underline">
                ログインページ
              </a>
              に戻ってください
            </p>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
