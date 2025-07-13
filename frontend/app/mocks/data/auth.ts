/**
 * MSWモック用の認証関連データ
 *
 * @description
 * 認証・認可に関連するモックデータ、バリデーション、
 * レスポンス生成機能を提供
 */

import {
  findUserByEmailOrUsername,
  MOCK_USER,
  MOCK_ADMIN_USER,
  AUTH_CREDENTIALS,
} from './users';
import type { UserResponse } from '../../features/feature_auth/types';

// ==================== JWTトークン ====================

/** モック用のJWTアクセストークン */
export const MOCK_ACCESS_TOKEN = 'mock-jwt-access-token-12345';

/** パスワードリセット用のモックトークン */
export const MOCK_RESET_TOKEN = 'mock-password-reset-token-abcde';

/** 認証メール用のモックトークン */
export const MOCK_VERIFY_TOKEN = 'mock-email-verify-token-fghij';

// ==================== APIレスポンスメッセージ ====================

/** ログイン成功メッセージ */
export const MSG_LOGIN_SUCCESS = 'ログインに成功しました';

/** ログアウト成功メッセージ */
export const MSG_LOGOUT_SUCCESS = 'ログアウトしました';

/** ユーザー情報取得成功メッセージ */
export const MSG_USER_INFO_SUCCESS = 'ユーザー情報を取得しました';

/** ユーザー情報更新成功メッセージ */
export const MSG_USER_UPDATE_SUCCESS = 'ユーザー情報が正常に更新されました';

/** アカウント削除成功メッセージ */
export const MSG_ACCOUNT_DELETE_SUCCESS =
  'ユーザーアカウントが正常に削除されました';

/** ユーザー登録成功メッセージ */
export const MSG_SIGNUP_SUCCESS = 'ユーザー登録が完了しました';

/** 認証メール送信成功メッセージ */
export const MSG_VERIFY_EMAIL_SUCCESS =
  '認証メールを送信しました。メールをご確認ください';

/** パスワードリセットメール送信成功メッセージ */
export const MSG_RESET_EMAIL_SUCCESS = 'パスワードリセットメールを送信しました';

/** パスワードリセット成功メッセージ */
export const MSG_PASSWORD_RESET_SUCCESS =
  'パスワードが正常にリセットされました';

// ==================== エラーメッセージ ====================

/** 認証失敗メッセージ */
export const MSG_AUTH_FAILED =
  'メールアドレスまたはパスワードが正しくありません';

/** 無効なトークンメッセージ */
export const MSG_INVALID_TOKEN = '無効なトークンです';

/** ユーザーが見つからないメッセージ */
export const MSG_USER_NOT_FOUND = 'ユーザーが見つかりません';

/** ユーザーが既に存在するメッセージ */
export const MSG_USER_ALREADY_EXISTS =
  'このメールアドレスは既に登録されています';

// ==================== Cookie設定 ====================

/** Cookie名: 認証トークン */
export const COOKIE_AUTH_TOKEN = 'authToken';

/** Cookie有効期限（秒） */
export const COOKIE_MAX_AGE = 60 * 60 * 3; // 3時間

// ==================== 認証情報の定義 ====================

/** 有効なログイン認証情報 */
export interface ValidCredential {
  emailOrUsername: string;
  password: string;
  user: UserResponse;
}

/** 利用可能な認証情報のリスト */
export const VALID_CREDENTIALS: ValidCredential[] = [
  {
    emailOrUsername: AUTH_CREDENTIALS.USER.email,
    password: AUTH_CREDENTIALS.USER.password,
    user: MOCK_USER,
  },
  {
    emailOrUsername: AUTH_CREDENTIALS.USER.username,
    password: AUTH_CREDENTIALS.USER.password,
    user: MOCK_USER,
  },
  {
    emailOrUsername: AUTH_CREDENTIALS.ADMIN.email,
    password: AUTH_CREDENTIALS.ADMIN.password,
    user: MOCK_ADMIN_USER,
  },
  {
    emailOrUsername: AUTH_CREDENTIALS.ADMIN.username,
    password: AUTH_CREDENTIALS.ADMIN.password,
    user: MOCK_ADMIN_USER,
  },
];

// ==================== 認証機能 ====================

/**
 * ログイン認証を検証
 * @param emailOrUsername - メールアドレスまたはユーザー名
 * @param password - パスワード
 * @returns 認証成功時はユーザー情報、失敗時はnull
 */
export const authenticateUser = (
  emailOrUsername: string,
  password: string,
): UserResponse | null => {
  const credential = VALID_CREDENTIALS.find(
    (cred) =>
      cred.emailOrUsername === emailOrUsername && cred.password === password,
  );

  return credential ? credential.user : null;
};

/**
 * トークンからユーザー情報を取得（モック）
 * @param token - JWTトークン（モック）
 * @returns ユーザー情報 | null
 */
export const getUserFromToken = (token: string): UserResponse | null => {
  // モック環境では常にデフォルトユーザーを返す
  if (token === MOCK_ACCESS_TOKEN) {
    return MOCK_USER;
  }
  return null;
};

/**
 * メールアドレスの存在確認
 * @param email - チェックするメールアドレス
 * @returns 存在する場合はtrue
 */
export const emailExists = (email: string): boolean => {
  return !!findUserByEmailOrUsername(email);
};

// ==================== レスポンス生成ヘルパー ====================

/**
 * 認証成功レスポンスを生成
 * @param message - 成功メッセージ
 * @param user - ユーザー情報（オプション）
 * @returns 成功レスポンス
 */
export const createAuthSuccessResponse = (
  message: string,
  user?: UserResponse,
) => {
  return {
    success: true,
    message,
    timestamp: new Date().toISOString(),
    data: user || { message },
  };
};

/**
 * 認証エラーレスポンスを生成
 * @param message - エラーメッセージ
 * @param statusCode - HTTPステータスコード
 * @returns エラーレスポンス
 */
export const createAuthErrorResponse = (
  message: string = MSG_AUTH_FAILED,
  statusCode: number = 401,
) => {
  return {
    success: false,
    message,
    timestamp: new Date().toISOString(),
    statusCode,
  };
};

// ==================== Cookie設定ヘルパー ====================

/**
 * 認証Cookieを設定するヘルパー
 * @param token - 設定するトークン
 * @returns Cookie設定文字列
 */
export const createAuthCookie = (token: string = MOCK_ACCESS_TOKEN): string => {
  return `${COOKIE_AUTH_TOKEN}=${token}; HttpOnly; Secure; SameSite=Lax; Max-Age=${COOKIE_MAX_AGE}; Path=/`;
};

/**
 * 認証Cookieを削除するヘルパー
 * @returns Cookie削除設定文字列
 */
export const deleteAuthCookie = (): string => {
  return `${COOKIE_AUTH_TOKEN}=; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Path=/`;
};

// ==================== トークン関連 ====================

/** トークン種別 */
export const TOKEN_TYPES = {
  ACCESS: 'access',
  REFRESH: 'refresh',
  RESET: 'reset',
  VERIFY: 'verify',
} as const;

/**
 * モック用トークンデータ
 */
export const MOCK_TOKENS = {
  [TOKEN_TYPES.ACCESS]: MOCK_ACCESS_TOKEN,
  [TOKEN_TYPES.RESET]: MOCK_RESET_TOKEN,
  [TOKEN_TYPES.VERIFY]: MOCK_VERIFY_TOKEN,
};

/**
 * トークンの種別を判定
 * @param token - 判定するトークン
 * @returns トークン種別
 */
export const getTokenType = (token: string): string | null => {
  for (const [type, mockToken] of Object.entries(MOCK_TOKENS)) {
    if (token === mockToken) {
      return type;
    }
  }
  return null;
};
