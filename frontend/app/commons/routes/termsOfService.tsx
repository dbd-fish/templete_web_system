import Header from '~/commons/components/Header';
import Footer from '~/commons/components/Footer';
import { LoaderFunction, redirect, ActionFunction } from 'react-router';
import { userDataLoader } from '~/features/feature_auth/loaders/userDataLoader';
import { AuthenticationError } from '~/commons/utils/errors/AuthenticationError';
import { logoutAction } from '~/features/feature_auth/actions/logoutAction';
// import logger from '~/commons/utils/logger';

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  // logger.info('[Home Loader] start');
  try {
    const userData = await userDataLoader(request, false);
    const responseBody = {
      user: userData,
    };
    // logger.info('[Home Loader] Successfully retrieved user data');
    // logger.debug('[Home Loader] User data', { userData });

    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    if (error instanceof AuthenticationError) {
      // logger.warn('[Home Loader] AuthenticationError occurred');
      return redirect('/login');
    }

    // logger.error('[Home Loader] Unexpected error occurred', {
    //   error: error,
    // });

    throw new Response('ユーザーデータの取得に失敗しました。', {
      status: 400,
    });
  } finally {
    // logger.info('[Home Loader] end');
  }
};

// NOTE: ログアウトが必要な画面ではこれと似たAction関数を実装する必要あり
/**
 * アクション関数:
 * - クライアントからのアクションを処理
 * - ログアウトやその他のアクションを処理
 */
export const action: ActionFunction = async ({ request }) => {
  // logger.info('[Home Action] start');
  try {
    const formData = await request.formData();
    const actionType = formData.get('_action');

    // logger.debug('[Home Action] Received actionType', { actionType });

    if (actionType === 'logout') {
      const response = await logoutAction(request);
      // logger.info('[Home Action] Logout action processed successfully');
      return response;
    }

    // logger.warn('[Home Action] No valid actionType provided');
    throw new Response('サーバー上で不具合が発生しました', {
      status: 400,
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    // logger.error('[Home Action] Unexpected error occurred', {
    //   error: error
    // });
    throw new Response('サーバー上で予期しないエラーが発生しました', {
      status: 400,
    });
  } finally {
    // logger.info('[Home Action] end');
  }
};

export default function termsOfService() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow bg-gray-100 py-8">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            サービス利用規約
          </h1>
          <p className="text-gray-600 text-sm text-center mb-8">
            （最終更新日：2025年1月26日）
          </p>
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第1条（適用範囲）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                本規約は、本サービスの利用に関する当社とユーザーとの間の一切の関係に適用されます。また、当社が定める個別規定は、本規約の一部を構成します。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第2条（アカウントの登録）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                ユーザーは、本サービスを利用するために正確かつ最新の情報を提供するものとし、不正確な情報による損害について当社は責任を負いません。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第3条（個人情報の取り扱い）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                当社は、ユーザーの個人情報を個人情報保護法およびプライバシーポリシーに基づき取り扱います。
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li>サービス提供および運営</li>
                <li>お問い合わせへの対応</li>
                <li>ポイント購入および決済処理</li>
                <li>法令に基づく対応</li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第4条（ポイントの購入）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                ユーザーは、購入したポイントを返金不可であることに同意します。有効期限は購入日から1年間とし、期限を過ぎたポイントは失効します。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第5条（禁止事項）
              </h2>
              <ul className="list-disc list-inside text-gray-600">
                <li>法令または公序良俗に違反する行為</li>
                <li>不正行為またはポイントの不正利用</li>
                <li>虚偽の情報を提供する行為</li>
                <li>システムへの不正アクセス</li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第6条（サービス内容の変更および中断）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                当社は、システム保守や天災地変などの理由により、本サービスの内容を変更または中断することができます。これによる損害について当社は責任を負いません。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第7条（お問い合わせ窓口）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                本規約に関するお問い合わせは以下までご連絡ください：
              </p>
              <ul className="list-none text-gray-600 mt-2">
                <li>会社名: 株式会社〇〇</li>
                <li>担当者: 利用規約管理担当</li>
                <li>メールアドレス: support@example.com</li>
                <li>電話番号: 03-1234-5678</li>
                <li>住所: 東京都渋谷区〇〇丁目〇〇番地〇〇</li>
              </ul>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
