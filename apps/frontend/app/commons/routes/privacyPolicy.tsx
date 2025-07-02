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

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow bg-gray-100 py-8">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            サービスプライバシーポリシー
          </h1>
          <p className="text-gray-600 text-sm text-center mb-8">
            （最終更新日：2025年1月26日）
          </p>
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第1条（個人情報の定義）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                「個人情報」とは、個人情報保護法において定義される「個人情報」を指し、氏名、生年月日、住所、電話番号、電子メールアドレス、その他の記述等により個人を識別できる情報を含みます。
              </p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第2条（個人情報の収集方法）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                当社は、以下の方法で個人情報を収集することがあります：
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li>
                  ユーザーが本サービスに登録する際に提供される情報（氏名、メールアドレス、住所、電話番号など）
                </li>
                <li>商品購入やお問い合わせの際に提供される情報</li>
                <li>
                  Googleアドセンスやアクセス解析ツールを通じて収集されるクッキー（Cookie）情報やアクセスログ
                </li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第3条（個人情報の利用目的）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                当社は、収集した個人情報を以下の目的で利用します：
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li>本サービスの提供および運営</li>
                <li>ユーザーからのお問い合わせへの対応（本人確認を含む）</li>
                <li>商品の配送および代金決済</li>
                <li>サービス向上を目的としたマーケティングや分析</li>
                <li>法令遵守のための対応</li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第4条（Googleアドセンスとクッキー）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                本サービスでは、第三者配信の広告サービス「Googleアドセンス」を利用しています。Googleを含む第三者広告配信事業者は、ユーザーのブラウザにクッキーを設定し、それを使用して広告を配信します。
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li>
                  クッキーによる情報収集を希望しない場合は、ブラウザの設定で無効化できます。ただし、一部のサービスが利用できなくなる場合があります。
                </li>
                <li>
                  Googleアドセンスの詳細については、{' '}
                  <a
                    href="https://policies.google.com/technologies/ads?hl=ja"
                    className="text-blue-500 hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Googleの広告に関するポリシー
                  </a>{' '}
                  をご参照ください。
                </li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第5条（個人情報の第三者提供）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                当社は、次の場合を除き、ユーザーの同意を得ることなく個人情報を第三者に提供しません：
              </p>
              <ul className="list-disc list-inside text-gray-600 mt-2">
                <li>法令に基づく場合</li>
                <li>
                  人の生命、身体または財産の保護のために必要がある場合で、本人の同意を得ることが困難な場合
                </li>
                <li>
                  公衆衛生の向上や児童の健全な育成の推進のために特に必要がある場合
                </li>
                <li>
                  国の機関や地方公共団体、またはその委託を受けた者が法令の定める事務を遂行することに対して協力する必要がある場合
                </li>
              </ul>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                第8条（お問い合わせ窓口）
              </h2>
              <p className="text-gray-600 leading-relaxed">
                本ポリシーに関するお問い合わせは、以下の窓口までご連絡ください：
              </p>
              <ul className="list-none text-gray-600 mt-2">
                <li>会社名: 株式会社〇〇</li>
                <li>担当者: 個人情報管理責任者</li>
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
