import { SendPasswordResetEmailRequest, SuccessResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

export const fetchSendResetPasswordData = async (email: string) => {
  const apiUrl = process.env.API_URL;

  try {
    // 会員登録データをオブジェクトとして構築
    const sendResetEmailData = {
      email: email.trim(), // 空白を削除
    };

    // 不要なフィールドのチェック（例: 空文字列）
    Object.keys(sendResetEmailData).forEach((key) => {
      if (!sendResetEmailData[key as keyof typeof sendResetEmailData]) {
        throw new Error(`${key} の値が無効です`);
      }
    });

    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/send-password-reset-email`,
      {
        method: 'POST',
        body: JSON.stringify(sendResetEmailData),
      }
    );

    return response.json() as Promise<SuccessResponse>;
  } catch (error) {
    console.error('[fetchSendResetPasswordData] Error:', error);
    throw error;
  }
};
