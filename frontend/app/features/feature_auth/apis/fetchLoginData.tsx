
import { LoginRequest, TokenData, ErrorResponse } from '../../../commons/utils/types';
import { apiFormRequest } from '../../../commons/utils/apiErrorHandler';

/**
 * ユーザーのログインを処理する非同期関数
 * - '/api/v1/auth/login' エンドポイントを使用してログインリクエストを送信
 * - 成功時: Responseオブジェクトを返す
 * - 失敗時: ApiErrorをスロー
 *
 * @param email - ユーザーのメールアドレス
 * @param password - ユーザーのパスワード
 */
export const fetchLoginData = async (email: string, password: string) => {
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  try {
    const response = await apiFormRequest(
      `${apiUrl}/api/v1/auth/login`,
      {
        username: email, // OAuth2PasswordRequestFormは "username" フィールドを期待
        password: password,
      }
    );

    return response;
  } catch (error) {
    throw error;
  }
};
