import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';

/**
 * LoginForm コンポーネント
 */
export default function LoginForm() {
  return (
    <Form id="login-form" method="post" className="space-y-4">
      {/* メールアドレス入力フィールド */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          メールアドレス
        </label>
        <Input
          type="email"
          id="email"
          name="email"
          placeholder="example@example.com"
          required
        />
      </div>

      {/* パスワード入力フィールド */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          パスワード
        </label>
        <Input
          type="password"
          id="password"
          name="password"
          placeholder="********"
          minLength={8}
          required
        />
      </div>

      {/* ログインボタン */}
      <div>
        <Button type="submit" className="w-full">
          ログイン
        </Button>
      </div>
    </Form>
  );
}
