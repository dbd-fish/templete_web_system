/**
 * API設定ファイル
 *
 * SSR（サーバーサイドレンダリング）とCSR（クライアントサイドレンダリング）の
 * 両方で動作するAPI URL設定を提供
 */

/**
 * 実行環境に応じて適切なAPI URLを返す関数
 *
 * @returns {string} API URL
 */
export const getApiUrl = (): string => {
  // サーバーサイド環境の判定
  const isServer = typeof window === 'undefined';

  if (isServer) {
    // SSR環境: Docker内部ネットワークを使用
    return process.env.API_URL || 'http://backend:8000';
  } else {
    // CSR環境: 外部API URLを使用
    return import.meta.env?.VITE_API_URL || 'http://localhost:8000';
  }
};

/**
 * 外部公開用のAPI URLを取得する関数
 *
 * クライアントサイドでのAPI呼び出しに使用
 * ローカル開発環境ではlocalhost、本番環境では公開URLを使用
 *
 * @returns {string} 公開API URL
 */
export const getPublicApiUrl = (): string => {
  // import.meta.envはVite特有の機能
  const viteApiUrl = import.meta.env?.VITE_API_URL;

  // 開発環境のデフォルト値
  if (!viteApiUrl && typeof window !== 'undefined') {
    // ブラウザ環境でローカル開発中の場合
    return window.location.hostname === 'localhost'
      ? 'http://localhost:8000'
      : 'http://backend:8000';
  }

  return viteApiUrl || 'http://backend:8000';
};

/**
 * APIエンドポイントのベースURL
 */
export const API_BASE_URL = getApiUrl();
