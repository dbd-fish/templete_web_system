import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';

export default function ResetPasswordForm() {
  return (
    <Form method="post" className="space-y-4">
      {/* 新しいパスワード入力フィールド */}
      <div>
        <label htmlFor="newPassword" className="block text-sm font-medium mb-1">
          新しいパスワード
        </label>
        <Input
          type="password"
          id="newPassword"
          name="newPassword"
          placeholder="********"
          required
          className="bg-gray-100 focus:bg-white"
        />
      </div>

      {/* 新しいパスワード確認用フィールド */}
      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium mb-1"
        >
          新しいパスワード（確認用）
        </label>
        <Input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          placeholder="********"
          required
          className="bg-gray-100 focus:bg-white"
        />
      </div>

      {/* パスワードリセットボタン */}
      <div>
        <Button type="submit" className="w-full">
          パスワードをリセット
        </Button>
      </div>
    </Form>
  );
}
