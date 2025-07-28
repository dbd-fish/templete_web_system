import { Link } from 'react-router';
import { LoaderFunction } from 'react-router';
import { CheckCircle, XCircle } from 'lucide-react';
import { signup } from '~/features/auth/apis/authApi';
import { useLoaderData } from 'react-router';
import { LoaderDataType } from '~/utils/types';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';
import { Button } from '~/components/ui/button';

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  try {
    // GetクエリからTokenを取得
    const url = new URL(request.url);
    const token = url.searchParams.get('token');
    if (!token) {
      throw new Response('トークンが見つかりません', { status: 400 });
    }

    const response = await signup(token);
    // レスポンスステータスに応じてメッセージを設定
    let signupData;
    if (response) {
      signupData = {
        success: true,
      };
    } else {
      signupData = {
        success: false,
      };
    }
    const responseBody = {
      signupData: signupData,
    };

    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    throw new Response('本登録に失敗しました。', {
      status: 400,
    });
  }
};

export default function SignupVerifyCompete() {
  // ローダーデータから success と message を取得
  const loaderData = useLoaderData<LoaderDataType>();
  const isSuccess = loaderData.signupData?.success;

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <div className="text-center">
            {isSuccess ? (
              <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            ) : (
              <XCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
            )}
            <h1 className="text-xl font-semibold mb-4">
              {isSuccess ? '本登録が完了しました' : '本登録に失敗しました'}
            </h1>
          </div>

          <div className="text-center mb-6 space-y-3">
            {isSuccess ? (
              <>
                <p className="text-sm text-muted-foreground">
                  ご登録ありがとうございます。
                </p>
                <p className="text-sm text-muted-foreground">
                  本登録が正常に完了しました。
                </p>
                <p className="text-sm font-medium">
                  早速ログインしてサービスをご利用ください。
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-destructive">
                  本登録に失敗しました。
                </p>
                <p className="text-sm text-muted-foreground">
                  仮登録からやり直してください。
                </p>
                <p className="text-sm text-muted-foreground">
                  それでも登録できない場合は
                  <br />
                  別メールアドレスで試してください。
                </p>
              </>
            )}
          </div>

          <div className="text-center">
            <Button asChild className="w-full">
              <Link to={isSuccess ? '/login' : '/signup'}>
                {isSuccess ? 'ログインページへ' : '仮登録ページへ戻る'}
              </Link>
            </Button>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
