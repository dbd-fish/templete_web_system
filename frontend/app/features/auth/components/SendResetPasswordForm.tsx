import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';

export default function SendResetPasswordForm() {
  return (
    <Form method="post" className="space-y-6">
      {/* メールアドレス入力フィールド */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          登録メールアドレス
        </label>
        <Input type="email" id="email" name="email" required className="mt-1" />
      </div>

      {/* メール送信ボタン */}
      <div>
        <Button type="submit" variant="default" className="w-full">
          メールを送信
        </Button>
      </div>
    </Form>
  );
}
