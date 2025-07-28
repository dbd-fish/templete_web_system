/**
 * 管理者用マイページコンポーネント
 * 管理者権限専用のユーザー管理とシステム監視機能
 * 全ユーザー一覧とアカウント操作（削除・復旧・権限変更）を提供
 */
import { useState } from 'react';
import { Form } from 'react-router';
import { UserResponse as User, AdminUserResponse } from '~/features/auth/types';

interface AdminMyPageProps {
  user: User;
  users?: AdminUserResponse[];
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

export default function AdminMyPage({
  user,
  users = [],
  actionData,
}: AdminMyPageProps) {
  const [showUserManagement, setShowUserManagement] = useState(false);
  const [selectedUser, setSelectedUser] = useState<AdminUserResponse | null>(
    null,
  );
  const [editMode, setEditMode] = useState(false);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h1
          className="text-2xl font-bold text-red-600"
          data-cy="admin-mypage-title"
        >
          管理者マイページ
        </h1>
        <p className="text-muted-foreground mt-2">
          システム管理者として全機能にアクセス可能です
        </p>
      </div>

      {/* 全体的なエラー・成功メッセージ */}
      {actionData?.type === 'general' && actionData.error && (
        <div className="mb-4 text-sm text-destructive border border-destructive/50 bg-destructive/50 p-3 rounded-md">
          {actionData.error}
        </div>
      )}

      {actionData?.success && (
        <div className="mb-4 text-sm text-green-600 border border-green-200 bg-green-50 p-3 rounded-md">
          {actionData.success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* メインエリア（左側3カラム） */}
        <div className="lg:col-span-3 space-y-6">
          {/* 管理者プロフィール情報 */}
          <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border-2 border-red-200 p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center text-red-700">
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
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
              管理者プロフィール
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="admin-email"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  メールアドレス
                </label>
                <div
                  id="admin-email"
                  className="text-sm p-2 bg-white border rounded-md"
                >
                  {user.email}
                </div>
              </div>
              <div>
                <label
                  htmlFor="admin-username"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  ユーザー名
                </label>
                <div
                  id="admin-username"
                  className="text-sm p-2 bg-white border rounded-md"
                >
                  {user.username}
                </div>
              </div>
              <div>
                <label
                  htmlFor="admin-role"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  権限レベル
                </label>
                <div
                  id="admin-role"
                  className="text-sm p-2 bg-red-100 border border-red-300 rounded-md font-semibold text-red-700"
                >
                  {getUserRoleText(user.user_role)}
                </div>
              </div>
              <div>
                <label
                  htmlFor="admin-status"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  アカウント状態
                </label>
                <div
                  id="admin-status"
                  className="text-sm p-2 bg-green-100 border border-green-300 rounded-md font-semibold text-green-700"
                >
                  {getUserStatusText(user.user_status)}
                </div>
              </div>
            </div>
          </div>

          {/* 管理者機能パネル */}
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
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              管理者機能
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => setShowUserManagement(!showUserManagement)}
                className="p-4 text-left border rounded-lg hover:bg-blue-50 transition-colors border-blue-200"
                data-cy="user-management-toggle"
              >
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 mr-3 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                    />
                  </svg>
                  <div>
                    <p className="font-medium text-blue-700">ユーザー管理</p>
                    <p className="text-sm text-muted-foreground">
                      全ユーザーの管理・編集
                    </p>
                  </div>
                </div>
              </button>

              <div className="p-4 text-left border rounded-lg border-gray-200">
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 mr-3 text-gray-600"
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
                  <div>
                    <p className="font-medium text-gray-700">システム統計</p>
                    <p className="text-sm text-muted-foreground">
                      利用状況・アクセス統計
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 text-left border rounded-lg border-gray-200">
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 mr-3 text-gray-600"
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
                  <div>
                    <p className="font-medium text-gray-700">
                      セキュリティ管理
                    </p>
                    <p className="text-sm text-muted-foreground">
                      権限・アクセス制御
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 text-left border rounded-lg border-gray-200">
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 mr-3 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                  </svg>
                  <div>
                    <p className="font-medium text-gray-700">システム設定</p>
                    <p className="text-sm text-muted-foreground">
                      全体設定・メンテナンス
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ユーザー管理パネル */}
          {showUserManagement && (
            <div
              className="bg-card rounded-lg border p-6"
              data-cy="user-management-panel"
            >
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
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                  />
                </svg>
                ユーザー管理
              </h3>

              <div className="overflow-x-auto">
                <table
                  className="w-full border-collapse border border-gray-300"
                  data-cy="users-table"
                >
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        ユーザー名
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        メールアドレス
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        権限
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        状態
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        作成日
                      </th>
                      <th className="border border-gray-300 px-4 py-2 text-left">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((adminUser) => (
                      <tr key={adminUser.user_id} className="hover:bg-gray-50">
                        <td className="border border-gray-300 px-4 py-2">
                          {adminUser.username}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {adminUser.email}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              adminUser.user_role >= 4
                                ? 'bg-red-100 text-red-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {getUserRoleText(adminUser.user_role)}
                          </span>
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              adminUser.user_status === 1
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {getUserStatusText(adminUser.user_status)}
                          </span>
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {new Date(adminUser.created_at).toLocaleDateString(
                            'ja-JP',
                          )}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          <button
                            onClick={() => {
                              setSelectedUser(adminUser);
                              setEditMode(true);
                            }}
                            className="text-blue-600 hover:underline mr-2"
                            data-cy="edit-user-button"
                          >
                            編集
                          </button>
                          {adminUser.deleted_at ? (
                            <Form method="post" className="inline">
                              <input
                                type="hidden"
                                name="_action"
                                value="restoreUser"
                              />
                              <input
                                type="hidden"
                                name="userId"
                                value={adminUser.user_id}
                              />
                              <button
                                type="submit"
                                className="text-green-600 hover:underline"
                                data-cy="restore-user-button"
                              >
                                復活
                              </button>
                            </Form>
                          ) : (
                            <Form method="post" className="inline">
                              <input
                                type="hidden"
                                name="_action"
                                value="deleteUser"
                              />
                              <input
                                type="hidden"
                                name="userId"
                                value={adminUser.user_id}
                              />
                              <button
                                type="submit"
                                className="text-red-600 hover:underline"
                                data-cy="delete-user-button"
                                onClick={(e) => {
                                  if (
                                    !confirm(
                                      '本当にこのユーザーを削除しますか？',
                                    )
                                  ) {
                                    e.preventDefault();
                                  }
                                }}
                              >
                                削除
                              </button>
                            </Form>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* サイドバー（右側1カラム） */}
        <div className="space-y-6">
          {/* アカウント管理 */}
          <div
            className="bg-card rounded-lg border p-6"
            data-cy="admin-account-management"
          >
            <h3 className="text-lg font-semibold mb-4">アカウント管理</h3>
            <div className="space-y-3">
              <Form method="post" className="w-full">
                <input type="hidden" name="_action" value="logout" />
                <button
                  type="submit"
                  className="w-full p-3 text-left border rounded-lg hover:bg-muted transition-colors"
                  data-cy="admin-logout-button"
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
            </div>
          </div>

          {/* 管理者統計情報 */}
          <div className="bg-gradient-to-b from-red-50 to-orange-50 rounded-lg border-2 border-red-200 p-6">
            <h3 className="text-lg font-semibold mb-4 text-red-700">
              管理者情報
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">権限レベル</span>
                <span className="font-semibold text-red-600">管理者</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">最終ログイン</span>
                <span>今日</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">管理開始日</span>
                <span>2025年1月</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">管理ユーザー数</span>
                <span className="font-semibold">{users.length}人</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ユーザー編集モーダル */}
      {editMode && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">ユーザー編集</h3>
            <Form
              method="post"
              onSubmit={() => {
                setEditMode(false);
                setSelectedUser(null);
              }}
            >
              <input type="hidden" name="_action" value="updateUser" />
              <input type="hidden" name="userId" value={selectedUser.user_id} />

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="edit-username"
                    className="block text-sm font-medium mb-1"
                  >
                    ユーザー名
                  </label>
                  <input
                    type="text"
                    id="edit-username"
                    name="username"
                    defaultValue={selectedUser.username}
                    className="w-full p-2 border rounded-md"
                  />
                </div>

                <div>
                  <label
                    htmlFor="edit-email"
                    className="block text-sm font-medium mb-1"
                  >
                    メールアドレス
                  </label>
                  <input
                    type="email"
                    id="edit-email"
                    name="email"
                    defaultValue={selectedUser.email}
                    className="w-full p-2 border rounded-md"
                  />
                </div>

                <div>
                  <label
                    htmlFor="edit-role"
                    className="block text-sm font-medium mb-1"
                  >
                    権限
                  </label>
                  <select
                    id="edit-role"
                    name="user_role"
                    defaultValue={selectedUser.user_role}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value={1}>ゲスト</option>
                    <option value={2}>無料会員</option>
                    <option value={3}>一般会員</option>
                    <option value={4}>管理者</option>
                    <option value={5}>オーナー</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="edit-status"
                    className="block text-sm font-medium mb-1"
                  >
                    状態
                  </label>
                  <select
                    id="edit-status"
                    name="user_status"
                    defaultValue={selectedUser.user_status}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value={1}>アクティブ</option>
                    <option value={2}>停止中</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setEditMode(false);
                    setSelectedUser(null);
                  }}
                  className="px-4 py-2 border rounded-md hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  更新
                </button>
              </div>
            </Form>
          </div>
        </div>
      )}
    </div>
  );
}
