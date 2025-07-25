/**
 * ユーザー登録フォームコンポーネント
 * 新規ユーザー情報入力とバリデーション機能
 * パスワード強度チェックとリアルタイム確認表示
 */
import { Form } from 'react-router';
import { useState } from 'react';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';
import { isPasswordValid } from '~/features/auth/passwordValidation';

export default function SignupForm() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);

    if (newPassword && !isPasswordValid(newPassword)) {
      setPasswordError('パスワードが条件を満たしていません');
    } else {
      setPasswordError('');
    }

    // 確認パスワードのチェック
    if (confirmPassword && newPassword !== confirmPassword) {
      setConfirmPasswordError('パスワードが一致しません');
    } else {
      setConfirmPasswordError('');
    }
  };

  const handleConfirmPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const newConfirmPassword = e.target.value;
    setConfirmPassword(newConfirmPassword);

    if (newConfirmPassword && password !== newConfirmPassword) {
      setConfirmPasswordError('パスワードが一致しません');
    } else {
      setConfirmPasswordError('');
    }
  };

  return (
    <Form
      id="signup-form"
      method="post"
      action="/signup"
      className="space-y-4"
      data-cy="signup-form"
    >
      {/* ユーザー名入力フィールド */}
      <div>
        <label htmlFor="username" className="block text-sm font-medium mb-1">
          ユーザー名
        </label>
        <Input
          type="text"
          id="username"
          name="username"
          placeholder="ユーザー名を入力"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          data-cy="signup-username-input"
          required
          minLength={2}
          maxLength={50}
        />
      </div>

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
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          data-cy="signup-email-input"
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
          placeholder="8文字以上、大文字・小文字・数字・記号を含む"
          value={password}
          onChange={handlePasswordChange}
          data-cy="signup-password-input"
          required
          minLength={8}
        />
        {passwordError && (
          <div
            className="mt-1 text-xs text-destructive"
            data-cy="password-error"
          >
            {passwordError}
          </div>
        )}
      </div>

      {/* パスワード確認用フィールド */}
      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium mb-1"
        >
          パスワード（確認用）
        </label>
        <Input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          placeholder="パスワードを再入力"
          value={confirmPassword}
          onChange={handleConfirmPasswordChange}
          data-cy="signup-confirm-password-input"
          required
          minLength={8}
        />
        {confirmPasswordError && (
          <div
            className="mt-1 text-xs text-destructive"
            data-cy="confirm-password-error"
          >
            {confirmPasswordError}
          </div>
        )}
      </div>

      {/* 会員登録ボタン */}
      <div className="pt-2">
        <Button
          type="submit"
          className="w-full"
          disabled={
            !username.trim() ||
            !email.trim() ||
            !password ||
            !confirmPassword ||
            !!passwordError ||
            !!confirmPasswordError
          }
          data-cy="signup-submit-button"
        >
          会員登録
        </Button>
      </div>
    </Form>
  );
}
