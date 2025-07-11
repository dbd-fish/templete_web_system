import { MessageResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

/**
 * ユーザーアカウントを削除する非同期関数
 * - '/api/v1/auth/me' エンドポイントを使用してアカウントを削除
 * - 成功時: 削除確認メッセージを返す
 * - 失敗時: エラーメッセージをスロー
 *
 * @param request - Requestオブジェクト（Cookie取得用）
 */
export const fetchDeleteUserData = async (request: Request) => {
  const apiUrl = process.env.API_URL;
  const cookieHeader = request.headers.get('Cookie');

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'DELETE',
      },
      cookieHeader || ''
    );

    const data = await response.json() as MessageResponse;
    return data;
  } catch (error) {
    throw error;
  }
};