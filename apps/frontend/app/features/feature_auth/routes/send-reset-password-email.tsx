import { useActionData, redirect, ActionFunction } from 'react-router';
import SendResetPasswordForm from '~/features/feature_auth/components/SendResetPasswordForm';
import { fetchSendResetPasswordData } from '~/features/feature_auth/apis/fetchSendResetPasswordData';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const email = formData.get('email') as string;

  try {
    // パスワードリセットメール送信処理
    Promise.resolve(fetchSendResetPasswordData(email)).catch((error) => {
      console.error('Error sending password-reset email:', error);
    });

    return redirect('/send-reset-password-email-complete');
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

export default function SendResetPasswordEmail() {
  const actionData = useActionData<{ error?: string }>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">
            パスワードリセット
          </h1>
          {actionData?.error && (
            <div
              className="mb-4 text-sm text-red-500 border border-red-400 bg-red-100 px-4 py-2 rounded whitespace-pre-wrap"
              style={{ whiteSpace: 'pre-wrap' }}
            >
              {actionData.error}
            </div>
          )}
          <SendResetPasswordForm />
        </SimpleCard>
      </Main>
    </Layout>
  );
}
