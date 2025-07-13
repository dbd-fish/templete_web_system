import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';

export default function SignupForm() {
  return (
    <Form id="signup-form" method="post" action="/signup" className="space-y-6">
      {/* ユーザー名入力フィールド */}
      <div>
        <label htmlFor="username" className="block text-sm font-medium">
          ユーザー名
        </label>
        <Input
          type="text"
          id="username"
          name="username"
          required
          className="mt-1"
        />
      </div>

      {/* メールアドレス入力フィールド */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          メールアドレス
        </label>
        <Input type="email" id="email" name="email" required className="mt-1" />
      </div>

      {/* パスワード入力フィールド */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          パスワード
        </label>
        <Input
          type="password"
          id="password"
          name="password"
          required
          className="mt-1"
        />
      </div>

      {/* パスワード確認用フィールド */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium">
          パスワード（確認用）
        </label>
        <Input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          required
          className="mt-1"
        />
      </div>

      {/* 会員登録ボタン */}
      <div>
        <Button type="submit" variant="default" className="w-full">
          会員登録
        </Button>
      </div>
    </Form>
  );
}
