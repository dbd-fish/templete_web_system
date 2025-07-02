import { loginHandler } from './loginHandler';
import { getMeHandler } from './getMeHandler';
import { logoutHandler } from './logoutHandler';
// 他のハンドラーもここでインポート
// import { exampleHandler } from './exampleHandler';

export const handlers = [
  loginHandler,
  getMeHandler,
  logoutHandler,
  // 他のハンドラーもここに追加
  // exampleHandler,
];
