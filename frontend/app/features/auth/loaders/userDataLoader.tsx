import { AuthenticationError } from '../errors/AuthenticationError';
import { getUser } from '../apis/authApi';

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
    // 実際のバックエンドAPIからユーザー情報を取得
    const userData = await getUser(request);

    // ログインが必須の画面では下記でエラーがスローされる
    if (loginRequired && !userData) {
      throw new AuthenticationError('認証情報の取得に失敗しました。');
    }

    return userData;
  } catch (error) {
    // 認証エラーの場合はAuthenticationErrorとして処理
    if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
      if (loginRequired) {
        throw new AuthenticationError('認証情報の取得に失敗しました。');
      }
      return null;
    }
    throw error;
  }
}
