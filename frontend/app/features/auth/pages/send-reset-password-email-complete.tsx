import { Link } from 'react-router';
import { CheckCircle, Mail, Clock } from 'lucide-react';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';
import { Button } from '~/components/ui/button';

export default function SendResetPasswordEmailComplete() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <div className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <h1 className="text-xl font-semibold mb-4">
              リセット用メールを送信しました
            </h1>
          </div>

          <div className="text-center mb-6 space-y-3">
            <div className="flex items-center justify-center mb-4">
              <Mail className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">
              ご入力いただいたメールアドレス宛に
              <br />
              パスワード再設定用のURLを送信しました。
            </p>
            <p className="text-sm font-medium">
              メールをご確認のうえ、パスワードリセットを完了してください。
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-6">
            <div className="flex items-start space-x-2">
              <Clock className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-xs text-blue-800">
                <p className="font-medium mb-1">重要な注意事項</p>
                <ul className="space-y-1">
                  <li>• リセットリンクの有効期限は24時間です</li>
                  <li>
                    • メールが届かない場合は迷惑メールフォルダもご確認ください
                  </li>
                  <li>• リンクは一度のみ使用可能です</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-center">
              <Button asChild className="w-full">
                <Link to="/login">ログインページへ</Link>
              </Button>
            </div>

            <div className="text-center">
              <Button asChild variant="outline" className="w-full">
                <Link to="/send-reset-password-email">メールを再送信する</Link>
              </Button>
            </div>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
