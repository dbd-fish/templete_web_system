export const fetchSendVerifyEmailData = async (
  email: string,
  password: string,
  username: string,
) => {
  const apiUrl = process.env.API_URL;

  try {
    // 会員登録データをオブジェクトとして構築
    const signupData = {
      email: email.trim(), // 空白を削除
      password: password.trim(),
      username: username.trim(),
    };

    // 不要なフィールドのチェック（例: 空文字列）
    Object.keys(signupData).forEach((key) => {
      if (!signupData[key as keyof typeof signupData]) {
        throw new Error(`${key} の値が無効です`);
      }
    });

    const response = await fetch(`${apiUrl}/api/auth/send-verify-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });

    if (!response.ok) {
      const errorResponse = await response.json();
      throw new Error(errorResponse.message || '会員登録に失敗しました');
    }

    return response.json();
  } catch (error) {
    console.error('[fetchSendVerifyEmailData] Error:', error);
    throw error;
  }
};
