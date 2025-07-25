/**
 * 一般ユーザー用マイページコンポーネント
 * 一般ユーザー権限でのプロフィール表示と編集機能
 * ログアウト機能とユーザー情報管理機能を提供
 */
import { Form } from 'react-router';
import { UserResponse as User } from '~/features/auth/types';
import ProfileCard from './ProfileCard';

interface RegularMyPageProps {
  user: User;
  actionData?: {
    error?: string;
    success?: string;
    type?: string;
  };
}

const getUserRoleText = (role: number): string => {
  switch (role) {
    case 1:
      return 'ゲスト';
    case 2:
      return '無料会員';
    case 3:
      return '一般会員';
    case 4:
      return '管理者';
    case 5:
      return 'オーナー';
    default:
      return '不明';
  }
};

const getUserStatusText = (status: number): string => {
  switch (status) {
    case 1:
      return 'アクティブ';
    case 2:
      return '停止中';
    default:
      return '不明';
  }
};

export default function RegularMyPage({
  user,
  actionData,
}: RegularMyPageProps) {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold" data-cy="mypage-title">
          マイページ
        </h1>
        <p className="text-muted-foreground mt-2">
          アカウント情報の管理とセキュリティ設定
        </p>
      </div>

      {/* 全体的なエラー・成功メッセージ */}
      {actionData?.type === 'general' && actionData.error && (
        <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md">
          {actionData.error}
        </div>
      )}

      {actionData?.success && (
        <div className="mb-4 text-sm text-green-600 border border-green-200 bg-green-50 p-3 rounded-md">
          {actionData.success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* メインエリア（左側2カラム） */}
        <div className="lg:col-span-2 space-y-6">
          {/* プロフィール情報 */}
          <ProfileCard />

          {/* セキュリティ設定エリア */}
          <div className="bg-card rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              セキュリティ設定
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">パスワード</p>
                  <p className="text-sm text-muted-foreground">
                    最後に変更: 30日前
                  </p>
                </div>
                <a
                  href="/send-reset-password-email"
                  className="text-primary hover:underline text-sm"
                >
                  変更する
                </a>
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">ログインデバイス</p>
                  <p className="text-sm text-muted-foreground">
                    現在のデバイス: ブラウザ (Chrome)
                  </p>
                </div>
                <span className="text-green-600 text-sm">アクティブ</span>
              </div>
            </div>
          </div>

          {/* 利用状況エリア */}
          <div className="bg-card rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              利用状況
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-muted-foreground">
                  今月のログイン回数
                </p>
                <p className="text-2xl font-bold text-blue-600">12回</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-muted-foreground">
                  利用開始日からの日数
                </p>
                <p className="text-2xl font-bold text-green-600">30日</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-sm text-muted-foreground">
                  アカウントレベル
                </p>
                <p className="text-lg font-bold text-purple-600">
                  {getUserRoleText(user.user_role)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* サイドバー（右側1カラム） */}
        <div className="space-y-6">
          {/* アカウント管理 */}
          <div className="bg-card rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">アカウント管理</h3>
            <div className="space-y-3">
              <Form method="post" className="w-full">
                <input type="hidden" name="_action" value="logout" />
                <button
                  type="submit"
                  className="w-full p-3 text-left border rounded-lg hover:bg-muted transition-colors"
                  data-cy="logout-form-button"
                >
                  <div className="flex items-center">
                    <svg
                      className="w-4 h-4 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    ログアウト
                  </div>
                </button>
              </Form>

              <Form
                method="post"
                className="w-full"
                onSubmit={(e) => {
                  if (
                    !confirm(
                      '本当にアカウントを削除しますか？この操作は取り消せません。',
                    )
                  ) {
                    e.preventDefault();
                  }
                }}
              >
                <input type="hidden" name="_action" value="deleteAccount" />
                <button
                  type="submit"
                  className="w-full p-3 text-left border border-destructive/20 rounded-lg hover:bg-destructive/10 transition-colors text-destructive"
                  data-cy="delete-account-button"
                >
                  <div className="flex items-center">
                    <svg
                      className="w-4 h-4 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                    アカウント削除
                  </div>
                </button>
              </Form>
            </div>
          </div>

          {/* ユーザー統計情報 */}
          <div className="bg-card rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">アカウント情報</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">登録日</span>
                <span>2025年1月</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">認証方法</span>
                <span>メールアドレス</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">アカウントタイプ</span>
                <span className="font-semibold">
                  {getUserRoleText(user.user_role)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">アカウント状態</span>
                <span
                  className={`font-semibold ${
                    user.user_status === 1 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {getUserStatusText(user.user_status)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">最終ログイン</span>
                <span>今日</span>
              </div>
            </div>
          </div>

          {/* プレミアム機能案内（非管理者のみ） */}
          {user.user_role < 4 && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200 p-6">
              <h3 className="text-lg font-semibold mb-2 text-blue-700">
                プレミアム機能
              </h3>
              <p className="text-sm text-blue-600 mb-4">
                さらに高度な機能をご利用いただけます
              </p>
              <div className="space-y-2 text-sm text-blue-700">
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  高度な分析機能
                </div>
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  優先サポート
                </div>
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  容量無制限
                </div>
              </div>
              <button
                className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                data-cy="upgrade-button"
              >
                アップグレード
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
