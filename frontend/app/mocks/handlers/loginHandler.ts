// MSW（Mock Service Worker）から必要なモジュールをインポート
import { http, HttpResponse } from 'msw';
import { LoginRequest, TokenData, ErrorResponse } from '../../commons/utils/types';
import { authenticateUser, MOCK_ACCESS_TOKEN, MSG_LOGIN_SUCCESS, MSG_AUTH_FAILED } from '../data/auth';
import { createResponseWithCookie, createErrorResponse, formDataToObject, addDefaultDelay, logMockHandler, logMockResponse } from '../utils/mockHelpers';

// ログインリクエストのボディの型定義（form-urlencoded用）
export interface LoginRequestBody {
  username: string; // OAuth2PasswordRequestFormでは"username"フィールドを使用
  password: string; // ユーザーのパスワード
}

// /api/v1/auth/login エンドポイントへのPOSTリクエストを処理するハンドラーを定義
export const loginHandler = http.post(
  'http://localhost:5173/api/v1/auth/login',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      // NOTE: OAuth2PasswordRequestFormはapplication/x-www-form-urlencodedでリクエストを送信
      const clonedRequest = request.clone();
      const formData = await clonedRequest.formData();
      const requestData = formDataToObject(formData);
      const { username, password } = requestData;

      logMockHandler('loginHandler', 'POST', request.url, { username });

      // 認証情報の検証
      const user = authenticateUser(username, password);
      
      if (user) {
        // 成功レスポンスを返す（OpenAPI仕様に準拠）
        const tokenData: TokenData = {
          access_token: MOCK_ACCESS_TOKEN,
          token_type: 'bearer'
        };
        
        const cookieString = `authToken=${MOCK_ACCESS_TOKEN}; HttpOnly; Secure; SameSite=Lax; Path=/`;
        
        logMockResponse('loginHandler', 200, { success: true, user: user.email });
        
        return createResponseWithCookie(MSG_LOGIN_SUCCESS, cookieString, tokenData);
      } else {
        // 認証情報が無効な場合のエラーレスポンス
        const errorResponse: ErrorResponse = {
          detail: MSG_AUTH_FAILED,
          status_code: 401
        };
        
        logMockResponse('loginHandler', 401, errorResponse);
        
        return new HttpResponse(
          JSON.stringify(errorResponse),
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
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('loginHandler', 400, errorResponse);
      
      return createErrorResponse('Invalid request body', 400);
    }
  },
);
