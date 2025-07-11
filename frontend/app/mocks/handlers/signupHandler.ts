import { http, HttpResponse } from 'msw';
import { SignupRequest, SuccessResponse, ErrorResponse } from '../../commons/utils/types';
import { getTokenType } from '../data/auth';
import { MSG_SIGNUP_SUCCESS, MSG_INVALID_TOKEN, MOCK_VERIFY_TOKEN } from '../data/constants';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse } from '../utils/mockHelpers';

// /api/v1/auth/signup エンドポイントへのPOSTリクエストを処理するハンドラー
export const signupHandler = http.post(
  'http://localhost:5173/api/v1/auth/signup',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = await request.json() as SignupRequest;
      const { token } = body;

      logMockHandler('signupHandler', 'POST', request.url, { token: '***' });

      // 有効なトークンかどうかのチェック（モック用）
      if (!token || token.trim() === '') {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid or missing token',
          status_code: 400
        };
        
        logMockResponse('signupHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // トークンの種別確認
      const tokenType = getTokenType(token);
      if (tokenType !== 'verify') {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 400
        };
        
        logMockResponse('signupHandler', 400, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 400);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_SIGNUP_SUCCESS
      };

      logMockResponse('signupHandler', 200, { success: true });
      return createSuccessResponse(MSG_SIGNUP_SUCCESS, successResponse);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('signupHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  }
);