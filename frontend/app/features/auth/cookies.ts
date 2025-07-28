// NOTE:ブラウザの開発者モードでHttpOnlyのクッキーを確認できる

/**
 * Cookieヘッダーから特定のCookieのみを抽出して安全なヘッダー文字列を生成
 *
 * @param cookieHeader - リクエストのCookieヘッダー文字列
 * @param cookieNames - 抽出したいCookie名の配列
 * @returns 指定されたCookieのみを含むCookieヘッダー文字列
 */
export function extractSpecificCookies(
  cookieHeader: string | null,
  cookieNames: string[],
): string {
  if (!cookieHeader) return '';

  const cookies = cookieHeader.split(';').map((cookie) => cookie.trim());
  const extractedCookies: string[] = [];

  for (const cookie of cookies) {
    const [name] = cookie.split('=');
    if (cookieNames.includes(name)) {
      extractedCookies.push(cookie);
    }
  }

  return extractedCookies.join('; ');
}

/**
 * 認証に必要なトークンCookieのみを抽出
 *
 * @param cookieHeader - リクエストのCookieヘッダー文字列
 * @returns 認証トークンCookieのみを含むヘッダー文字列
 */
export function extractAuthTokens(cookieHeader: string | null): string {
  return extractSpecificCookies(cookieHeader, ['authToken', 'refreshToken']);
}

/**
 * リフレッシュトークンのみを抽出
 *
 * @param cookieHeader - リクエストのCookieヘッダー文字列
 * @returns リフレッシュトークンのみを含むヘッダー文字列
 */
export function extractRefreshToken(cookieHeader: string | null): string {
  return extractSpecificCookies(cookieHeader, ['refreshToken']);
}
