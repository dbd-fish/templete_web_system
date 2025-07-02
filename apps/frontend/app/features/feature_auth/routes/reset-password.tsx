import {
  useActionData,
  redirect,
  ActionFunction,
  LoaderFunction,
} from 'react-router';
import ResetPasswordForm from '~/features/feature_auth/components/ResetPasswordForm';
import { fetchResetPasswordData } from '~/features/feature_auth/apis/fetchResetPasswordData';
import {
  isPasswordValid,
  getAllowedSymbols,
} from '~/features/feature_auth/passwordValidation';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

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

  // URLクエリからトークンを取得
  const url = new URL(request.url);
  const token = url.searchParams.get('token');
  if (!token) {
    return new Response('Token is missing.', { status: 400 });
  }
  try {
    // パスワードバリデーション
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
    await fetchResetPasswordData(token, newPassword);
    return redirect('/reset-password-complete');
  } catch {
    return new Response(
      JSON.stringify({
        error: 'パスワードリセットに失敗しました。再度お試しください。',
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
          <h1 className="text-2xl font-bold text-center mb-4">
            パスワードリセット
          </h1>
          {actionData?.error && (
            <div className="mb-4 text-sm text-red-500 border border-red-400 bg-red-100 px-4 py-2 rounded">
              {actionData.error}
            </div>
          )}
          <ResetPasswordForm />
        </SimpleCard>
      </Main>
    </Layout>
  );
}
