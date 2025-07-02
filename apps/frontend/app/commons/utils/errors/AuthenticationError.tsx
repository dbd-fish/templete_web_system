/**
 * 認証エラーを表すカスタムエラークラス。
 *
 */
export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}
