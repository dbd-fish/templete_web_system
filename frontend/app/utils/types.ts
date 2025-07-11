// NOTE: 全loader関数共通の返り値の型を定義。
export type LoaderDataType = {
  user?: { email: string; username: string }; // 必要なプロパティを定義
  signupData?: { success: boolean };
  test?: { test1: number; test2: string }; // 必要なプロパティを定義
};

// OpenAPI仕様に基づく認証関連の型定義
export interface UserResponse {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  password?: string;
}

export interface LoginRequest {
  username: string; // OAuth2PasswordRequestFormでは"username"フィールドを使用
  password: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

export interface SuccessResponse {
  success: boolean;
  message?: string;
}

export interface SendVerifyEmailRequest {
  email: string;
  username: string;
}

export interface SignupRequest {
  token: string;
}

export interface SendPasswordResetEmailRequest {
  email: string;
}

export interface PasswordResetRequest {
  token: string;
  new_password: string;
}

export interface ErrorResponse {
  detail: string;
  status_code: number;
}
