import { http, HttpResponse } from 'msw';
import { SendPasswordResetEmailRequest, SuccessResponse, ErrorResponse } from '../../commons/utils/types';
import { emailExists } from '../data/auth';
import { MSG_RESET_EMAIL_SUCCESS, MSG_USER_NOT_FOUND } from '../data/constants';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse, isValidEmail, validateRequiredFields } from '../utils/mockHelpers';

// /api/v1/auth/send-password-reset-email エンドポイントへのPOSTリクエストを処理するハンドラー
export const sendPasswordResetEmailHandler = http.post(
  'http://localhost:5173/api/v1/auth/send-password-reset-email',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = await request.json() as SendPasswordResetEmailRequest;
      const { email } = body;

      logMockHandler('sendPasswordResetEmailHandler', 'POST', request.url, { email });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ email }, ['email']);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: 'Email is required',
          status_code: 400
        };
        
        logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック
      if (!isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400
        };
        
        logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスが存在するかチェック
      if (!emailExists(email)) {
        const errorResponse: ErrorResponse = {
          detail: MSG_USER_NOT_FOUND,
          status_code: 404
        };
        
        logMockResponse('sendPasswordResetEmailHandler', 404, errorResponse);
        return createErrorResponse(MSG_USER_NOT_FOUND, 404);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_RESET_EMAIL_SUCCESS
      };

      logMockResponse('sendPasswordResetEmailHandler', 200, { success: true });
      return createSuccessResponse(MSG_RESET_EMAIL_SUCCESS, successResponse);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  }
);