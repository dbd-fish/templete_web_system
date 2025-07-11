
import { MessageResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

/**
 * ユーザーのログアウトを処理する非同期関数
 * - '/api/v1/auth/logout' エンドポイントを使用してログアウトリクエストを送信
 * - 成功時: レスポンスを返す
 * - 失敗時: エラーメッセージをスロー
 */
export const fetchLogoutData = async (request: Request) => {

  // NOTE: processが使用できないため、API URLを直接指定
  const apiUrl = process.env.API_URL; // 環境変数からURLを取得

  try {
    const cookieHeader = request.headers.get('Cookie');
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/logout`,
      {
        method: 'POST',
      },
      cookieHeader || ''
    );

    return response;
  } catch (error) {
    throw error;
  }
};
