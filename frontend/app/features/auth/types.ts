/**
 * 認証機能専用の型定義
 */

// ==================== ユーザー関連 ====================

export interface UserResponse {
  email: string;
  username: string;
  contact_number: string | null;
  date_of_birth: string | null;
  user_role: number;
  user_status: number;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  password?: string;
}

// ==================== レスポンス ====================

export interface MessageResponse {
  message: string;
}

export interface SuccessResponse {
  success: boolean;
  message?: string;
}

export interface ErrorResponse {
  detail: string;
  status_code: number;
}
