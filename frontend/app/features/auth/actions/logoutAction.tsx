import { redirect } from 'react-router';
import { logout } from '~/features/auth/apis/authApi';

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
    const response = await logout(request);

    // バックエンドからのSet-Cookieヘッダーを取得
    const setCookieHeaders = response.headers.get('set-cookie');
    
    // バックエンドがauthTokenとrefreshTokenの両方を削除するSet-Cookieヘッダーを返す
    return redirect('/login', {
      headers: {
        ...(setCookieHeaders && { 'Set-Cookie': setCookieHeaders }),
      },
    });
  } catch (error) {
    throw error;
  }
}
