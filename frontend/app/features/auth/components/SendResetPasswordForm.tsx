/**
 * パスワードリセット申請フォームコンポーネント
 * メールアドレス入力によるリセット用トークン送信
 * メールアドレスバリデーションとエラーハンドリング機能
 */
import { Form } from 'react-router';
import { useState } from 'react';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';

export default function SendResetPasswordForm() {
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);

    // メールアドレス形式チェック
    if (newEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
      setEmailError('有効なメールアドレスを入力してください');
    } else {
      setEmailError('');
    }
  };

  return (
    <Form method="post" className="space-y-4">
      {/* メールアドレス入力フィールド */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          登録メールアドレス
        </label>
        <Input
          type="email"
          id="email"
          name="email"
          placeholder="example@example.com"
          value={email}
          onChange={handleEmailChange}
          required
        />
        {emailError && (
          <div className="mt-1 text-xs text-destructive">{emailError}</div>
        )}
        <div className="mt-1 text-xs text-muted-foreground">
          ご登録のメールアドレスにパスワードリセット用のURLを送信します
        </div>
      </div>

      {/* メール送信ボタン */}
      <div className="pt-2">
        <Button
          type="submit"
          className="w-full"
          disabled={!!emailError || !email}
        >
          リセット用メールを送信
        </Button>
      </div>
    </Form>
  );
}
