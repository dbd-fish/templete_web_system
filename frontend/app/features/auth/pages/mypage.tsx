import {
  LoaderFunction,
  ActionFunction,
  redirect,
  MetaFunction,
} from 'react-router';
import { useActionData, useLoaderData } from 'react-router';
import AdminMyPage from '~/features/auth/components/AdminMyPage';
import RegularMyPage from '~/features/auth/components/RegularMyPage';
import { userDataLoader } from '~/features/auth/loaders/userDataLoader';
import { AuthenticationError } from '../errors/AuthenticationError';
import { logoutAction } from '~/features/auth/actions/logoutAction';
import { updateUser, deleteUser } from '~/features/auth/apis/authApi';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import {
  UserResponse as User,
  AdminUserResponse,
  AdminUserUpdateData,
} from '~/features/auth/types';
import { getApiUrl } from '~/config/api';

/**
 * メタデータ関数:
 * - ページのタイトルとメタデータを設定
 */
export const meta: MetaFunction = () => {
  return [
    { title: 'マイページ | Webシステム開発テンプレート' },
    {
      name: 'description',
      content: 'ユーザープロフィールの確認・編集ページです。',
    },
  ];
};

/**
 * 管理者用ユーザー一覧取得関数
 */
async function fetchAdminUsers(request: Request): Promise<AdminUserResponse[]> {
  try {
    const apiUrl = getApiUrl();
    const response = await fetch(
      `${apiUrl}/api/v1/auth/admin/users?page=1&page_size=50`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Cookie: request.headers.get('Cookie') || '',
        },
        credentials: 'include',
      },
    );

    if (!response.ok) {
      console.warn('Failed to fetch admin users:', response.status);
      return [];
    }

    const result = await response.json();
    return result.data?.users || [];
  } catch (error) {
    console.warn('Error fetching admin users:', error);
    return [];
  }
}

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 管理者の場合はユーザー一覧も取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  try {
    // throw new Error('Error occurred in MyPage Loader');
    // authTokenLoaderを削除し、直接userDataLoaderで認証チェック
    const userData = await userDataLoader(request);

    let users: AdminUserResponse[] = [];

    // 管理者権限のチェック（ROLE_ADMIN = 4以上）
    if (userData && userData.user_role >= 4) {
      users = await fetchAdminUsers(request);
    }

    const responseBody = {
      user: userData,
      users,
    };
    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    if (error instanceof AuthenticationError) {
      return redirect('/login');
    }

    console.error('Unexpected error in MyPage loader:', error);
    throw new Response('ユーザーデータの取得に失敗しました。', {
      status: 400,
    });
  }
};

/**
 * 管理者用ユーザー更新関数
 */
async function updateUserAsAdmin(
  request: Request,
  userId: string,
  updateData: AdminUserUpdateData,
): Promise<void> {
  // SSR環境ではMSWが動作しないため、常に実際のバックエンドAPIを使用する
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/v1/auth/admin/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Cookie: request.headers.get('Cookie') || '',
    },
    credentials: 'include',
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'ユーザー更新に失敗しました');
  }
}

/**
 * 管理者用ユーザー削除関数
 */
async function deleteUserAsAdmin(
  request: Request,
  userId: string,
): Promise<void> {
  // SSR環境ではMSWが動作しないため、常に実際のバックエンドAPIを使用する
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/v1/auth/admin/users/${userId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Cookie: request.headers.get('Cookie') || '',
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'ユーザー削除に失敗しました');
  }
}

/**
 * 管理者用ユーザー復活関数
 */
async function restoreUserAsAdmin(
  request: Request,
  userId: string,
): Promise<void> {
  // SSR環境ではMSWが動作しないため、常に実際のバックエンドAPIを使用する
  const apiUrl = getApiUrl();
  const response = await fetch(
    `${apiUrl}/api/v1/auth/admin/users/${userId}/restore`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: request.headers.get('Cookie') || '',
      },
      credentials: 'include',
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'ユーザー復活に失敗しました');
  }
}

/**
 * アクション関数:
 * - クライアントからのアクションを処理
 * - ログアウト、プロフィール更新、アカウント削除、管理者用ユーザー管理等を処理
 */
export const action: ActionFunction = async ({ request }) => {
  try {
    const formData = await request.formData();
    const actionType = formData.get('_action');

    if (actionType === 'logout') {
      const response = await logoutAction(request);
      return response;
    }

    if (actionType === 'updateProfile') {
      const email = formData.get('email') as string;
      const username = formData.get('username') as string;

      // 入力値バリデーション
      if (!email || !username) {
        return new Response(
          JSON.stringify({
            error: 'メールアドレスとユーザー名を入力してください。',
            type: 'updateProfile',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }

      // メールアドレス形式チェック
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return new Response(
          JSON.stringify({
            error: '有効なメールアドレスを入力してください。',
            type: 'updateProfile',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }

      await updateUser(request, { email, username });
      return new Response(
        JSON.stringify({
          success: 'プロフィールを更新しました。',
          type: 'updateProfile',
        }),
        {
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    if (actionType === 'deleteAccount') {
      await deleteUser(request);
      return redirect('/login');
    }

    // 管理者用アクション
    if (actionType === 'updateUser') {
      const userId = formData.get('userId') as string;
      const username = formData.get('username') as string;
      const email = formData.get('email') as string;
      const user_role = formData.get('user_role') as string;
      const user_status = formData.get('user_status') as string;

      if (!userId) {
        return new Response(
          JSON.stringify({
            error: 'ユーザーIDが指定されていません。',
            type: 'updateUser',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }

      const updateData: AdminUserUpdateData = {};
      if (username) updateData.username = username;
      if (email) updateData.email = email;
      if (user_role) updateData.user_role = parseInt(user_role);
      if (user_status) updateData.user_status = parseInt(user_status);

      await updateUserAsAdmin(request, userId, updateData);
      return new Response(
        JSON.stringify({
          success: 'ユーザー情報を更新しました。',
          type: 'updateUser',
        }),
        {
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    if (actionType === 'deleteUser') {
      const userId = formData.get('userId') as string;

      if (!userId) {
        return new Response(
          JSON.stringify({
            error: 'ユーザーIDが指定されていません。',
            type: 'deleteUser',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }

      await deleteUserAsAdmin(request, userId);
      return new Response(
        JSON.stringify({
          success: 'ユーザーを削除しました。',
          type: 'deleteUser',
        }),
        {
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    if (actionType === 'restoreUser') {
      const userId = formData.get('userId') as string;

      if (!userId) {
        return new Response(
          JSON.stringify({
            error: 'ユーザーIDが指定されていません。',
            type: 'restoreUser',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }

      await restoreUserAsAdmin(request, userId);
      return new Response(
        JSON.stringify({
          success: 'ユーザーを復活させました。',
          type: 'restoreUser',
        }),
        {
          headers: { 'Content-Type': 'application/json' },
        },
      );
    }

    throw new Response('サーバー上で不具合が発生しました', {
      status: 400,
    });
  } catch (error) {
    console.error('MyPage action error:', error);
    return new Response(
      JSON.stringify({
        error:
          error instanceof Error && error.message
            ? error.message
            : 'サーバー上で予期しないエラーが発生しました',
        type: 'general',
      }),
      {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  }
};

interface LoaderDataType {
  user: User;
  users?: AdminUserResponse[];
}

/**
 * マイページコンポーネント:
 * - ユーザー情報を表示・編集するページ
 * - ユーザーロールに応じて管理者用・一般ユーザー用のページを表示
 */
export default function MyPage() {
  const loaderData = useLoaderData<LoaderDataType>();
  const actionData = useActionData<{
    error?: string;
    success?: string;
    type?: string;
  }>();

  // ローダーデータからユーザー情報を取得
  const { user, users } = loaderData;

  // 管理者権限のチェック（ROLE_ADMIN = 4以上）
  const isAdmin = user.user_role >= 4;

  return (
    <Layout>
      <Main>
        {isAdmin ? (
          <AdminMyPage user={user} users={users} actionData={actionData} />
        ) : (
          <RegularMyPage user={user} actionData={actionData} />
        )}
      </Main>
    </Layout>
  );
}
