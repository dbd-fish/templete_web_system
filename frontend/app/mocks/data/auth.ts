/**
 * MSWモック用の認証関連データ
 * 
 * @description
 * 認証・認可に関連するモックデータ、バリデーション、
 * レスポンス生成機能を提供
 */

import { 
  MOCK_ACCESS_TOKEN,
  MOCK_RESET_TOKEN,
  MOCK_VERIFY_TOKEN,
  MSG_AUTH_FAILED,
  COOKIE_AUTH_TOKEN,
  COOKIE_MAX_AGE
} from './constants';
import { findUserByEmailOrUsername, MOCK_USER, MOCK_ADMIN_USER, AUTH_CREDENTIALS } from './users';
import type { UserResponse } from '../../commons/utils/types';

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
  password: string
): UserResponse | null => {
  const credential = VALID_CREDENTIALS.find(
    cred => cred.emailOrUsername === emailOrUsername && cred.password === password
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
  user?: UserResponse
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
  statusCode: number = 401
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