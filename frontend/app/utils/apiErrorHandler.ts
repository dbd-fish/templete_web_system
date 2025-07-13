import { ErrorResponse } from '../features/feature_auth/types';

/**
 * API呼び出しで発生するエラーを統一的に処理するクラス
 */
export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly detail: string;

  constructor(statusCode: number, detail: string) {
    super(detail);
    this.statusCode = statusCode;
    this.detail = detail;
    this.name = 'ApiError';
  }
}

/**
 * Responseオブジェクトからエラー情報を抽出し、ApiErrorをスローする
 * @param response - fetch APIのResponseオブジェクト
 */
export const handleApiError = async (response: Response): Promise<never> => {
  try {
    const errorData = (await response.json()) as ErrorResponse;
    throw new ApiError(
      response.status,
      errorData.detail || 'Unknown error occurred',
    );
  } catch {
    // JSON解析に失敗した場合
    throw new ApiError(
      response.status,
      response.statusText || 'Unknown error occurred',
    );
  }
};

/**
 * 汎用的なAPIリクエストヘルパー関数
 * @param url - リクエストURL
 * @param options - fetchのオプション
 * @param cookieHeader - Cookie ヘッダー（オプション）
 * @returns Promise<Response>
 */
export const apiRequest = async (
  url: string,
  options: RequestInit = {},
  cookieHeader?: string,
): Promise<Response> => {
  const headers = new Headers(options.headers);

  // デフォルトのContent-Typeを設定
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Cookieヘッダーを追加（提供されている場合）
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    await handleApiError(response);
  }

  return response;
};

/**
 * form-urlencoded形式でのAPIリクエストヘルパー関数
 * @param url - リクエストURL
 * @param data - フォームデータ
 * @param options - fetchのオプション
 * @returns Promise<Response>
 */
export const apiFormRequest = async (
  url: string,
  data: Record<string, string>,
  options: RequestInit = {},
): Promise<Response> => {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/x-www-form-urlencoded');

  const body = new URLSearchParams(data).toString();

  const response = await fetch(url, {
    ...options,
    method: 'POST',
    headers,
    body,
    credentials: 'include',
  });

  if (!response.ok) {
    await handleApiError(response);
  }

  return response;
};
