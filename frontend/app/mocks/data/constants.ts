/**
 * MSWモック用の共通定数
 * 
 * @description
 * テスト用のアカウント情報、API定数、レスポンスメッセージなど
 * 全てのモックハンドラーで共通して使用される定数を定義
 */

// ==================== JWTトークン ====================

/** モック用のJWTアクセストークン */
export const MOCK_ACCESS_TOKEN = 'mock-jwt-access-token-12345';


/** パスワードリセット用のモックトークン */
export const MOCK_RESET_TOKEN = 'mock-password-reset-token-abcde';

/** 認証メール用のモックトークン */
export const MOCK_VERIFY_TOKEN = 'mock-email-verify-token-fghij';



// ==================== APIレスポンスメッセージ ====================

/** ログイン成功メッセージ */
export const MSG_LOGIN_SUCCESS = 'ログインに成功しました';

/** ログアウト成功メッセージ */
export const MSG_LOGOUT_SUCCESS = 'ログアウトしました';

/** ユーザー情報取得成功メッセージ */
export const MSG_USER_INFO_SUCCESS = 'ユーザー情報を取得しました';

/** ユーザー情報更新成功メッセージ */
export const MSG_USER_UPDATE_SUCCESS = 'ユーザー情報が正常に更新されました';

/** アカウント削除成功メッセージ */
export const MSG_ACCOUNT_DELETE_SUCCESS = 'ユーザーアカウントが正常に削除されました';

/** ユーザー登録成功メッセージ */
export const MSG_SIGNUP_SUCCESS = 'ユーザー登録が完了しました';

/** 認証メール送信成功メッセージ */
export const MSG_VERIFY_EMAIL_SUCCESS = '認証メールを送信しました。メールをご確認ください';

/** パスワードリセットメール送信成功メッセージ */
export const MSG_RESET_EMAIL_SUCCESS = 'パスワードリセットメールを送信しました';

/** パスワードリセット成功メッセージ */
export const MSG_PASSWORD_RESET_SUCCESS = 'パスワードが正常にリセットされました';

// ==================== エラーメッセージ ====================

/** 認証失敗メッセージ */
export const MSG_AUTH_FAILED = 'メールアドレスまたはパスワードが正しくありません';

/** 無効なトークンメッセージ */
export const MSG_INVALID_TOKEN = '無効なトークンです';

/** ユーザーが見つからないメッセージ */
export const MSG_USER_NOT_FOUND = 'ユーザーが見つかりません';

/** ユーザーが既に存在するメッセージ */
export const MSG_USER_ALREADY_EXISTS = 'このメールアドレスは既に登録されています';

// ==================== 遅延設定 ====================

/** API レスポンスの遅延時間（ミリ秒） */
export const MOCK_DELAY_MS = 800;

/** 高速レスポンス用の遅延時間（ミリ秒） */
export const MOCK_DELAY_FAST_MS = 200;

/** 低速レスポンス用の遅延時間（ミリ秒） */
export const MOCK_DELAY_SLOW_MS = 2000;

// ==================== その他の設定 ====================

/** Cookie名: 認証トークン */
export const COOKIE_AUTH_TOKEN = 'authToken';

/** Cookie有効期限（秒） */
export const COOKIE_MAX_AGE = 60 * 60 * 3; // 3時間