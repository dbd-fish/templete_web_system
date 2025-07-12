/**
 * MSW 認証関連ハンドラー
 *
 * @description
 * 認証、認可、ユーザー管理に関連するすべてのMSWハンドラーを統合
 * ログイン、ログアウト、ユーザー登録、パスワードリセット、ユーザー情報管理を提供
 */

import { http, HttpResponse } from 'msw';
import {
  ErrorResponse,
  UserResponse,
  MessageResponse,
  SuccessResponse,
  UserUpdate,
} from '../../utils/types';
import {
  authenticateUser,
  getUserFromToken,
  deleteAuthCookie,
  getTokenType,
  emailExists,
  MOCK_ACCESS_TOKEN,
  MSG_LOGIN_SUCCESS,
  MSG_AUTH_FAILED,
  MSG_LOGOUT_SUCCESS,
  MSG_USER_INFO_SUCCESS,
  MSG_INVALID_TOKEN,
  MSG_SIGNUP_SUCCESS,
  MSG_VERIFY_EMAIL_SUCCESS,
  MSG_USER_ALREADY_EXISTS,
  MSG_RESET_EMAIL_SUCCESS,
  MSG_USER_NOT_FOUND,
  MSG_PASSWORD_RESET_SUCCESS,
  MSG_USER_UPDATE_SUCCESS,
  MSG_ACCOUNT_DELETE_SUCCESS,
  COOKIE_AUTH_TOKEN,
} from '../data/auth';
import { updateMockUser } from '../data/users';
import {
  createResponseWithCookie,
  createSuccessResponse,
  createErrorResponse,
  formDataToObject,
  addDefaultDelay,
  logMockHandler,
  logMockResponse,
  isValidEmail,
  isValidPassword,
  validateRequiredFields,
} from '../utils/mockHelpers';

// ==================== 型定義 ====================

/** ログインリクエストのボディの型定義（form-urlencoded用） */
export interface LoginRequestBody {
  username: string; // OAuth2PasswordRequestFormでは"username"フィールドを使用
  password: string; // ユーザーのパスワード
}

// ==================== ログイン ====================

/** ログインハンドラー */
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
        const tokenData = {
          access_token: MOCK_ACCESS_TOKEN,
          token_type: 'bearer',
        };

        const cookieString = `authToken=${MOCK_ACCESS_TOKEN}; HttpOnly; Secure; SameSite=Lax; Path=/`;

        logMockResponse('loginHandler', 200, {
          success: true,
          user: user.email,
        });

        return createResponseWithCookie(
          MSG_LOGIN_SUCCESS,
          cookieString,
          tokenData,
        );
      } else {
        // 認証情報が無効な場合のエラーレスポンス
        const errorResponse: ErrorResponse = {
          detail: MSG_AUTH_FAILED,
          status_code: 401,
        };

        logMockResponse('loginHandler', 401, errorResponse);

        return new HttpResponse(JSON.stringify(errorResponse), {
          status: 401,
          headers: {
            'Content-Type': 'application/json',
          },
        });
      }
    } catch {
      // リクエストボディのパース中にエラーが発生した場合の処理
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('loginHandler', 400, errorResponse);

      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== ログアウト ====================

/** ログアウトハンドラー */
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
        message: MSG_LOGOUT_SUCCESS,
      };

      logMockResponse('logoutHandler', 200, { success: true });

      return createResponseWithCookie(
        MSG_LOGOUT_SUCCESS,
        deleteCookieHeader,
        messageResponse,
      );
    } catch {
      // リクエストボディのパース中にエラーが発生した場合の処理
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('logoutHandler', 400, errorResponse);

      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== ユーザー情報取得 ====================

/** ユーザー情報取得ハンドラー */
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
        status_code: 401,
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
        status_code: 403,
      };

      logMockResponse('getMeHandler', 403, errorResponse);
      return createErrorResponse(MSG_INVALID_TOKEN, 403);
    }
  },
);

// ==================== ユーザー登録 ====================

/** ユーザー登録ハンドラー */
export const signupHandler = http.post(
  'http://localhost:5173/api/v1/auth/signup',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = (await request.json()) as { token: string };
      const { token } = body;

      logMockHandler('signupHandler', 'POST', request.url, { token: '***' });

      // 有効なトークンかどうかのチェック（モック用）
      if (!token || token.trim() === '') {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid or missing token',
          status_code: 400,
        };

        logMockResponse('signupHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // トークンの種別確認
      const tokenType = getTokenType(token);
      if (tokenType !== 'verify') {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 400,
        };

        logMockResponse('signupHandler', 400, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 400);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_SIGNUP_SUCCESS,
      };

      logMockResponse('signupHandler', 200, { success: true });
      return createSuccessResponse(MSG_SIGNUP_SUCCESS, successResponse);
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('signupHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== 認証メール送信 ====================

/** 認証メール送信ハンドラー */
export const sendVerifyEmailHandler = http.post(
  'http://localhost:5173/api/v1/auth/send-verify-email',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = (await request.json()) as {
        email: string;
        username: string;
        password: string;
      };
      const { email, username } = body;

      logMockHandler('sendVerifyEmailHandler', 'POST', request.url, {
        email,
        username,
      });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ email, username }, [
        'email',
        'username',
      ]);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: `Required fields are missing: ${missingFields.join(', ')}`,
          status_code: 400,
        };

        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック
      if (!isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400,
        };

        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 既存のメールアドレスかどうかチェック
      if (emailExists(email)) {
        const errorResponse: ErrorResponse = {
          detail: MSG_USER_ALREADY_EXISTS,
          status_code: 400,
        };

        logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
        return createErrorResponse(MSG_USER_ALREADY_EXISTS, 400);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_VERIFY_EMAIL_SUCCESS,
      };

      logMockResponse('sendVerifyEmailHandler', 200, { success: true });
      return createSuccessResponse(MSG_VERIFY_EMAIL_SUCCESS, successResponse);
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('sendVerifyEmailHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== パスワードリセットメール送信 ====================

/** パスワードリセットメール送信ハンドラー */
export const sendPasswordResetEmailHandler = http.post(
  'http://localhost:5173/api/v1/auth/send-password-reset-email',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = (await request.json()) as { email: string };
      const { email } = body;

      logMockHandler('sendPasswordResetEmailHandler', 'POST', request.url, {
        email,
      });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ email }, ['email']);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: 'Email is required',
          status_code: 400,
        };

        logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック
      if (!isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400,
        };

        logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスが存在するかチェック
      if (!emailExists(email)) {
        const errorResponse: ErrorResponse = {
          detail: MSG_USER_NOT_FOUND,
          status_code: 404,
        };

        logMockResponse('sendPasswordResetEmailHandler', 404, errorResponse);
        return createErrorResponse(MSG_USER_NOT_FOUND, 404);
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_RESET_EMAIL_SUCCESS,
      };

      logMockResponse('sendPasswordResetEmailHandler', 200, { success: true });
      return createSuccessResponse(MSG_RESET_EMAIL_SUCCESS, successResponse);
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('sendPasswordResetEmailHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== パスワードリセット ====================

/** パスワードリセットハンドラー */
export const resetPasswordHandler = http.post(
  'http://localhost:5173/api/v1/auth/reset-password',
  async ({ request }) => {
    await addDefaultDelay();

    try {
      const body = (await request.json()) as {
        token: string;
        new_password: string;
      };
      const { token, new_password } = body;

      logMockHandler('resetPasswordHandler', 'POST', request.url, {
        token: '***',
        password: '***',
      });

      // 必須フィールドの検証
      const missingFields = validateRequiredFields({ token, new_password }, [
        'token',
        'new_password',
      ]);
      if (missingFields.length > 0) {
        const errorResponse: ErrorResponse = {
          detail: `Required fields are missing: ${missingFields.join(', ')}`,
          status_code: 400,
        };

        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // トークンの種別確認
      const tokenType = getTokenType(token);
      if (tokenType !== 'reset') {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 400,
        };

        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 400);
      }

      // パスワードの強度チェック
      if (!isValidPassword(new_password)) {
        const errorResponse: ErrorResponse = {
          detail: 'Password must be at least 8 characters long',
          status_code: 400,
        };

        logMockResponse('resetPasswordHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 成功レスポンスを返す
      const successResponse: SuccessResponse = {
        success: true,
        message: MSG_PASSWORD_RESET_SUCCESS,
      };

      logMockResponse('resetPasswordHandler', 200, { success: true });
      return createSuccessResponse(MSG_PASSWORD_RESET_SUCCESS, successResponse);
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('resetPasswordHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== ユーザー情報更新 ====================

/** ユーザー情報更新ハンドラー */
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
          status_code: 401,
        };

        logMockResponse('updateUserHandler', 401, errorResponse);
        return HttpResponse.json(errorResponse, { status: 401 });
      }

      // トークンからユーザー情報を取得
      const currentUser = getUserFromToken(authToken);
      if (!currentUser) {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 403,
        };

        logMockResponse('updateUserHandler', 403, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 403);
      }

      const body = (await request.json()) as UserUpdate;
      const { email, username, password } = body;

      logMockHandler('updateUserHandler', 'PATCH', request.url, {
        email,
        username,
        password: '***',
      });

      // 少なくとも一つの更新フィールドが必要
      if (!email && !username && !password) {
        const errorResponse: ErrorResponse = {
          detail: 'At least one field must be provided for update',
          status_code: 400,
        };

        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // メールアドレスの形式チェック（提供されている場合）
      if (email && !isValidEmail(email)) {
        const errorResponse: ErrorResponse = {
          detail: 'Invalid email format',
          status_code: 400,
        };

        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // パスワードの強度チェック（提供されている場合）
      if (password && !isValidPassword(password)) {
        const errorResponse: ErrorResponse = {
          detail: 'Password must be at least 8 characters long',
          status_code: 400,
        };

        logMockResponse('updateUserHandler', 400, errorResponse);
        return HttpResponse.json(errorResponse, { status: 400 });
      }

      // 更新されたユーザー情報を生成
      const updates: Partial<UserResponse> = {};
      if (email) updates.email = email;
      if (username) updates.username = username;

      const updatedUser = updateMockUser(currentUser, updates);

      logMockResponse('updateUserHandler', 200, {
        success: true,
        user: updatedUser.email,
      });
      return createSuccessResponse(MSG_USER_UPDATE_SUCCESS, updatedUser);
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Invalid request body',
        status_code: 400,
      };

      logMockResponse('updateUserHandler', 400, errorResponse);
      return createErrorResponse('Invalid request body', 400);
    }
  },
);

// ==================== ユーザーアカウント削除 ====================

/** ユーザーアカウント削除ハンドラー */
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
          status_code: 401,
        };

        logMockResponse('deleteUserHandler', 401, errorResponse);
        return HttpResponse.json(errorResponse, { status: 401 });
      }

      // トークンからユーザー情報を取得
      const currentUser = getUserFromToken(authToken);
      if (!currentUser) {
        const errorResponse: ErrorResponse = {
          detail: MSG_INVALID_TOKEN,
          status_code: 403,
        };

        logMockResponse('deleteUserHandler', 403, errorResponse);
        return createErrorResponse(MSG_INVALID_TOKEN, 403);
      }

      logMockHandler('deleteUserHandler', 'DELETE', request.url, {
        user: currentUser.email,
      });

      // 成功レスポンスを返す
      const messageResponse: MessageResponse = {
        message: MSG_ACCOUNT_DELETE_SUCCESS,
      };

      // 認証クッキーを削除
      const deleteCookieHeader = deleteAuthCookie();

      logMockResponse('deleteUserHandler', 200, { success: true });

      return createResponseWithCookie(
        MSG_ACCOUNT_DELETE_SUCCESS,
        deleteCookieHeader,
        messageResponse,
      );
    } catch {
      const errorResponse: ErrorResponse = {
        detail: 'Internal server error',
        status_code: 500,
      };

      logMockResponse('deleteUserHandler', 500, errorResponse);
      return createErrorResponse('Internal server error', 500);
    }
  },
);

// ==================== ハンドラーのエクスポート ====================

/** 認証関連のすべてのハンドラー */
export const authHandlers = [
  loginHandler,
  logoutHandler,
  getMeHandler,
  signupHandler,
  sendVerifyEmailHandler,
  sendPasswordResetEmailHandler,
  resetPasswordHandler,
  updateUserHandler,
  deleteUserHandler,
];
