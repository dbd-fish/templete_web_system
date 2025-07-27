/**
 * API Client パターンの実装
 * 共通のAPI呼び出しロジックを提供
 */

import { apiRequest } from './apiErrorHandler';
import { getApiUrl } from '~/config/api';
import { extractAuthTokens, extractRefreshToken } from '~/features/auth/cookies';

interface ApiClientOptions {
  baseUrl?: string;
  defaultHeaders?: HeadersInit;
}

interface RequestOptions extends Omit<RequestInit, 'method' | 'body'> {
  request?: Request; // SSR対応でCookieを渡すためのRequest
  cookieType?: 'all' | 'auth' | 'refresh'; // Cookie抽出タイプの指定
}

/**
 * API Clientクラス
 * HTTPメソッドごとのヘルパーメソッドを提供
 */
export class ApiClient {
  private baseUrl: string;
  private defaultHeaders: HeadersInit;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl || getApiUrl();
    this.defaultHeaders = options.defaultHeaders || {
      'Content-Type': 'application/json',
    };
  }

  /**
   * リクエストを準備する共通メソッド
   */
  private async prepareRequest(
    endpoint: string,
    method: string,
    options?: RequestOptions,
    body?: unknown,
  ): Promise<Response> {
    const url = `${this.baseUrl}${endpoint}`;

    // SSR環境でのCookie処理
    let authCookies: string | undefined;
    if (options?.request) {
      const cookieHeader = options.request.headers.get('Cookie');
      const cookieType = options.cookieType || 'auth';
      
      switch (cookieType) {
        case 'refresh':
          authCookies = extractRefreshToken(cookieHeader);
          break;
        case 'all':
          authCookies = cookieHeader || '';
          break;
        case 'auth':
        default:
          authCookies = extractAuthTokens(cookieHeader);
          break;
      }
    }

    const requestOptions: RequestInit = {
      ...options,
      method,
      headers: {
        ...this.defaultHeaders,
        ...options?.headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    };

    // requestプロパティを削除（RequestInitに含まれないため）
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { request, ...cleanRequestOptions } =
      requestOptions as RequestOptions & RequestInit;

    return apiRequest(url, cleanRequestOptions, authCookies);
  }

  /**
   * GETリクエスト
   */
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const response = await this.prepareRequest(endpoint, 'GET', options);
    return response.json() as Promise<T>;
  }

  /**
   * POSTリクエスト
   */
  async post<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    const response = await this.prepareRequest(endpoint, 'POST', options, data);
    return response.json() as Promise<T>;
  }

  /**
   * POSTリクエスト（レスポンスボディなし）
   */
  async postWithoutResponse(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions,
  ): Promise<Response> {
    return this.prepareRequest(endpoint, 'POST', options, data);
  }

  /**
   * PATCHリクエスト
   */
  async patch<T>(
    endpoint: string,
    data: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    const response = await this.prepareRequest(
      endpoint,
      'PATCH',
      options,
      data,
    );
    return response.json() as Promise<T>;
  }

  /**
   * DELETEリクエスト
   */
  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const response = await this.prepareRequest(endpoint, 'DELETE', options);
    return response.json() as Promise<T>;
  }
}

/**
 * デフォルトのAPI Clientインスタンス
 */
export const apiClient = new ApiClient();

/**
 * 認証API専用のクライアント
 * 将来的に認証専用の設定が必要になった場合に拡張可能
 */
export const authApiClient = new ApiClient({
  // 認証API専用の設定をここに追加可能
});
