/**
 * パスワードバリデーション関数
 * - 8文字以上
 * - 大文字・小文字をそれぞれ1文字以上含む
 * - 数字を1文字以上含む
 * - 特定の記号を1文字以上含む
 */
export const isPasswordValid = (password: string): boolean => {
  const passwordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[-!"#$%&()*+,./:;<=>?@[\\\]^_`{|}~])[A-Za-z\d\-!"#$%&()*+,./:;<=>?@[\\\]^_`{|}~]{8,}$/;
  return passwordRegex.test(password);
};

/**
 * 使用可能な記号を取得する関数
 */
export const getAllowedSymbols = (): string => {
  return `-!"#$%&()*+,./:;<=>?@[\\]^_\`{|}~`;
};
