import { SignupRequest, SuccessResponse, ErrorResponse } from '../../../commons/utils/types';
import { apiRequest } from '../../../commons/utils/apiErrorHandler';

export const fetchSignupData = async (token: string) => {
  const apiUrl = process.env.API_URL;

  try {
    const signupData = {
      token: token,
    };

    const response = await apiRequest(
      `${apiUrl}/api/v1/auth/signup`,
      {
        method: 'POST',
        body: JSON.stringify(signupData),
      }
    );

    const data = await response.json() as SuccessResponse;
    return data.success;
  } catch (error) {
    console.error('[fetchSignupData] Error:', error);
    throw error;
  }
};
