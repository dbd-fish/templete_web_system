import { http, HttpResponse } from 'msw';
import { MessageResponse, ErrorResponse } from '../../commons/utils/types';
import { getUserFromToken, deleteAuthCookie, MSG_ACCOUNT_DELETE_SUCCESS, MSG_INVALID_TOKEN, COOKIE_AUTH_TOKEN } from '../data/auth';
import { createResponseWithCookie, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse } from '../utils/mockHelpers';

// /api/v1/auth/me エンドポイントへのDELETEリクエストを処理するハンドラー（アカウント削除）
export const deleteUserHandler = http.delete(
  'http://localhost:5173/api/v1/auth/me',
  async ({ request, cookies }) => {
    await addDefaultDelay();

    try {
      // 認証チェック
      const authToken = cookies[COOKIE_AUTH_TOKEN];
      if (!authToken) {
        const errorResponse: ErrorResponse = {
          detail: 'Unauthorized',
          status_code: 401
        };
        
        logMockResponse('deleteUserHandler', 401, errorResponse);
        return HttpResponse.json(errorResponse, { status: 401 });
      }

      // トークンからユーザー情報を取得
      const currentUser = getUserFromToken(authToken);
      if (!currentUser) {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 403
        };
        
        logMockResponse('deleteUserHandler', 403, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 403);
      }

      logMockHandler('deleteUserHandler', 'DELETE', request.url, { user: currentUser.email });

      // 成功レスポンスを返す
      const messageResponse: MessageResponse = {
        message: MSG_ACCOUNT_DELETE_SUCCESS
      };

      // 認証クッキーを削除
      const deleteCookieHeader = deleteAuthCookie();

      logMockResponse('deleteUserHandler', 200, { success: true });
      
      return createResponseWithCookie(MSG_ACCOUNT_DELETE_SUCCESS, deleteCookieHeader, messageResponse);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Internal server error',
        status_code: 500
      };
      
      logMockResponse('deleteUserHandler', 500, errorResponse);
      return createErrorResponse('Internal server error', 500);
    }
  }
);