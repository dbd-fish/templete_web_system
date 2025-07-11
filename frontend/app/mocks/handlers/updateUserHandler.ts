import { http, HttpResponse } from 'msw';
import { UserUpdate, UserResponse, ErrorResponse } from '../../commons/utils/types';
import { getUserFromToken, MSG_USER_UPDATE_SUCCESS, MSG_INVALID_TOKEN, COOKIE_AUTH_TOKEN } from '../data/auth';
import { updateMockUser, MOCK_USER } from '../data/users';
import { createSuccessResponse, createErrorResponse, addDefaultDelay, logMockHandler, logMockResponse, isValidEmail, isValidPassword } from '../utils/mockHelpers';

// /api/v1/auth/me エンドポイントへのPATCHリクエストを処理するハンドラー（ユーザー情報更新）
export const updateUserHandler = http.patch(
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
        
        logMockResponse('updateUserHandler', 401, errorResponse);
        return HttpResponse.json(errorResponse, { status: 401 });
      }

      // トークンからユーザー情報を取得
      const currentUser = getUserFromToken(authToken);
      if (!currentUser) {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 403
        };
        
        logMockResponse('updateUserHandler', 403, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 403);
      }

      const body = await request.json() as UserUpdate;
      const { email, username, password } = body;

      logMockHandler('updateUserHandler', 'PATCH', request.url, { email, username, password: '***' });

      // 少なくとも一つの更新フィールドが必要
      if (!email && !username && !password) {
        const errorResponse: ErrorResponse = {
          detail: 'At least one field must be provided for update',
          status_code: 400
        };
        
        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック（提供されている場合）
      if (email && !isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400
        };
        
        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // パスワードの強度チェック（提供されている場合）
      if (password && !isValidPassword(password)) {
        const errorResponse: ErrorResponse = {
          detail: 'Password must be at least 8 characters long',
          status_code: 400
        };
        
        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 更新されたユーザー情報を生成
      const updates: Partial<UserResponse> = {};
      if (email) updates.email = email;
      if (username) updates.username = username;
      
      const updatedUser = updateMockUser(currentUser, updates);

      logMockResponse('updateUserHandler', 200, { success: true, user: updatedUser.email });
      return createSuccessResponse(MSG_USER_UPDATE_SUCCESS, updatedUser);
      
    } catch (error) {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400
      };
      
      logMockResponse('updateUserHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  }
);