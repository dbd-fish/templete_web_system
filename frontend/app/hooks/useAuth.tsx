import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';

/**
 * 認証状態の型定義
 */
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}

/**
 * ユーザー情報の型定義
 */
interface User {
  email: string;
  username: string;
  user_role: number;
  user_status: number;
  contact_number?: string;
  date_of_birth?: string;
}

/**
 * 認証コンテキストの型定義
 */
interface AuthContextType extends AuthState {
  login: (user: User) => void;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

/**
 * 認証コンテキスト
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * 認証プロバイダーのProps
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * 認証プロバイダーコンポーネント
 * 
 * アプリケーション全体の認証状態を管理します
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
  });

  /**
   * ログイン処理
   */
  const login = (user: User) => {
    setAuthState({
      isAuthenticated: true,
      user,
      isLoading: false,
    });
  };

  /**
   * ログアウト処理
   */
  const logout = async (): Promise<void> => {
    try {
      // バックエンドのログアウトAPIを呼び出し
      const response = await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include', // HttpOnlyクッキーを送信
      });

      if (!response.ok) {
        console.warn('ログアウトAPIの呼び出しに失敗しましたが、クライアント側の状態をクリアします');
      }
    } catch (error) {
      console.error('ログアウト処理エラー:', error);
    } finally {
      // レスポンスの成功/失敗に関わらず、クライアント側の認証状態をクリア
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });
    }
  };

  /**
   * 認証状態確認
   */
  const checkAuthStatus = useCallback(async (): Promise<void> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch('/api/v1/auth/me', {
        method: 'POST',
        credentials: 'include', // HttpOnlyクッキーを送信
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setAuthState({
            isAuthenticated: true,
            user: data.data,
            isLoading: false,
          });
        } else {
          setAuthState({
            isAuthenticated: false,
            user: null,
            isLoading: false,
          });
        }
      } else {
        setAuthState({
          isAuthenticated: false,
          user: null,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error('認証状態確認エラー:', error);
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });
    }
  }, []);

  /**
   * 認証状態の更新（トークンリフレッシュなど）
   */
  const refreshAuth = useCallback(async (): Promise<void> => {
    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include', // HttpOnlyクッキーを送信
      });

      if (response.ok) {
        // リフレッシュ成功後、ユーザー情報を再取得
        await checkAuthStatus();
      } else {
        // リフレッシュ失敗時は認証状態をクリア
        setAuthState({
          isAuthenticated: false,
          user: null,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error('認証更新エラー:', error);
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });
    }
  }, [checkAuthStatus]);

  /**
   * 初期認証状態確認
   */
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  /**
   * 定期的な認証状態確認（10分間隔）
   */
  useEffect(() => {
    if (authState.isAuthenticated) {
      const interval = setInterval(() => {
        refreshAuth();
      }, 10 * 60 * 1000); // 10分

      return () => clearInterval(interval);
    }
  }, [authState.isAuthenticated, refreshAuth]);

  const contextValue: AuthContextType = {
    ...authState,
    login,
    logout,
    checkAuthStatus,
    refreshAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * 認証フック
 * 
 * コンポーネントで認証状態や認証処理を使用するためのフック
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * 認証が必要なページ用のフック
 * 
 * 未認証時にログインページにリダイレクトする
 */
export function useRequireAuth(): AuthContextType {
  const auth = useAuth();

  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      // 未認証の場合、ログインページにリダイレクト
      window.location.href = '/login';
    }
  }, [auth.isLoading, auth.isAuthenticated]);

  return auth;
}

/**
 * ゲスト専用ページ用のフック
 * 
 * 認証済みの場合にマイページにリダイレクトする
 */
export function useRequireGuest(): AuthContextType {
  const auth = useAuth();

  useEffect(() => {
    if (!auth.isLoading && auth.isAuthenticated) {
      // 認証済みの場合、マイページにリダイレクト
      window.location.href = '/mypage';
    }
  }, [auth.isLoading, auth.isAuthenticated]);

  return auth;
}