/**
 * プロフィールカードコンポーネント
 * ユーザー情報の表示と編集機能を提供
 * プロフィール画像、ユーザー名、メールアドレスの管理
 */
import { LoaderDataType } from '~/utils/types';
import { useLoaderData, useActionData, Form } from 'react-router';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Badge } from '~/components/ui/badge';
import { User, Mail, Edit3, Camera, Shield } from 'lucide-react';

export default function ProfileCard() {
  const loaderData = useLoaderData<LoaderDataType>();
  const actionData = useActionData<{
    error?: string;
    success?: string;
    type?: string;
  }>();
  const user = loaderData.user;

  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState(user?.email || '');
  const [username, setUsername] = useState(user?.username || '');
  const [emailError, setEmailError] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);

    if (newEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
      setEmailError('有効なメールアドレスを入力してください');
    } else {
      setEmailError('');
    }
  };

  // プロフィール更新成功時は編集モードを終了
  if (actionData?.type === 'updateProfile' && actionData.success && isEditing) {
    setIsEditing(false);
  }

  return (
    <Card className="w-full">
      <CardHeader className="text-center">
        <div className="relative mx-auto mb-4">
          <div className="w-24 h-24 bg-gradient-to-br from-primary/20 to-primary/40 rounded-full flex items-center justify-center mx-auto">
            <User className="w-12 h-12 text-primary" />
          </div>
          <button className="absolute bottom-0 right-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center hover:bg-primary/90 transition-colors">
            <Camera className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-center gap-2 mb-2">
          <CardTitle className="text-xl">
            {user?.username || 'ユーザー名'}
          </CardTitle>
          <Badge variant="secondary" className="text-xs">
            <Shield className="w-3 h-3 mr-1" />
            認証済み
          </Badge>
        </div>

        <div className="flex items-center justify-center text-muted-foreground">
          <Mail className="w-4 h-4 mr-2" />
          <span className="text-sm">{user?.email}</span>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* プロフィール更新エラー・成功メッセージ */}
        {actionData?.type === 'updateProfile' && actionData.error && (
          <div className="text-sm text-destructive border border-destructive/50 bg-destructive/10 p-3 rounded-md">
            {actionData.error}
          </div>
        )}
        {actionData?.type === 'updateProfile' && actionData.success && (
          <div className="text-sm text-green-700 border border-green-200 bg-green-50 p-3 rounded-md">
            {actionData.success}
          </div>
        )}

        {!isEditing ? (
          /* 表示モード */
          <div className="space-y-4">
            <div className="p-4 border rounded-lg space-y-2">
              <h4 className="font-medium text-sm text-muted-foreground">
                基本情報
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">ユーザー名:</span>
                  <span className="font-medium">{user?.username}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">メールアドレス:</span>
                  <span className="font-medium">{user?.email}</span>
                </div>
              </div>
            </div>

            <Button
              onClick={() => setIsEditing(true)}
              className="w-full"
              variant="outline"
            >
              <Edit3 className="w-4 h-4 mr-2" />
              プロフィール編集
            </Button>
          </div>
        ) : (
          /* 編集モード */
          <Form method="post" className="space-y-4">
            <input type="hidden" name="_action" value="updateProfile" />

            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium mb-1"
              >
                ユーザー名
              </label>
              <Input
                type="text"
                id="username"
                name="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ユーザー名を入力"
                required
                minLength={2}
                maxLength={50}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                メールアドレス
              </label>
              <Input
                type="email"
                id="email"
                name="email"
                value={email}
                onChange={handleEmailChange}
                placeholder="example@example.com"
                required
              />
              {emailError && (
                <div className="mt-1 text-xs text-destructive">
                  {emailError}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                type="submit"
                className="flex-1"
                disabled={!!emailError || !email || !username}
              >
                保存
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEmail(user?.email || '');
                  setUsername(user?.username || '');
                  setEmailError('');
                }}
                className="flex-1"
              >
                キャンセル
              </Button>
            </div>
          </Form>
        )}

        {/* Google認証統合UI対応（将来拡張用） */}
        <div className="pt-4 border-t">
          <h4 className="font-medium text-sm text-muted-foreground mb-3">
            アカウント連携
          </h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center">
                <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white text-xs font-bold">G</span>
                </div>
                <span className="text-sm">Google</span>
              </div>
              <Button variant="outline" size="sm" disabled>
                連携予定
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
