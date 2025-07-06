// import logger from '~/commons/utils/logger';

/**
 * ユーザー情報を取得する非同期関数
 * - '/api/get/me' エンドポイントからユーザー情報を取得
 * - 成功時: ユーザー情報オブジェクトを返す
 * - 失敗時: null を返す
 */
export const fetchUserData = async (request: Request) => {
  // logger.info('[fetchUserData] start');

  const apiUrl = process.env.API_URL; // 環境変数からURLを取得
  // logger.debug('[fetchUserData] API URL', { apiUrl: apiUrl });

  const cookieHeader = request.headers.get('Cookie');
  // logger.debug('[fetchUserData] Cookie header', { cookieHeader: cookieHeader });

  try {
    const response = await fetch(`${apiUrl}/api/auth/me`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // NOTE: credentials: 'include'だけではなく下記のようにクッキーを明示的に渡さないとCookieが送信されない
        Cookie: cookieHeader || '', // 明示的にクッキーを渡す
      },
      credentials: 'include', // Cookieを送信
    });

    if (response.ok) {
      const data = await response.json();
      // logger.info('[fetchUserData] User data retrieved successfully');
      // logger.debug('[fetchUserData] User data', { data });

      return { username: data.username, email: data.email };
    } else {
      // logger.warn('[fetchUserData] Failed to retrieve user data', {
      //   status: response.status,
      //   statusText: response.statusText,
      // });
      return null;
    }
  } catch (error) {
    // logger.error('[fetchUserData] Unexpected error occurred', {
    //   error: error,
    // });
    throw error;
  } finally {
    // logger.info('[fetchUserData] end');
  }
};
