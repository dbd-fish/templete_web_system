import { ActionFunction, redirect, Link } from 'react-router';
import { useActionData } from 'react-router';
import LoginForm from '~/features/feature_auth/components/LoginForm';
import { fetchLoginData } from '~/features/feature_auth/apis/fetchLoginData';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

// アクション関数
export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    // fetchLoginDataを呼び出して認証処理
    const response = await fetchLoginData(email, password);
    const responseCookieHeader = response.headers.get('set-Cookie');
    if (!responseCookieHeader) {
      throw new Error('Cookieが見つかりません');
    }
    return redirect('/mypage', {
      headers: { 'Set-Cookie': responseCookieHeader },
    });
  } catch {
    return new Response(JSON.stringify({ error: 'ログインに失敗しました' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};

// LoginPage コンポーネント
export default function LoginPage() {
  const actionData = useActionData<{ error?: string }>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-xl font-semibold text-center mb-4">ログイン</h1>
          {actionData?.error && (
            <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md">
              {actionData.error}
            </div>
          )}
          <LoginForm />
          <div className="mt-4 text-center">
            <Link
              to="/send-reset-password-email"
              className="text-muted-foreground hover:underline"
            >
              パスワードを忘れた場合はこちら
            </Link>
            <Link
              to="/signup"
              className="text-muted-foreground hover:underline block mt-2"
            >
              新規会員登録はこちら
            </Link>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
