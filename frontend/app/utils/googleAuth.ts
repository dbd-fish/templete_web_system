/**
 * Google認証ユーティリティ
 *
 * Google Identity Servicesを使用したOAuth認証の処理を担当
 */

// Google Identity Services の型定義（簡易版）
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: GoogleIdConfiguration) => void;
          prompt: () => void;
          renderButton: (
            parent: HTMLElement,
            options: GoogleButtonConfiguration,
          ) => void;
        };
      };
    };
  }
}

interface GoogleIdConfiguration {
  client_id: string;
  callback: (response: GoogleCredentialResponse) => void;
  auto_select?: boolean;
  cancel_on_tap_outside?: boolean;
}

interface GoogleButtonConfiguration {
  theme?: 'outline' | 'filled_blue' | 'filled_black';
  size?: 'large' | 'medium' | 'small';
  text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
  shape?: 'rectangular' | 'pill' | 'circle' | 'square';
  width?: string | number;
}

interface GoogleCredentialResponse {
  credential: string;
  select_by?: string;
}

/**
 * Google認証の初期化状態
 */
let isGoogleInitialized = false;

/**
 * Googleクライアント設定
 */
const GOOGLE_CONFIG = {
  CLIENT_ID:
    import.meta.env.VITE_GOOGLE_CLIENT_ID ||
    'mock-google-client-id-for-development.apps.googleusercontent.com', // 開発用モック値
};

/**
 * Google Identity Services スクリプトを読み込む
 */
export const loadGoogleScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 既に読み込み済みの場合
    if (window.google?.accounts?.id) {
      resolve();
      return;
    }

    // スクリプトが既に存在する場合は削除して再読み込み
    const existingScript = document.querySelector(
      'script[src*="accounts.google.com"]',
    );
    if (existingScript) {
      existingScript.remove();
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;

    script.onload = () => {
      // Google スクリプトの読み込み完了後、少し待ってから初期化
      setTimeout(() => {
        if (window.google?.accounts?.id) {
          resolve();
        } else {
          reject(
            new Error('Google Identity Services の読み込みに失敗しました'),
          );
        }
      }, 100);
    };

    script.onerror = () => {
      reject(
        new Error(
          'Google Identity Services スクリプトの読み込みに失敗しました',
        ),
      );
    };

    document.head.appendChild(script);
  });
};

/**
 * Google認証の初期化
 */
export const initializeGoogleAuth = async (
  onSuccess: (credential: string) => void,
  onError: (error: string) => void,
): Promise<void> => {
  try {
    if (isGoogleInitialized) {
      return;
    }

    await loadGoogleScript();

    if (!window.google?.accounts?.id) {
      throw new Error('Google Identity Services が利用できません');
    }

    window.google.accounts.id.initialize({
      client_id: GOOGLE_CONFIG.CLIENT_ID,
      callback: (response: GoogleCredentialResponse) => {
        if (response.credential) {
          onSuccess(response.credential);
        } else {
          onError('Google認証のレスポンスが無効です');
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
    });

    isGoogleInitialized = true;
  } catch (error) {
    const errorMessage =
      error instanceof Error
        ? error.message
        : 'Google認証の初期化に失敗しました';
    onError(errorMessage);
  }
};

/**
 * Googleログインボタンをレンダリング
 */
export const renderGoogleButton = (
  element: HTMLElement,
  options: GoogleButtonConfiguration = {},
): void => {
  if (!window.google?.accounts?.id) {
    console.error('Google Identity Services が初期化されていません');
    return;
  }

  const defaultOptions: GoogleButtonConfiguration = {
    theme: 'outline',
    size: 'large',
    text: 'signin_with',
    shape: 'rectangular',
    width: '100%',
  };

  window.google.accounts.id.renderButton(element, {
    ...defaultOptions,
    ...options,
  });
};

/**
 * Googleログインプロンプトを表示
 */
export const showGooglePrompt = (): void => {
  if (!window.google?.accounts?.id) {
    console.error('Google Identity Services が初期化されていません');
    return;
  }

  window.google.accounts.id.prompt();
};

/**
 * バックエンドAPIにGoogle認証情報を送信
 */
export const authenticateWithGoogle = async (
  credential: string,
): Promise<{ success: boolean; message?: string; error?: string }> => {
  try {
    // 実際のバックエンドAPIに接続（Docker環境対応）
    const apiUrl = 'http://backend:8000';
    const response = await fetch(`${apiUrl}/api/v1/auth/google-login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id_token: credential,
      }),
      credentials: 'include', // HttpOnlyクッキーを受信するため
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        message: data.message || 'Googleログインに成功しました',
      };
    } else {
      return {
        success: false,
        error: data.detail || 'Googleログインに失敗しました',
      };
    }
  } catch (error) {
    console.error('Google認証API呼び出しエラー:', error);
    return {
      success: false,
      error: 'ネットワークエラーが発生しました',
    };
  }
};

/**
 * 環境設定の検証
 */
export const validateGoogleConfig = (): boolean => {
  if (!GOOGLE_CONFIG.CLIENT_ID) {
    console.error(
      'Google Client ID が設定されていません。環境変数を確認してください。',
    );
    return false;
  }

  // 開発環境では本番のGoogle Client IDでなくてもOKとする
  if (
    import.meta.env.DEV &&
    GOOGLE_CONFIG.CLIENT_ID.includes('mock-google-client-id')
  ) {
    console.warn('開発環境でモックGoogle Client IDを使用しています。');
    return true; // 開発環境では通す
  }

  // 本番環境では適切なGoogle Client IDが必要
  if (
    GOOGLE_CONFIG.CLIENT_ID ===
    'your-google-client-id-here.apps.googleusercontent.com'
  ) {
    console.error(
      '本番用のGoogle Client ID が設定されていません。環境変数を確認してください。',
    );
    return false;
  }

  return true;
};
