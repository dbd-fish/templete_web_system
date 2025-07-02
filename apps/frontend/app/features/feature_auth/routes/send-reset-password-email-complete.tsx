import { Link } from 'react-router';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

export default function SendResetPasswordEmailComplete() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">
            パスワードリセット用メールを送信しました！
          </h1>
          <p className="text-center mb-6">
            ご入力いただいたメールアドレス宛にパスワード再設定用のURLを送信しました。
            メールをご確認のうえ、本登録を完了してください。
          </p>
          <div className="text-center">
            <Link
              to="/login"
              className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md"
            >
              ログインページへ
            </Link>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
