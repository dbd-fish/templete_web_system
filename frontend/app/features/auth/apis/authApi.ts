/**
 * 認証関連API統合ファイル
 *
 * @description
 * すべての認証・ユーザー管理API関数を集約
 * 各API関数で個別に処理を記述
 */

import {
  UserResponse,
  MessageResponse,
  SuccessResponse,
  UserUpdate,
} from '../types';
import { apiRequest } from '~/utils/apiErrorHandler';
import { getApiUrl } from '~/config/api';
import { extractAuthTokens, extractRefreshToken } from '../cookies';

// ==================== 認証関連 ====================

/**
 * リフレッシュトークンを使用して新しいアクセストークンを取得する非同期関数
 * - '/api/v1/auth/refresh' エンドポイントを使用してトークンリフレッシュリクエストを送信
 * - 成功時: 新しいアクセストークンを含むレスポンスを返す
 * - 失敗時: エラーをスロー
 */
export const refreshToken = async (request: Request): Promise<Response> => {
  const apiUrl = getApiUrl();
  const cookieHeader = request.headers.get('Cookie');
  const refreshTokenCookie = extractRefreshToken(cookieHeader);
  
  return apiRequest(
    `${apiUrl}/api/v1/auth/refresh`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(refreshTokenCookie && { Cookie: refreshTokenCookie }),
      },
    },
    refreshTokenCookie,
  );
};

/**
 * ユーザーのログインを処理する非同期関数
 * - '/api/v1/auth/login' エンドポイントを使用してログインリクエストを送信
 * - 成功時: Responseオブジェクトを返す
 * - 失敗時: ApiErrorをスロー
 *
 * @param email - ユーザーのメールアドレス
 * @param password - ユーザーのパスワード
 */
export const login = async (
  email: string,
  password: string,
): Promise<Response> => {
  const apiUrl = getApiUrl();
  
  return apiRequest(`${apiUrl}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: email, // emailアドレスをusernameフィールドで送信（OAuth2互換）
      password: password,
    }),
  });
};

/**
 * ユーザーのログアウトを処理する非同期関数
 * - '/api/v1/auth/logout' エンドポイントを使用してログアウトリクエストを送信
 * - 成功時: レスポンスを返す
 * - 失敗時: エラーメッセージをスロー
 */
export const logout = async (request: Request): Promise<Response> => {
  const apiUrl = getApiUrl();
  const cookieHeader = request.headers.get('Cookie');
  const authTokens = extractAuthTokens(cookieHeader);
  
  return apiRequest(
    `${apiUrl}/api/v1/auth/logout`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authTokens && { Cookie: authTokens }),
      },
    },
    authTokens,
  );
};

// ==================== ユーザー管理 ====================

/**
 * ユーザー情報を取得する非同期関数
 * - '/api/v1/auth/me' エンドポイントからユーザー情報を取得（POSTメソッド）
 * - 成功時: ユーザー情報オブジェクトを返す
 * - 失敗時: null を返す
 */
export const getUser = async (
  request: Request,
): Promise<UserResponse | null> => {
  const apiUrl = getApiUrl();
  const cookieHeader = request.headers.get('Cookie');
  const authTokens = extractAuthTokens(cookieHeader);

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authTokens && { Cookie: authTokens }),
        },
      },
      authTokens,
    );
    return (await response.json()) as UserResponse;
  } catch (error) {
    // 認証エラーの場合はnullを返す
    if (error instanceof Error && error.message.includes('401')) {
      return null;
    }
    throw error;
  }
};

/**
 * ユーザー情報を更新する非同期関数
 * - '/api/v1/auth/me' エンドポイントでユーザー情報を更新
 * - 成功時: 更新されたユーザー情報を返す
 * - 失敗時: エラーをスロー
 */
export const updateUser = async (
  request: Request,
  updateData: UserUpdate,
): Promise<UserResponse> => {
  const apiUrl = getApiUrl();
  const cookieHeader = request.headers.get('Cookie');
  const authTokens = extractAuthTokens(cookieHeader);

  const response = await apiRequest(
    `${apiUrl}/api/v1/auth/me`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(authTokens && { Cookie: authTokens }),
      },
      body: JSON.stringify(updateData),
    },
    authTokens,
  );
  
  return (await response.json()) as UserResponse;
};

/**
 * ユーザーアカウントを削除する非同期関数
 * - '/api/v1/auth/user' エンドポイントでアカウントを削除
 * - 成功時: メッセージレスポンスを返す
 * - 失敗時: エラーをスロー
 */
export const deleteUser = async (
  request: Request,
): Promise<MessageResponse> => {
  const apiUrl = getApiUrl();
  const cookieHeader = request.headers.get('Cookie');
  const authTokens = extractAuthTokens(cookieHeader);

  const response = await apiRequest(
    `${apiUrl}/api/v1/auth/user`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(authTokens && { Cookie: authTokens }),
      },
    },
    authTokens,
  );
  
  return (await response.json()) as MessageResponse;
};

// ==================== 登録関連 ====================

/**
 * ユーザー登録を処理する非同期関数
 * - '/api/v1/auth/signup' エンドポイントでユーザー登録を完了
 * - 成功時: 成功フラグを返す
 * - 失敗時: エラーをスロー
 */
export const signup = async (token: string): Promise<boolean> => {
  const apiUrl = getApiUrl();
  
  const response = await apiRequest(`${apiUrl}/api/v1/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: token,
    }),
  });
  
  const data = (await response.json()) as SuccessResponse;
  return data.success;
};

/**
 * 認証メール送信を処理する非同期関数
 * - '/api/v1/auth/send-verify-email' エンドポイントで認証メールを送信
 * - 成功時: SuccessResponseを返す
 * - 失敗時: エラーをスロー
 */
export const sendVerifyEmail = async (
  email: string,
  password: string,
  username: string,
): Promise<SuccessResponse> => {
  // 各フィールドをトリムし、空文字列チェック
  const trimmedEmail = email.trim();
  const trimmedPassword = password.trim();
  const trimmedUsername = username.trim();

  if (!trimmedEmail || !trimmedPassword || !trimmedUsername) {
    throw new Error('すべてのフィールドが必要です');
  }

  const apiUrl = getApiUrl();
  
  const response = await apiRequest(`${apiUrl}/api/v1/auth/send-verify-email`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: trimmedEmail,
      password: trimmedPassword,
      username: trimmedUsername,
    }),
  });
  
  return (await response.json()) as SuccessResponse;
};

// ==================== パスワードリセット ====================

/**
 * パスワードリセットメール送信を処理する非同期関数
 * - '/api/v1/auth/send-password-reset-email' エンドポイントでリセットメールを送信
 * - 成功時: SuccessResponseを返す
 * - 失敗時: エラーをスロー
 */
export const sendPasswordResetEmail = async (
  email: string,
): Promise<SuccessResponse> => {
  // メールアドレスをトリムし、空文字列チェック
  const trimmedEmail = email.trim();

  if (!trimmedEmail) {
    throw new Error('メールアドレスが必要です');
  }

  const apiUrl = getApiUrl();
  
  const response = await apiRequest(
    `${apiUrl}/api/v1/auth/send-password-reset-email`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: trimmedEmail,
      }),
    },
  );
  
  return (await response.json()) as SuccessResponse;
};

/**
 * パスワードリセット実行を処理する非同期関数
 * - '/api/v1/auth/reset-password' エンドポイントでパスワードをリセット
 * - 成功時: SuccessResponseを返す
 * - 失敗時: エラーをスロー
 */
export const resetPassword = async (
  token: string,
  newPassword: string,
): Promise<SuccessResponse> => {
  const apiUrl = getApiUrl();
  
  const response = await apiRequest(`${apiUrl}/api/v1/auth/reset-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: token,
      new_password: newPassword.trim(), // パスワードはトリム処理
    }),
  });
  
  return (await response.json()) as SuccessResponse;
};
