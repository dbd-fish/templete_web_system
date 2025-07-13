import { ActionFunction, redirect, Link } from 'react-router';
import { useActionData } from 'react-router';
import LoginForm from '~/features/auth/components/LoginForm';
import { authenticateUser, MOCK_ACCESS_TOKEN } from '~/mocks/data/auth';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';

// アクション関数
export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    // モック認証情報で直接認証
    const user = authenticateUser(email, password);

    if (user) {
      // 認証成功時はCookieを設定してリダイレクト
      const cookieString = `authToken=${MOCK_ACCESS_TOKEN}; HttpOnly; Secure; SameSite=Lax; Path=/`;

      return redirect('/mypage', {
        headers: { 'Set-Cookie': cookieString },
      });
    } else {
      return { error: 'メールアドレスまたはパスワードが正しくありません' };
    }
  } catch (error) {
    console.error('ログインエラー:', error);
    return { error: 'ログインに失敗しました' };
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
