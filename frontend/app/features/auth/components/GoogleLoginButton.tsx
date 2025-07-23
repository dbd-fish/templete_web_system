/**
 * Googleログインボタンコンポーネント
 * Google OAuth 2.0を使用したシングルサインオン機能
 * Googleアカウントでの簡単ログインが可能
 */
import { useEffect, useRef, useState } from 'react';
import { Button } from '~/components/ui/button';
import { 
  initializeGoogleAuth, 
  authenticateWithGoogle, 
  validateGoogleConfig 
} from '~/utils/googleAuth';

/**
 * GoogleLoginButtonProps インターフェース
 */
interface GoogleLoginButtonProps {
  onSuccess?: (message: string) => void;
  onError?: (error: string) => void;
  onLoginStart?: () => void;
  onLoginEnd?: () => void;
  disabled?: boolean;
}

/**
 * GoogleLoginButton コンポーネント
 * 
 * Google OAuth認証用のボタンコンポーネント
 * Google Identity Services (gsi) ライブラリと統合済み
 */
export default function GoogleLoginButton({
  onSuccess,
  onError,
  onLoginStart,
  onLoginEnd,
  disabled = false,
}: GoogleLoginButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const initializeAttempted = useRef(false);

  // Google認証の初期化
  useEffect(() => {
    if (initializeAttempted.current || disabled) {
      return;
    }

    initializeAttempted.current = true;

    const initializeAuth = async () => {
      try {
        // 環境設定の検証
        if (!validateGoogleConfig()) {
          if (onError) {
            onError('Google OAuth設定が不完全です。管理者にお問い合わせください。');
          }
          return;
        }

        await initializeGoogleAuth(
          async (credential: string) => {
            await handleGoogleCredential(credential);
          },
          (error: string) => {
            console.error('Google認証初期化エラー:', error);
            if (onError) {
              onError(`Google認証の初期化に失敗しました: ${error}`);
            }
          }
        );

        setIsInitialized(true);
      } catch (error) {
        console.error('Google認証初期化エラー:', error);
        if (onError) {
          onError('Google認証の初期化に失敗しました');
        }
      }
    };

    initializeAuth();
  }, [disabled, onError]);

  /**
   * Googleから受け取った認証情報を処理
   */
  const handleGoogleCredential = async (credential: string) => {
    try {
      setIsLoading(true);
      if (onLoginStart) {
        onLoginStart();
      }

      const result = await authenticateWithGoogle(credential);

      if (result.success) {
        if (onSuccess && result.message) {
          onSuccess(result.message);
        }
      } else {
        if (onError && result.error) {
          onError(result.error);
        }
      }
    } catch (error) {
      console.error('Google認証処理エラー:', error);
      if (onError) {
        onError('Google認証処理中にエラーが発生しました');
      }
    } finally {
      setIsLoading(false);
      if (onLoginEnd) {
        onLoginEnd();
      }
    }
  };

  /**
   * Googleログインボタンクリック処理
   */
  const handleGoogleLogin = () => {
    if (isLoading || disabled || !isInitialized) {
      return;
    }

    // Google Identity Services のプロンプトを表示
    // 実際の認証は handleGoogleCredential で処理される
    try {
      if (window.google?.accounts?.id) {
        window.google.accounts.id.prompt();
      } else {
        if (onError) {
          onError('Google認証サービスが利用できません');
        }
      }
    } catch (error) {
      console.error('Googleログインプロンプト表示エラー:', error);
      if (onError) {
        onError('Googleログインの開始に失敗しました');
      }
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full flex items-center justify-center gap-2 border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      onClick={handleGoogleLogin}
      disabled={isLoading || disabled || !isInitialized}
      data-cy="google-login-button"
    >
      {isLoading ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600"></div>
          <span>ログイン中...</span>
        </>
      ) : !isInitialized ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600"></div>
          <span>初期化中...</span>
        </>
      ) : (
        <>
          {/* Google アイコン SVG */}
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Googleでログイン</span>
        </>
      )}
    </Button>
  );
}