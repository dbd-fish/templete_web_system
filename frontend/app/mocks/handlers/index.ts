import { loginHandler } from './loginHandler';
import { getMeHandler } from './getMeHandler';
import { logoutHandler } from './logoutHandler';
import { signupHandler } from './signupHandler';
import { sendVerifyEmailHandler } from './sendVerifyEmailHandler';
import { sendPasswordResetEmailHandler } from './sendPasswordResetEmailHandler';
import { resetPasswordHandler } from './resetPasswordHandler';
import { updateUserHandler } from './updateUserHandler';
import { deleteUserHandler } from './deleteUserHandler';

export const handlers = [
  // 認証関連のハンドラー
  loginHandler,
  getMeHandler,
  logoutHandler,
  signupHandler,
  sendVerifyEmailHandler,
  sendPasswordResetEmailHandler,
  resetPasswordHandler,
  updateUserHandler,
  deleteUserHandler,
];
