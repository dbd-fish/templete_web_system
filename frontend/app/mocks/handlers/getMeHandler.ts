import { http, HttpResponse } from 'msw';
import { UserResponse, ErrorResponse } from '../../commons/utils/types';
import { getUserFromToken } from '../data/auth';
import { MOCK_USER } from '../data/users';
import { MOCK_ACCESS_TOKEN, MSG_USER_INFO_SUCCESS, MSG_INVALID_TOKEN, COOKIE_AUTH_TOKEN } from '../data/constants';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse } from '../utils/mockHelpers';

// /api/v1/auth/me エンドポイントへのPOSTリクエストを処理するハンドラー
export const getMeHandler = http.post(
  'http://localhost:5173/api/v1/auth/me',
  async ({ request, cookies }) => {
    await addDefaultDelay();

    logMockHandler('getMeHandler', 'POST', request.url);

    // CookieからJWTを取得
    const authToken = cookies[COOKIE_AUTH_TOKEN];

    if (!authToken) {
      // JWTが存在しない場合はエラーレスポンスを返す
      const errorResponse: ErrorResponse = {
        detail: 'Unauthorized',
        status_code: 401
      };
      
      logMockResponse('getMeHandler', 401, errorResponse);
      return HttpResponse.json(errorResponse, { status: 401 });
    }

    // トークンからユーザー情報を取得
    const user = getUserFromToken(authToken);
    
    if (user) {
      logMockResponse('getMeHandler', 200, { success: true, user: user.email });
      return createSuccessResponse(MSG_USER_INFO_SUCCESS, user);
    } else {
      const errorResponse: ErrorResponse = {
        detail: MSG_INVALID_TOKEN,
        status_code: 403
      };
      
      logMockResponse('getMeHandler', 403, errorResponse);
      return createErrorResponse(MSG_INVALID_TOKEN, 403);
    }
  },
);
