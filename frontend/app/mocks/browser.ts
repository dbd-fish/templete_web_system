// NOTE: msw環境でモックAPIが動作するようなコードを残しておく。基本的に使わない方針。
import { setupWorker } from 'msw/browser';
// NOTE: 認証関連のモックハンドラーを直接インポート
import { authHandlers } from './handlers/authHandlers';

export const worker = setupWorker(...authHandlers);
