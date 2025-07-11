// MSW（Mock Service Worker）から必要なモジュールをインポート
import { http, HttpResponse } from 'msw';
import { MessageResponse, ErrorResponse } from '../../commons/utils/types';
import { deleteAuthCookie } from '../data/auth';
import { MSG_LOGOUT_SUCCESS } from '../data/constants';
import { createResponseWithCookie, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse } from '../utils/mockHelpers';

// /api/v1/auth/logout エンドポイントへのPOSTリクエストを処理するハンドラーを定義
export const logoutHandler = http.post(
  'http://localhost:5173/api/v1/auth/logout',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      logMockHandler('logoutHandler', 'POST', request.url);

      // 認証Cookieを削除
      const deleteCookieHeader = deleteAuthCookie();

      // 成功レスポンスを返す
      const messageResponse: MessageResponse = {
        message: MSG_LOGOUT_SUCCESS
      };
      
      logMockResponse('logoutHandler', 200, { success: true });
      
      return createResponseWithCookie(MSG_LOGOUT_SUCCESS, deleteCookieHeader, messageResponse);
      
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      // リクエストボディのパース中にエラーが発生した場合の処理
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('logoutHandler', 400, errorResponse);
      
      return createErrorResponse('Invalid request body', 400);
    }
  },
);
