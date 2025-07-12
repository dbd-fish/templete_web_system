// NOTE: msw環境でモックAPIが動作するようなコードを残しておく。基本的に使わない方針。
// app/mocks/server.ts
import { setupServer } from 'msw/node';
import { authHandlers } from './handlers/authHandlers';

export const server = setupServer(...authHandlers);
