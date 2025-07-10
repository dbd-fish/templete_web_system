
/**
 * ユーザーのログアウトを処理する非同期関数
 * - '/api/logout' エンドポイントを使用してログアウトリクエストを送信
 * - 成功時: レスポンスを返す
 * - 失敗時: エラーメッセージをスロー
 */
export const fetchLogoutData = async (request: Request) => {

  // NOTE: processが使用できないため、API URLを直接指定
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  try {
    const cookieHeader = request.headers.get('Cookie');
    const response = await fetch(`${apiUrl}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookieHeader || '', // 明示的にクッキーを渡す
      },
      credentials: 'include', // HTTP-only Cookieを送信
    });

    if (response.ok) {
      // console.log('[fetchLogoutData] Logout successful');
      return response; // 必要に応じてデータを返す
    } else {
      const errorData = await response.json();
      // console.log('[fetchLogoutData] Logout failed', { errorData: errorData });

      throw new Error(errorData.message || 'ログアウトに失敗しました');
    }
  } catch (error) {

    throw error;
  } finally {
  }
};
