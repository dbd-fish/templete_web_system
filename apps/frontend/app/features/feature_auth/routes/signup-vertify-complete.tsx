import { Link } from 'react-router';
import { LoaderFunction } from 'react-router';
import { fetchSignupData } from '~/features/feature_auth/apis/fetchSignupData';
import { useLoaderData } from 'react-router';
import { LoaderDataType } from '~/commons/utils/types';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  // logger.info('[SignupVerifyCompete Loader] start');
  try {
    // GetクエリからTokenを取得
    const url = new URL(request.url);
    const token = url.searchParams.get('token');
    if (!token) {
      throw new Response('トークンが見つかりません', { status: 400 });
    }

    const response = await fetchSignupData(token);
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
    // logger.info('[SignupVerifyCompete Loader] Successfully retrieved user data');

    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    // logger.error('[SignupVerifyCompete Loader] Unexpected error occurred', {
    //   error: error,
    // });

    throw new Response('本登録に失敗しました。', {
      status: 400,
    });
  } finally {
    // logger.info('[SignupVerifyCompete Loader] end');
  }
};

export default function SignupVerifyCompete() {
  // ローダーデータから success と message を取得
  const loaderData = useLoaderData<LoaderDataType>();

  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-center mb-6">
            {loaderData.signupData?.success
              ? '本登録が完了しました。'
              : '本登録に失敗しました。'}
          </h1>
          {loaderData.signupData?.success ? (
            <p className="text-center mb-6">
              ご登録ありがとうございます。本登録が正常に完了しました。
              <br />
              早速ログインしてサービスをご利用ください。
            </p>
          ) : (
            <div className="text-center mb-6">
              <p>本登録に失敗しました。</p>
              <p>仮登録からやり直してください。</p>
              <p>
                それでも登録できない場合は別メールアドレスで試してください。
              </p>
            </div>
          )}
          <div className="text-center">
            {loaderData.signupData?.success ? (
              <Link
                to="/login"
                className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md"
              >
                ログインページへ
              </Link>
            ) : (
              <Link
                to="/signup"
                className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md"
              >
                仮登録ページへ戻る
              </Link>
            )}
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
