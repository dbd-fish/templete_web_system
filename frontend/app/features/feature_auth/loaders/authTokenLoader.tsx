import { AuthenticationError } from '~/commons/utils/errors/AuthenticationError';
// import logger from '~/commons/utils/logger';

/**
 * リクエストヘッダーから認証トークンを取得して検証します。
 *
 * この関数は、リクエストヘッダー内のクッキーを解析して`authToken`を抽出します。
 * `authToken` が存在しない場合は認証エラーをスローします。
 *
 * @param {Request} request - 必要なヘッダーやクッキーを含むHTTPリクエストオブジェクト。
 * @throws {AuthenticationError} 認証トークン (`authToken`) が見つからない場合にスローされます。
 * @returns {Promise<void>} 成功した場合、特に値は返しません。
 */
export async function authTokenLoader(request: Request) {
  // logger.info('[authTokenLoader] start');
  try {
    // HTTP-only クッキーの取得
    const cookieHeader = request.headers.get('Cookie');
    // logger.debug('[authTokenLoader] Incoming cookies', {
    //   cookieHeader: cookieHeader,
    // });

    // authToken と csrfToken をクッキーから抽出
    const authTokenMatch = cookieHeader?.match(/authToken=([^;]+)/);
    // const csrfTokenMatch = cookieHeader?.match(/csrftoken=([^;]+)/);

    const authToken = authTokenMatch ? authTokenMatch[1] : null;
    // const csrfToken = csrfTokenMatch ? csrfTokenMatch[1] : null;

    // logger.debug('[authTokenLoader] Extracted authToken', {
    //   authToken: authToken,
    // });
    // logger.debug('[authTokenLoader] Extracted csrfToken', {
    //   csrfToken: csrfToken,
    // });

    // authToken が存在しない場合はログインページへリダイレクト
    if (!authToken) {
      // logger.info('[authTokenLoader] Missing authToken, throwing error.');
      throw new AuthenticationError('認証トークンが見つかりません。');
    }

    // logger.info('[authTokenLoader] completed successfully');
  } catch (error) {
    // logger.error('[authTokenLoader] Error occurred', {
    //   error: error,
    // });
    throw error;
  } finally {
    // logger.info('[authTokenLoader] end');
  }
}
