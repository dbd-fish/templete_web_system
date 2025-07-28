/**
 * ログインフォームコンポーネント
 * メールアドレスとパスワードによるユーザー認証フォーム
 * エラーメッセージ表示とフォーム送信処理を含む
 */
import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';
export default function LoginForm() {
  return (
    <Form
      id="login-form"
      method="post"
      className="space-y-4"
      data-cy="login-form"
    >
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
          data-cy="email-input"
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
          data-cy="password-input"
          required
        />
      </div>

      {/* ログインボタン */}
      <div>
        <Button type="submit" className="w-full" data-cy="login-submit-button">
          ログイン
        </Button>
      </div>
    </Form>
  );
}
