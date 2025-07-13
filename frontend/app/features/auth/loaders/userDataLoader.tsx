import { AuthenticationError } from '../errors/AuthenticationError';
import { getUserFromToken } from '~/mocks/data/auth';

/**
 * 認証情報を取得します。
 *
 * @param {Request} request - 必要なヘッダーやクッキーを含むHTTPリクエストオブジェクト。
 * @param {boolean} [loginRequired=true] - 呼び出し元がログインを必須とするかどうかを示すフラグ。
 *     true の場合、認証情報が取得できないとエラーをスローします。
 * @throws {AuthenticationError} 認証情報が見つからず、`loginRequired` が true の場合にスローされます。
 * @returns {Promise<any>} 取得した認証情報。
 */
export async function userDataLoader(
  request: Request,
  loginRequired: boolean = true,
) {
  try {
    // Cookieから認証トークンを取得
    const cookieHeader = request.headers.get('Cookie');
    let authToken = null;

    if (cookieHeader) {
      const cookies = cookieHeader.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
      }, {} as Record<string, string>);

      authToken = cookies.authToken;
    }

    // トークンからユーザー情報を取得
    const userData = authToken ? getUserFromToken(authToken) : null;

    // ログインが必須の画面では下記でエラーがスローされる
    if (loginRequired && !userData) {
      throw new AuthenticationError('認証情報の取得に失敗しました。');
    }

    return userData;
  } catch (error) {
    throw error;
  }
}
