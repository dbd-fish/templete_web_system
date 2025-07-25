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

// ==================== 管理者関連 ====================

export interface AdminUserResponse {
  user_id: string;
  email: string;
  username: string;
  user_role: number;
  user_status: number;
  created_at: string;
  deleted_at?: string | null;
  contact_number?: string | null;
  date_of_birth?: string | null;
}

export interface AdminUsersListResponse {
  users: AdminUserResponse[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface AdminUserUpdateData {
  username?: string;
  email?: string;
  user_role?: number;
  user_status?: number;
}
