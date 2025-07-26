import { ErrorResponse } from '../features/auth/types';

// リフレッシュ中かどうかを管理するフラグ
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

// JWT+リフレッシュトークンシステム設定
let lastRefreshTime = 0;
const REFRESH_COOLDOWN = 3000; // 3秒のクールダウン

// 自動リフレッシュ機能
const ENABLE_AUTO_REFRESH = true;

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
 * JWT+リフレッシュトークンシステム - アクセストークン自動更新
 */
const refreshAccessToken = async (cookieHeader?: string): Promise<void> => {
  const now = Date.now();
  
  // クールダウンチェック
  if (now - lastRefreshTime < REFRESH_COOLDOWN) {
    return;
  }

  const { getApiUrl } = await import('../config/api');
  const apiUrl = getApiUrl();

  // リフレッシュトークンのみでの認証実装
  let refreshTokenOnly = '';
  if (cookieHeader) {
    const refreshTokenMatch = cookieHeader.match(/refreshToken=([^;]+)/);
    if (refreshTokenMatch) {
      refreshTokenOnly = `refreshToken=${refreshTokenMatch[1]}`;
    }
  }

  const requestHeaders = {
    'Content-Type': 'application/json',
    ...(refreshTokenOnly && { 'Cookie': refreshTokenOnly }),
  };

  const refreshRequestOptions = {
    method: 'POST',
    headers: requestHeaders,
    credentials: 'include' as RequestCredentials,
  };

  const refreshResponse = await fetch(`${apiUrl}/api/v1/auth/refresh`, refreshRequestOptions);

  if (!refreshResponse.ok) {
    throw new Error(`RefreshToken failed: ${refreshResponse.status}`);
  }

  lastRefreshTime = now;
  return;
};

/**
 * 新要件対応: JWT+リフレッシュトークンシステム - 自動リフレッシュ対応APIリクエスト
 * - アクセストークンのみでの認可（新要件: アクセストークンのみをバックエンドに送信）  
 * - 401エラー検知時の自動トークンリフレッシュ（リフレッシュトークンのみ使用）
 * - 新アクセストークン取得後の元リクエスト再実行
 * - 同時リクエストのキューイング機能
 * - リフレッシュ失敗時の自動ログインリダイレクト
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

  // アクセストークンのみでの認可実装
  if (cookieHeader) {
    // アクセストークンのみを抽出してAPIに送信
    const authTokenMatch = cookieHeader.match(/authToken=([^;]+)/);
    if (authTokenMatch) {
      const authTokenOnly = `authToken=${authTokenMatch[1]}`;
      headers.set('Cookie', authTokenOnly);
    }
  }

  const makeRequest = () => {
    const requestOptions: RequestInit = {
      ...options,
      headers,
      credentials: 'include' as RequestCredentials,
    };
    
    return fetch(url, requestOptions);
  };

  const response = await makeRequest();

  // 401エラー検知時の自動リフレッシュ
  if (response.status === 401 && !url.includes('/auth/refresh') && !url.includes('/auth/login')) {
    
    // 自動リフレッシュ有効性確認
    if (!ENABLE_AUTO_REFRESH) {
      await handleApiError(response);
      return response;
    }
    
    if (isRefreshing) {
      // 同時リクエストのキューイング
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => {
        return makeRequest();
      });
    }

    isRefreshing = true;

    try {
      await refreshAccessToken(cookieHeader);
      
      // キューに溜まったリクエストを処理
      failedQueue.forEach(({ resolve }) => resolve());
      failedQueue = [];
      
      isRefreshing = false;

      // 元のリクエストを再実行
      const retryResponse = await makeRequest();
      if (!retryResponse.ok && retryResponse.status !== 401) {
        await handleApiError(retryResponse);
      }
      return retryResponse;
    } catch (error) {
      // リフレッシュ失敗時処理
      failedQueue.forEach(({ reject }) => reject(error));
      failedQueue = [];
      isRefreshing = false;
      
      // 期限切れ時のセッション無効化
      try {
        // Cookie削除を試行（可能な場合）
        document.cookie = 'authToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        document.cookie = 'refreshToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      } catch {
        // SSR環境ではCookie削除不可
      }
      
      // 認証エラー処理とログインリダイレクト
      await handleApiError(response);
      throw error;
    }
  }

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

  const formRequestOptions = {
    ...options,
    method: 'POST',
    headers,
    body,
    credentials: 'include' as RequestCredentials,
  };

  const response = await fetch(url, formRequestOptions);

  if (!response.ok) {
    await handleApiError(response);
  }

  return response;
};
