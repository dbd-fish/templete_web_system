import { useActionData, redirect, ActionFunction } from 'react-router';
import SignupForm from '~/features/feature_auth/components/SignupForm';
import { fetchSendVerifyEmailData } from '~/features/feature_auth/apis/fetchSendVerifyEmailData';
import {
  isPasswordValid,
  getAllowedSymbols,
} from '~/features/feature_auth/passwordValidation';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;
  const username = formData.get('username') as string;

  try {
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

    // 会員登録用の確認メール送信
    // 確認メール送信をバックグラウンドで処理
    Promise.resolve(fetchSendVerifyEmailData(email, password, username)).catch(
      (error) => {
        console.error('Error sending verification email:', error);
      },
    );
    return redirect('/send-signup-email');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    return new Response(
      JSON.stringify({ error: '会員登録に失敗しました。再度お試しください。' }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  }
};

export default function SignupPage() {
  const actionData = useActionData<{ error?: string }>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">
            会員登録
          </h1>
          {actionData?.error && (
            <div
              className="mb-4 text-sm text-red-500 border border-red-400 bg-red-100 px-4 py-2 rounded whitespace-pre-wrap"
              style={{ whiteSpace: 'pre-wrap' }}
            >
              {actionData.error}
            </div>
          )}
          <SignupForm />
        </SimpleCard>
      </Main>
    </Layout>
  );
}
