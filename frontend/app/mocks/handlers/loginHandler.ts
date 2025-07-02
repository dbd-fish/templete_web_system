// MSW（Mock Service Worker）から必要なモジュールをインポート
import { http, HttpResponse } from 'msw';
// import logger from '.~/commons/utils/logger';

// ログインリクエストのボディの型定義
export interface LoginRequestBody {
  email: string; // ユーザーのメールアドレス
  password: string; // ユーザーのパスワード
}

// 許可されたメールアドレスとパスワードを定義
const VALID_EMAIL = 'user@example.com';
const VALID_PASSWORD = 'securepassword';

// /api/login エンドポイントへのPOSTリクエストを処理するハンドラーを定義
export const loginHandler = http.post(
  'http://localhost:5173/api/login',
  async ({ request }) => {
    try {
      // logger.info(`[loginHandler] start`);

      // NOTE: リクエストのクローンを作成して、非同期でリクエストボディを取得
      const clonedRequest = request.clone();
      const rawBody = await clonedRequest.text(); // JSON文字列として取得
      const body = JSON.parse(rawBody) as LoginRequestBody;

      const { email, password } = body;

      // 受け取ったメールアドレスとパスワードをログに記録
      // logger.debug(`[loginHandler] Received email`, { email: email });
      // logger.debug(`[loginHandler] Received password`, {
      //   password: password,
      // });

      // メールアドレスとパスワードの検証
      if (email === VALID_EMAIL && password === VALID_PASSWORD) {
        // 検証が成功した場合、JWT（JSON Web Token）を生成
        const jwt = 'your_jwt_token'; // 実際の実装では、適切な方法でJWTを生成してください

        // クッキーの設定を定義
        const setCookieHeader = `authToken=${jwt}; HttpOnly; Secure; SameSite=Lax; Path=/`;

        // logger.info(`[loginHandler] Authentication successful, returning JWT`);

        // 成功レスポンスを返す
        return new HttpResponse(
          JSON.stringify({ message: 'Logged in successfully' }),
          {
            status: 200,
            headers: {
              'Content-Type': 'application/json', // レスポンスの内容がJSONであることを示す
              'Set-Cookie': setCookieHeader, // クライアントにJWTを含むクッキーを設定
              'Access-Control-Allow-Origin': 'http://localhost:5173', // クライアントのオリジンを許可
              'Access-Control-Allow-Credentials': 'true', // クッキーを含むリクエストを許可
            },
          },
        );
      } else {
        // 認証情報が無効な場合のエラーレスポンス
        // logger.warn(`[loginHandler] Invalid credentials`, { email: email });

        return new HttpResponse(
          JSON.stringify({ message: 'ユーザ名またはパスワードが違います' }),
          {
            status: 401,
            headers: {
              'Content-Type': 'application/json',
            },
          },
        );
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      // リクエストボディのパース中にエラーが発生した場合の処理
      // logger.error(`[loginHandler] Error parsing request body`, {
      //   error: error,
      // });

      // エラーレスポンスを返す
      return new HttpResponse(
        JSON.stringify({ message: 'Invalid request body' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      );
    } finally {
      // logger.info(`[loginHandler] end`);
    }
  },
);
