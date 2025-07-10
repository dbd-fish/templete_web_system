
/**
 * ユーザー情報を取得する非同期関数
 * - '/api/get/me' エンドポイントからユーザー情報を取得
 * - 成功時: ユーザー情報オブジェクトを返す
 * - 失敗時: null を返す
 */
export const fetchUserData = async (request: Request) => {

  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  const cookieHeader = request.headers.get('Cookie');

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

      return { username: data.username, email: data.email };
    } else {
      return null;
    }
  } catch (error) {
    throw error;
  } finally {
  }
};
