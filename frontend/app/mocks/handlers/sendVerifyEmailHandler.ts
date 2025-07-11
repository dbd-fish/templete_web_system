import { http, HttpResponse } from 'msw';
import { SendVerifyEmailRequest, SuccessResponse, ErrorResponse } from '../../commons/utils/types';
import { emailExists, MSG_VERIFY_EMAIL_SUCCESS, MSG_USER_ALREADY_EXISTS } from '../data/auth';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse, isValidEmail, validateRequiredFields } from '../utils/mockHelpers';

// /api/v1/auth/send-verify-email エンドポイントへのPOSTリクエストを処理するハンドラー
export const sendVerifyEmailHandler = http.post(
  'http://localhost:5173/api/v1/auth/send-verify-email',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = await request.json() as SendVerifyEmailRequest;
      const { email, username } = body;

      logMockHandler('sendVerifyEmailHandler', 'POST', request.url, { email, username });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ email, username }, ['email', 'username']);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: `Required fields are missing: ${missingFields.join(', ')}`,
          status_code: 400
        };
        
        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック
      if (!isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400
        };
        
        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 既存のメールアドレスかどうかチェック
      if (emailExists(email)) {
        const errorResponse: ErrorResponse = {
          detail: MSG_USER_ALREADY_EXISTS,
          status_code: 400
        };
        
        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return createErrorResponse(MSG_USER_ALREADY_EXISTS, 400);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_VERIFY_EMAIL_SUCCESS
      };

      logMockResponse('sendVerifyEmailHandler', 200, { success: true });
      return createSuccessResponse(MSG_VERIFY_EMAIL_SUCCESS, successResponse);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  }
);