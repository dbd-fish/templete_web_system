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

    const response = await fetch(
      `${apiUrl}/api/auth/send-password-reset-email`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sendResetEmailData),
      },
    );

    console.log('res', response);
    if (!response.ok) {
      const errorResponse = await response.json();
      throw new Error(
        errorResponse.message || 'パスワード再設定に失敗しました',
      );
    }

    return response.json();
  } catch (error) {
    console.error('[fetchSendResetPasswordData] Error:', error);
    throw error;
  }
};
