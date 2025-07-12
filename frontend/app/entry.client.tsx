/**
 * By default, Remix will handle hydrating your app on the client for you.
 * You are free to delete this file if you'd like to, but if you ever want it revealed again, you can run `npx remix reveal` ✨
 * For more information, see https://remix.run/file-conventions/entry.client
 */

import { HydratedRouter } from 'react-router/dom';
import { startTransition, StrictMode } from 'react';
import { hydrateRoot } from 'react-dom/client';

// NOTE: mswのモックAPIの設定するとき、
// worker.start()が非同期で実行されて、画面起動時にモックAPIが読み込まれないため、
// async functionでラップして、await worker.start()を実行する
async function main() {
  // NOTE: モックAPI用の設定（開発時のみ有効）
  if (process.env.NODE_ENV === 'development') {
    const { worker } = await import('./mocks/browser');
    await worker.start({
      onUnhandledRequest: 'warn', // 未処理のリクエストを警告
    });
    console.log('🔥 MSW Mock API が開始されました');
  }

  // NOTE: ReactのStrictModeを使用するとコンソールログが2回出力されるかも
  startTransition(() => {
    hydrateRoot(
      document,
      <StrictMode>
        <HydratedRouter />
      </StrictMode>,
    );
  });
}

main();
