import { PasswordResetRequest, SuccessResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

export const fetchResetPasswordData = async (
  token: string,
  newPassword: string,
) => {
  const apiUrl = process.env.API_URL;
  const resetPasswordData = {
    token: token, // 空白を削除
    new_password: newPassword.trim(),
  };

  try {
    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/reset-password`,
      {
        method: 'POST',
        body: JSON.stringify(resetPasswordData),
      }
    );

    return response.json() as Promise<SuccessResponse>;
  } catch (error) {
    console.error('[fetchResetPasswordData] Error:', error);
    throw error;
  }
};
