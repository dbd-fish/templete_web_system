/**
 * パスワードリセットフォームコンポーネント
 * 新しいパスワードの設定とバリデーション機能
 * トークン認証によるセキュアなパスワード変更処理
 */
import { Form } from 'react-router';
import { useState } from 'react';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';
import {
  isPasswordValid,
  getAllowedSymbols,
} from '~/features/auth/passwordValidation';

export default function ResetPasswordForm() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    setNewPassword(password);

    if (password && !isPasswordValid(password)) {
      const allowedSymbols = getAllowedSymbols();
      setPasswordError(
        `パスワードが条件を満たしていません:\n・8文字以上\n・大文字・小文字\n・数字\n・記号(${allowedSymbols})を含む`,
      );
    } else {
      setPasswordError('');
    }

    // 確認パスワードのチェック
    if (confirmPassword && password !== confirmPassword) {
      setConfirmPasswordError('パスワードが一致しません');
    } else {
      setConfirmPasswordError('');
    }
  };

  const handleConfirmPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const password = e.target.value;
    setConfirmPassword(password);

    if (password && newPassword !== password) {
      setConfirmPasswordError('パスワードが一致しません');
    } else {
      setConfirmPasswordError('');
    }
  };

  return (
    <Form method="post" className="space-y-4" data-cy="new-password-form">
      {/* 新しいパスワード入力フィールド */}
      <div>
        <label htmlFor="newPassword" className="block text-sm font-medium mb-1">
          新しいパスワード
        </label>
        <Input
          type="password"
          id="newPassword"
          name="newPassword"
          placeholder="8文字以上、大文字・小文字・数字・記号を含む"
          value={newPassword}
          onChange={handlePasswordChange}
          data-cy="new-password-input"
          required
          minLength={8}
        />
        {passwordError && (
          <div className="mt-1 text-xs text-destructive whitespace-pre-line" data-cy="new-password-error">
            {passwordError}
          </div>
        )}
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
          placeholder="新しいパスワードを再入力"
          value={confirmPassword}
          onChange={handleConfirmPasswordChange}
          data-cy="confirm-new-password-input"
          required
          minLength={8}
        />
        {confirmPasswordError && (
          <div className="mt-1 text-xs text-destructive" data-cy="confirm-new-password-error">
            {confirmPasswordError}
          </div>
        )}
      </div>

      {/* パスワードリセットボタン */}
      <div className="pt-2">
        <Button
          type="submit"
          className="w-full"
          disabled={
            !!passwordError ||
            !!confirmPasswordError ||
            !newPassword ||
            !confirmPassword
          }
          data-cy="new-password-submit-button"
        >
          パスワードをリセット
        </Button>
      </div>
    </Form>
  );
}
