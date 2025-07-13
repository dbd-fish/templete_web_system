/**
 * アプリケーション共通の型定義
 * 
 * @description
 * 複数の機能で使用される共通の型定義のみを含む
 * 機能固有の型は各featureディレクトリ内のtypes.tsに定義する
 */

// ==================== Loader共通型 ====================

/**
 * 全loader関数共通の返り値の型
 * React Router v7のLoader関数で使用
 */
export type LoaderDataType = {
  user?: { email: string; username: string };
  signupData?: { success: boolean };
  test?: { test1: number; test2: string };
};

// ==================== 共通UI型 ====================

/**
 * 共通のサイズバリアント
 */
export type SizeVariant = 'sm' | 'md' | 'lg';

/**
 * 共通のカラーバリアント  
 */
export type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error';

/**
 * 共通のステータス型
 */
export type Status = 'idle' | 'loading' | 'success' | 'error';