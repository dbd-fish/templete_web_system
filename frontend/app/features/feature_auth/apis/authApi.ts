/**
 * 認証関連API統合ファイル
 *
 * @description
 * すべての認証・ユーザー管理API関数を集約
 * 既存の実装パターンを維持しながら単一ファイルに統合
 */

import {
  UserResponse,
  MessageResponse,
  SuccessResponse,
  UserUpdate,
} from '~/utils/types';
import { apiRequest, apiFormRequest } from '~/utils/apiErrorHandler';

// ==================== 認証関連 ====================

/**
 * ユーザーのログインを処理する非同期関数
 * - '/api/v1/auth/login' エンドポイントを使用してログインリクエストを送信
 * - 成功時: Responseオブジェクトを返す
 * - 失敗時: ApiErrorをスロー
 *
 * @param email - ユーザーのメールアドレス
 * @param password - ユーザーのパスワード
 */
export const login = async (email: string, password: string) => {
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  try {
    const response = await apiFormRequest(`${apiUrl}/api/v1/auth/login`, {
      username: email, // OAuth2PasswordRequestFormは "username" フィールドを期待
      password: password,
    });

    return response;
  } catch (error) {
    throw error;
  }
};

/**
 * ユーザーのログアウトを処理する非同期関数
 * - '/api/v1/auth/logout' エンドポイントを使用してログアウトリクエストを送信
 * - 成功時: レスポンスを返す
 * - 失敗時: エラーメッセージをスロー
 */
export const logout = async (request: Request) => {
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  try {
    const cookieHeader = request.headers.get('Cookie');
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/logout`,
      {
        method: 'POST',
      },
      cookieHeader || '',
    );

    return response;
  } catch (error) {
    throw error;
  }
};

// ==================== ユーザー管理 ====================

/**
 * ユーザー情報を取得する非同期関数
 * - '/api/v1/auth/me' エンドポイントからユーザー情報を取得
 * - 成功時: ユーザー情報オブジェクトを返す
 * - 失敗時: null を返す
 */
export const getUser = async (request: Request) => {
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  const cookieHeader = request.headers.get('Cookie');

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'POST',
      },
      cookieHeader || '',
    );

    const data = (await response.json()) as UserResponse;
    return { username: data.username, email: data.email };
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
  const apiUrl = process.env.API_URL;

  try {
    const cookieHeader = request.headers.get('Cookie');
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'PATCH',
        body: JSON.stringify(updateData),
      },
      cookieHeader || '',
    );

    return (await response.json()) as UserResponse;
  } catch (error) {
    throw error;
  }
};

/**
 * ユーザーアカウントを削除する非同期関数
 * - '/api/v1/auth/me' エンドポイントでアカウントを削除
 * - 成功時: メッセージレスポンスを返す
 * - 失敗時: エラーをスロー
 */
export const deleteUser = async (
  request: Request,
): Promise<MessageResponse> => {
  const apiUrl = process.env.API_URL;

  try {
    const cookieHeader = request.headers.get('Cookie');
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'DELETE',
      },
      cookieHeader || '',
    );

    return (await response.json()) as MessageResponse;
  } catch (error) {
    throw error;
  }
};

// ==================== 登録関連 ====================

/**
 * ユーザー登録を処理する非同期関数
 * - '/api/v1/auth/signup' エンドポイントでユーザー登録を完了
 * - 成功時: 成功フラグを返す
 * - 失敗時: エラーをスロー
 */
export const signup = async (token: string): Promise<boolean> => {
  const apiUrl = process.env.API_URL;

  try {
    const signupData = {
      token: token,
    };

    const response = await apiRequest(`${apiUrl}/api/v1/auth/signup`, {
      method: 'POST',
      body: JSON.stringify(signupData),
    });

    const data = (await response.json()) as SuccessResponse;
    return data.success;
  } catch (error) {
    console.error('[signup] Error:', error);
    throw error;
  }
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
  const apiUrl = process.env.API_URL;

  try {
    // 各フィールドをトリムし、空文字列チェック
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const trimmedUsername = username.trim();

    if (!trimmedEmail || !trimmedPassword || !trimmedUsername) {
      throw new Error('すべてのフィールドが必要です');
    }

    const verifyEmailData = {
      email: trimmedEmail,
      password: trimmedPassword,
      username: trimmedUsername,
    };

    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/send-verify-email`,
      {
        method: 'POST',
        body: JSON.stringify(verifyEmailData),
      },
    );

    return (await response.json()) as SuccessResponse;
  } catch (error) {
    console.error('[sendVerifyEmail] Error:', error);
    throw error;
  }
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
  const apiUrl = process.env.API_URL;

  try {
    // メールアドレスをトリムし、空文字列チェック
    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      throw new Error('メールアドレスが必要です');
    }

    const resetEmailData = {
      email: trimmedEmail,
    };

    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/send-password-reset-email`,
      {
        method: 'POST',
        body: JSON.stringify(resetEmailData),
      },
    );

    return (await response.json()) as SuccessResponse;
  } catch (error) {
    console.error('[sendPasswordResetEmail] Error:', error);
    throw error;
  }
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
  const apiUrl = process.env.API_URL;

  try {
    const resetData = {
      token: token,
      new_password: newPassword.trim(), // パスワードはトリム処理
    };

    const response = await apiRequest(`${apiUrl}/api/v1/auth/reset-password`, {
      method: 'POST',
      body: JSON.stringify(resetData),
    });

    return (await response.json()) as SuccessResponse;
  } catch (error) {
    console.error('[resetPassword] Error:', error);
    throw error;
  }
};
