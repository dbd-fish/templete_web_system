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
    const response = await fetch(`${apiUrl}/api/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(resetPasswordData),
    });

    if (!response.ok) {
      throw new Error('パスワードリセットに失敗しました');
    }

    return response.json();
  } catch (error) {
    console.error('[fetchResetPasswordData] Error:', error);
    throw error;
  }
};
