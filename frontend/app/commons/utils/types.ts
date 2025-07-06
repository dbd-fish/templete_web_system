// NOTE: 全loader関数共通の返り値の型を定義。
export type LoaderDataType = {
  user?: { email: string; username: string }; // 必要なプロパティを定義
  signupData?: { success: boolean };
  test?: { test1: number; test2: string }; // 必要なプロパティを定義
};
