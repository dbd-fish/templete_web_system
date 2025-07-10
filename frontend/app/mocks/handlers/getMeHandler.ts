import { http, HttpResponse } from 'msw';

// ユーザー情報のモックデータ
const MOCK_USER = {
  username: 'mockuser',
  email: 'mockuser@example.com',
};

// /api/get/me エンドポイントへのPOSTリクエストを処理するハンドラー
export const getMeHandler = http.post(
  'http://localhost:5173/api/auth/me',
  ({ cookies }) => {

    // クッキー情報をログに記録

    // CSRFトークンを取得してログに記録
    // const csrfToken = cookies.csrftoken;

    // CookieからJWTを取得
    const authToken = cookies.authToken;

    if (!authToken) {
      // JWTが存在しない場合はエラーレスポンスを返す
      return HttpResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }

    // JWTの簡易的なバリデーション（モック処理のため省略可能）

    // NOTE: 本来はJWTの検証処理してJWTから認証情報を取り出すが、モックでは省略
    // JWTのバリデーション（簡略化）
    // const authToken = 'your_jwt_token';
    // if (authToken === 'your_jwt_token') {
    //   console.log('/api/get/me jwt yes', authToken);
    return HttpResponse.json(MOCK_USER, { status: 200 });
    // } else {
    //   console.log('/api/get/me jwt', authToken);
    //   return HttpResponse.json({ message: 'Invalid token' }, { status: 403 });
    // }
  },
);
