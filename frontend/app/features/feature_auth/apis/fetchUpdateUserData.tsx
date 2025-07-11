import { UserUpdate, UserResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

/**
 * ユーザー情報を更新する非同期関数
 * - '/api/v1/auth/me' エンドポイントを使用してユーザー情報を更新
 * - 成功時: 更新されたユーザー情報オブジェクトを返す
 * - 失敗時: エラーメッセージをスロー
 *
 * @param request - Requestオブジェクト（Cookie取得用）
 * @param updateData - 更新するユーザー情報
 */
export const fetchUpdateUserData = async (request: Request, updateData: UserUpdate) => {
  const apiUrl = process.env.API_URL;
  const cookieHeader = request.headers.get('Cookie');

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/me`,
      {
        method: 'PATCH',
        body: JSON.stringify(updateData),
      },
      cookieHeader || ''
    );

    const data = await response.json() as UserResponse;
    return data;
  } catch (error) {
    throw error;
  }
};