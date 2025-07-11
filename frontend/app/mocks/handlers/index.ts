/**
 * MSW ハンドラー統合エクスポート
 * 
 * @description
 * 機能別に統合されたハンドラーを集約し、MSWで使用するハンドラー配列を提供
 */

import { authHandlers } from './authHandlers';

// 全ハンドラーを統合
export const handlers = [
  ...authHandlers,
];

// 個別のハンドラーグループもエクスポート
export { authHandlers } from './authHandlers';
