
import { UserResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

/**
 * ユーザー情報を取得する非同期関数
 * - '/api/v1/auth/me' エンドポイントからユーザー情報を取得
 * - 成功時: ユーザー情報オブジェクトを返す
 * - 失敗時: null を返す
 */
export const fetchUserData = async (request: Request) => {

  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  const cookieHeader = request.headers.get('Cookie');

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'POST',
      },
      cookieHeader || ''
    );

    const data = await response.json() as UserResponse;
    return { username: data.username, email: data.email };
  } catch (error) {
    // 認証エラーの場合はnullを返す
    if (error instanceof Error && error.message.includes('401')) {
      return null;
    }
    throw error;
  }
};
