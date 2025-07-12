/**
 * MSWモック用のユーザーデータ
 *
 * @description
 * テスト用のユーザー情報、プロフィールデータなど
 * ユーザー関連のモックレスポンスで使用されるデータを定義
 */

import type { UserResponse } from '../../utils/types';

// ==================== テストユーザーデータ ====================

/** 一般テストユーザーの情報 */
export const MOCK_USER: UserResponse = {
  email: 'testuser@example.com',
  username: 'testuser',
  contact_number: '090-1234-5678',
  date_of_birth: '1990-01-15',
  user_role: 2, // 一般ユーザー
  user_status: 1, // アクティブ
};

/** 管理者テストユーザーの情報 */
export const MOCK_ADMIN_USER: UserResponse = {
  email: 'admin@example.com',
  username: 'admin',
  contact_number: '090-9876-5432',
  date_of_birth: '1985-12-25',
  user_role: 4, // 管理者
  user_status: 1, // アクティブ
};

/** 新規登録用のテストユーザー */
export const MOCK_NEW_USER: UserResponse = {
  email: 'newuser@example.com',
  username: 'newuser123',
  contact_number: null,
  date_of_birth: null,
  user_role: 2, // 一般ユーザー
  user_status: 1, // アクティブ
};

// ==================== 認証情報 ====================

/** テスト用の認証情報 */
export const AUTH_CREDENTIALS = {
  // 一般ユーザー
  USER: {
    email: 'testuser@example.com',
    username: 'testuser',
    password: 'Password123456+-',
  },
  // 管理者
  ADMIN: {
    email: 'admin@example.com',
    username: 'admin',
    password: 'adminpassword',
  },
} as const;

// ==================== ユーザーリスト ====================

/** 利用可能なテストユーザーのリスト */
export const MOCK_USERS: UserResponse[] = [
  MOCK_USER,
  MOCK_ADMIN_USER,
  MOCK_NEW_USER,
];

// ==================== ユーザー検索機能 ====================

/**
 * メールアドレスでユーザーを検索
 * @param email - 検索するメールアドレス
 * @returns 見つかったユーザー情報 | undefined
 */
export const findUserByEmail = (email: string): UserResponse | undefined => {
  return MOCK_USERS.find((user) => user.email === email);
};

/**
 * ユーザー名でユーザーを検索
 * @param username - 検索するユーザー名
 * @returns 見つかったユーザー情報 | undefined
 */
export const findUserByUsername = (
  username: string,
): UserResponse | undefined => {
  return MOCK_USERS.find((user) => user.username === username);
};

/**
 * メールアドレスまたはユーザー名でユーザーを検索
 * @param emailOrUsername - メールアドレスまたはユーザー名
 * @returns 見つかったユーザー情報 | undefined
 */
export const findUserByEmailOrUsername = (
  emailOrUsername: string,
): UserResponse | undefined => {
  return MOCK_USERS.find(
    (user) =>
      user.email === emailOrUsername || user.username === emailOrUsername,
  );
};

// ==================== ユーザーデータ生成ヘルパー ====================

/**
 * 新しいテストユーザーデータを生成
 * @param overrides - 上書きするプロパティ
 * @returns 新しいユーザーデータ
 */
export const createMockUser = (
  overrides: Partial<UserResponse> = {},
): UserResponse => {
  return {
    ...MOCK_USER,
    ...overrides,
  };
};

/**
 * 更新されたユーザーデータを生成
 * @param currentUser - 現在のユーザー情報
 * @param updates - 更新内容
 * @returns 更新されたユーザーデータ
 */
export const updateMockUser = (
  currentUser: UserResponse,
  updates: Partial<UserResponse>,
): UserResponse => {
  return {
    ...currentUser,
    ...updates,
  };
};
