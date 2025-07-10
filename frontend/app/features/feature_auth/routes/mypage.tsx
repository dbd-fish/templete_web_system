import { LoaderFunction, ActionFunction, redirect } from 'react-router';
import { useLoaderData } from 'react-router';
import ProfileCard from '~/features/feature_auth/components/ProfileCard';
import { userDataLoader } from '~/features/feature_auth/loaders/userDataLoader';
import { authTokenLoader } from '~/features/feature_auth/loaders/authTokenLoader';
import { AuthenticationError } from '~/commons/utils/errors/AuthenticationError';
import { logoutAction } from '~/features/feature_auth/actions/logoutAction';
import { LoaderDataType } from '~/commons/utils/types';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  try {
    // throw new Error('Error occurred in MyPage Loader');
    await authTokenLoader(request);
    const userData = await userDataLoader(request);


    const responseBody = {
      user: userData,
    };
    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    if (error instanceof AuthenticationError) {
      return redirect('/login');
    }


    throw new Response('ユーザーデータの取得に失敗しました。', {
      status: 400,
    });
  } finally {
  }
};

/**
 * アクション関数:
 * - クライアントからのアクションを処理
 * - ログアウトやその他のアクションを処理
 */
export const action: ActionFunction = async ({ request }) => {
  try {
    const formData = await request.formData();
    const actionType = formData.get('_action');


    if (actionType === 'logout') {
      const response = await logoutAction(request);
      return response;
    }

    throw new Response('サーバー上で不具合が発生しました', {
      status: 400,
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    throw new Response('サーバー上で予期しないエラーが発生しました', {
      status: 400,
    });
  } finally {
  }
};

/**
 * マイページコンポーネント:
 * - ユーザー情報を表示するページ
 */
export default function MyPage() {
  const loaderData = useLoaderData<LoaderDataType>();

  return (
    <Layout>
      <Main>
        <div className="w-full max-w-4xl bg-white rounded-lg shadow-md p-8">
          <div className="flex flex-col md:flex-row items-center justify-center space-y-6 md:space-y-0 md:space-x-6">
            <ProfileCard />
            <div className="w-full md:w-2/3 bg-gray-50 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">概要</h2>
              <p className="text-gray-600">
                {/* loaderDataの中にuserが存在するか確認するためオプショナルチェーン (?.)をつける */}
                名前: {loaderData.user?.username}
                <br />
                メール: {loaderData.user?.email}
                <br />
                あなたのアカウント情報や、活動の概要をここに表示します。好きな項目をクリックして更新したり、詳細を確認してください。
              </p>
            </div>
          </div>
        </div>
      </Main>
    </Layout>
  );
}
