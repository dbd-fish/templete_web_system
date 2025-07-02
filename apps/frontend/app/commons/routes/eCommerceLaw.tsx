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

export default function eCommerceLaw() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow bg-gray-100 py-8">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            特定商取引法に基づく表記
          </h1>
          <p className="text-gray-600 text-sm text-center mb-8">
            （最終更新日：2025年1月26日）
          </p>
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                販売事業者
              </h2>
              <p className="text-gray-600 leading-relaxed">株式会社〇〇</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                販売責任者
              </h2>
              <p className="text-gray-600 leading-relaxed">
                代表取締役 〇〇〇〇
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                所在地
              </h2>
              <p className="text-gray-600 leading-relaxed">
                東京都渋谷区〇〇丁目〇〇番地〇〇
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                電話番号
              </h2>
              <p className="text-gray-600 leading-relaxed">03-1234-5678</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                メールアドレス
              </h2>
              <p className="text-gray-600 leading-relaxed">
                support@example.com
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                商品の販売価格
              </h2>
              <p className="text-gray-600 leading-relaxed">
                商品ごとに表示される価格（税込）に基づきます。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                商品代金以外の必要料金
              </h2>
              <p className="text-gray-600 leading-relaxed">
                消費税および配送料がかかる場合があります。詳細は購入ページをご確認ください。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                お支払い方法
              </h2>
              <p className="text-gray-600 leading-relaxed">
                クレジットカード、銀行振込、電子マネーをご利用いただけます。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                商品の引き渡し時期
              </h2>
              <p className="text-gray-600 leading-relaxed">
                デジタル商品については、決済完了後、即時ダウンロード可能となります。物理商品はご注文から5営業日以内に発送いたします。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                返品・交換について
              </h2>
              <p className="text-gray-600 leading-relaxed">
                デジタル商品は性質上、返品を受け付けておりません。不良品や誤送の場合、商品到着後7日以内にお問い合わせください。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                特別な販売条件
              </h2>
              <p className="text-gray-600 leading-relaxed">
                特別な条件がある場合は、商品ごとの説明ページに明記します。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                問い合わせ窓口
              </h2>
              <p className="text-gray-600 leading-relaxed">
                上記「メールアドレス」または「電話番号」までお問い合わせください。
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
