import { redirect } from 'react-router';
import { logout } from '~/features/feature_auth/apis/authApi';
import { authTokenCookie } from '~/features/feature_auth/cookies';

/**
 * ログアウト処理を実行するアクション関数。
 *
 * この関数は、ログアウトAPIを呼び出し、認証トークンを削除するための
 * クッキーを設定した後、ログインページにリダイレクトします。
 *
 * @param {Request} request - HTTPリクエストオブジェクト。クライアントから送信されたクッキーを含む。
 * @returns {Promise<Response>} ログインページへのリダイレクトレスポンス。
 *
 * @throws {Error} ログアウトAPI呼び出し中にエラーが発生した場合にスローされます。
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function logoutAction(request: Request) {
  try {
    // ログアウトAPIを呼び出し
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const response = await logout(request);

    // デバッグ用: レスポンスの内容をコンソールに出力
    // const authToken = response.headers.get('set-cookie'); // 仮定: fetchLoginDataがauthTokenを返す

    // デバッグ用: クライアントから送信された既存のクッキーを取得
    // const existingCookiesHeader = request.headers.get('Cookie');

    // Cookieを破棄するためにmax-age=0のCookieを作成
    const setCookieHeader = await authTokenCookie.serialize('', {});

    return redirect('/login', {
      headers: {
        'Set-Cookie': setCookieHeader,
      },
    });
  } catch (error) {
    throw error;
  }
}
