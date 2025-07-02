import { http, HttpResponse } from 'msw';
// import logger from '~/commons/utils/logger';

// ユーザー情報のモックデータ
const MOCK_USER = {
  username: 'mockuser',
  email: 'mockuser@example.com',
};

// /api/get/me エンドポイントへのPOSTリクエストを処理するハンドラー
export const getMeHandler = http.post(
  'http://localhost:5173/api/auth/me',
  ({ cookies }) => {
    // logger.info('[getMeHandler] start');

    // クッキー情報をログに記録
    // logger.debug('[getMeHandler] Cookies', { cookies: cookies });

    // CSRFトークンを取得してログに記録
    // const csrfToken = cookies.csrftoken;
    // logger.debug('[getMeHandler] CSRF token', { csrfToken: csrfToken });

    // CookieからJWTを取得
    const authToken = cookies.authToken;
    // logger.debug('[getMeHandler] Auth token', { authToken: authToken });

    if (!authToken) {
      // JWTが存在しない場合はエラーレスポンスを返す
      // logger.warn('[getMeHandler] No auth token provided');
      return HttpResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }

    // JWTの簡易的なバリデーション（モック処理のため省略可能）
    // logger.info(
    //   '[getMeHandler] Authentication successful, returning mock user data',
    // );
    // logger.debug('[getMeHandler] Mock user data', { user: MOCK_USER });

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
