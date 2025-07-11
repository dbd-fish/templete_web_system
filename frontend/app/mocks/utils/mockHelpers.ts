/**
 * MSWモック用のユーティリティヘルパー
 * 
 * @description
 * モックハンドラーで共通して使用される機能、
 * レスポンス生成、遅延処理、リクエスト解析などを提供
 */

import { delay } from 'msw';

// ==================== 遅延設定 ====================

/** API レスポンスの遅延時間（ミリ秒） */
export const MOCK_DELAY_MS = 800;

/** 高速レスポンス用の遅延時間（ミリ秒） */
export const MOCK_DELAY_FAST_MS = 200;

/** 低速レスポンス用の遅延時間（ミリ秒） */
export const MOCK_DELAY_SLOW_MS = 2000;

// ==================== 遅延処理 ====================

/**
 * デフォルトの遅延を追加
 */
export const addDefaultDelay = () => delay(MOCK_DELAY_MS);

/**
 * 高速レスポンス用の遅延を追加
 */
export const addFastDelay = () => delay(MOCK_DELAY_FAST_MS);

/**
 * 低速レスポンス用の遅延を追加
 */
export const addSlowDelay = () => delay(MOCK_DELAY_SLOW_MS);

/**
 * カスタム遅延を追加
 * @param ms - 遅延時間（ミリ秒）
 */
export const addCustomDelay = (ms: number) => delay(ms);

// ==================== リクエスト解析 ====================

/**
 * FormDataからオブジェクトに変換
 * @param formData - FormDataオブジェクト
 * @returns 変換されたオブジェクト
 */
export const formDataToObject = (formData: FormData): Record<string, string> => {
  const obj: Record<string, string> = {};
  for (const [key, value] of formData.entries()) {
    obj[key] = value.toString();
  }
  return obj;
};

/**
 * URLSearchParamsからオブジェクトに変換
 * @param params - URLSearchParamsオブジェクト
 * @returns 変換されたオブジェクト
 */
export const urlParamsToObject = (params: URLSearchParams): Record<string, string> => {
  const obj: Record<string, string> = {};
  for (const [key, value] of params.entries()) {
    obj[key] = value;
  }
  return obj;
};

/**
 * リクエストヘッダーからCookieを取得
 * @param request - Request オブジェクト
 * @param cookieName - 取得するCookie名
 * @returns Cookie値 | null
 */
export const getCookieFromRequest = (request: Request, cookieName: string): string | null => {
  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(';').map(cookie => cookie.trim());
  const targetCookie = cookies.find(cookie => cookie.startsWith(`${cookieName}=`));
  
  return targetCookie ? targetCookie.split('=')[1] : null;
};

// ==================== レスポンス生成 ====================

/**
 * 成功レスポンスを生成
 * @param message - 成功メッセージ
 * @param data - レスポンスデータ
 * @param status - HTTPステータスコード
 * @returns Response オブジェクト
 */
export const createSuccessResponse = (
  message: string,
  data?: any,
  status: number = 200
): Response => {
  const responseBody = {
    success: true,
    message,
    timestamp: new Date().toISOString(),
    data: data || { message },
  };

  return new Response(JSON.stringify(responseBody), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

/**
 * エラーレスポンスを生成
 * @param message - エラーメッセージ
 * @param status - HTTPステータスコード
 * @param details - 詳細情報
 * @returns Response オブジェクト
 */
export const createErrorResponse = (
  message: string,
  status: number = 400,
  details?: any
): Response => {
  const responseBody = {
    success: false,
    message,
    timestamp: new Date().toISOString(),
    ...(details && { details }),
  };

  return new Response(JSON.stringify(responseBody), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

/**
 * Cookie付きレスポンスを生成
 * @param message - 成功メッセージ
 * @param cookieString - 設定するCookie文字列
 * @param data - レスポンスデータ
 * @param status - HTTPステータスコード
 * @returns Response オブジェクト
 */
export const createResponseWithCookie = (
  message: string,
  cookieString: string,
  data?: any,
  status: number = 200
): Response => {
  const responseBody = {
    success: true,
    message,
    timestamp: new Date().toISOString(),
    data: data || { message },
  };

  return new Response(JSON.stringify(responseBody), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Set-Cookie': cookieString,
    },
  });
};

// ==================== バリデーション ====================

/**
 * メールアドレス形式の検証
 * @param email - 検証するメールアドレス
 * @returns 有効な場合はtrue
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * パスワード強度の検証
 * @param password - 検証するパスワード
 * @returns 有効な場合はtrue
 */
export const isValidPassword = (password: string): boolean => {
  // 最低8文字以上
  return password.length >= 8;
};

/**
 * 必須フィールドの検証
 * @param data - 検証するデータ
 * @param requiredFields - 必須フィールドの配列
 * @returns 不足しているフィールドの配列
 */
export const validateRequiredFields = (
  data: Record<string, any>,
  requiredFields: string[]
): string[] => {
  const missingFields: string[] = [];
  
  for (const field of requiredFields) {
    if (!data[field] || data[field].toString().trim() === '') {
      missingFields.push(field);
    }
  }
  
  return missingFields;
};

// ==================== デバッグ ====================

/**
 * モックハンドラーのデバッグログを出力
 * @param handlerName - ハンドラー名
 * @param method - HTTPメソッド
 * @param url - リクエストURL
 * @param data - リクエストデータ
 */
export const logMockHandler = (
  handlerName: string,
  method: string,
  url: string,
  data?: any
): void => {
  console.log(`🔥 [MSW] ${handlerName}:`, {
    method,
    url,
    data,
    timestamp: new Date().toISOString(),
  });
};

/**
 * モックレスポンスのデバッグログを出力
 * @param handlerName - ハンドラー名
 * @param status - HTTPステータス
 * @param response - レスポンスデータ
 */
export const logMockResponse = (
  handlerName: string,
  status: number,
  response: any
): void => {
  console.log(`✅ [MSW] ${handlerName} Response:`, {
    status,
    response,
    timestamp: new Date().toISOString(),
  });
};