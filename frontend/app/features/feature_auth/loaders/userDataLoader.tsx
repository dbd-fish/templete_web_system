import { AuthenticationError } from '~/commons/utils/errors/AuthenticationError';
import { fetchUserData } from '~/features/feature_auth/apis/fetchUserData';
// import logger from '~/commons/utils/logger';

/**
 * 外部APIから認証情報を取得します。
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
  // logger.info('[userDataLoader] start', { loginRequired: loginRequired });
  try {
    // 外部API呼び出し
    // logger.info('[userDataLoader] Fetching user data with authToken', {
    //   loginRequired: loginRequired,
    // });
    const userData = await fetchUserData(request);
    // logger.debug('[userDataLoader] Retrieved user data', {
    //   userData: userData,
    // });

    // ログインが必須の画面では下記でエラーがスローされる
    if (loginRequired && !userData) {
      // logger.warn('[userDataLoader] User data not found.', { loginRequired: loginRequired });
      throw new AuthenticationError('認証情報の取得に失敗しました。');
    }

    // logger.info('[userDataLoader] completed successfully', {
    //   userDataExists: !!userData,
    // });
    return userData;
  } catch (error) {
    // logger.error('[userDataLoader] Error occurred', {
    //   error: error
    // });
    throw error;
  } finally {
    // logger.info('[userDataLoader] end');
  }
}
