export const fetchSignupData = async (token: string) => {
  const apiUrl = process.env.API_URL;

  try {
    const signupData = {
      token: token,
    };

    const response = await fetch(`${apiUrl}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });

    return response.ok;
  } catch (error) {
    console.error('[fetchSignupData] Error:', error);
    throw error;
  }
};
