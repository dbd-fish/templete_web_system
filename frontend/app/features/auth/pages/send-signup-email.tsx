import { Link } from 'react-router';
import { CheckCircle, Mail } from 'lucide-react';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';
import { Button } from '~/components/ui/button';

export default function SendSignUpEmail() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <div className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <h1 className="text-xl font-semibold mb-4">仮登録が完了しました</h1>
          </div>

          <div className="text-center mb-6 space-y-3">
            <div className="flex items-center justify-center mb-4">
              <Mail className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">
              ご登録ありがとうございます。仮登録が完了しました。
            </p>
            <p className="text-sm text-muted-foreground">
              ご入力いただいたメールアドレス宛に
              <br />
              本登録用のURLを送信しました。
            </p>
            <p className="text-sm font-medium">
              メールをご確認のうえ、本登録を完了してください。
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-center">
              <Button asChild className="w-full">
                <Link to="/login">ログインページへ</Link>
              </Button>
            </div>

            <div className="text-center">
              <p className="text-xs text-muted-foreground">
                メールが届かない場合は、迷惑メールフォルダもご確認ください
              </p>
            </div>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
