import { http, HttpResponse } from 'msw';
import { PasswordResetRequest, SuccessResponse, ErrorResponse } from '../../commons/utils/types';
import { getTokenType, MSG_PASSWORD_RESET_SUCCESS, MSG_INVALID_TOKEN } from '../data/auth';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse, isValidPassword, validateRequiredFields } from '../utils/mockHelpers';

// /api/v1/auth/reset-password エンドポイントへのPOSTリクエストを処理するハンドラー
export const resetPasswordHandler = http.post(
  'http://localhost:5173/api/v1/auth/reset-password',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = await request.json() as PasswordResetRequest;
      const { token, new_password } = body;

      logMockHandler('resetPasswordHandler', 'POST', request.url, { token: '***', password: '***' });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ token, new_password }, ['token', 'new_password']);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: `Required fields are missing: ${missingFields.join(', ')}`,
          status_code: 400
        };
        
        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // トークンの種別確認
      const tokenType = getTokenType(token);
      if (tokenType !== 'reset') {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 400
        };
        
        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 400);
      }

      // パスワードの強度チェック
      if (!isValidPassword(new_password)) {
        const errorResponse: ErrorResponse = {
          detail: 'Password must be at least 8 characters long',
          status_code: 400
        };
        
        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_PASSWORD_RESET_SUCCESS
      };

      logMockResponse('resetPasswordHandler', 200, { success: true });
      return createSuccessResponse(MSG_PASSWORD_RESET_SUCCESS, successResponse);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('resetPasswordHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  }
);