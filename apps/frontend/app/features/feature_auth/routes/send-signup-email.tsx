import { Link } from 'react-router';
import Layout from '~/commons/components/Layout';
import Main from '~/commons/components/Main';
import SimpleCard from '~/commons/components/SimpleCard';

export default function SendSignUpEmail() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-center mb-6">
            仮登録が完了しました。
          </h1>
          <p className=" text-center mb-4">
            ご登録ありがとうございます。仮登録が完了しました。
          </p>
          <p className=" text-center mb-6">
            ご入力いただいたメールアドレス宛に本登録用のURLを送信しました。
            メールをご確認のうえ、本登録を完了してください。
          </p>
          <div className="text-center">
            <Link
              to="/login"
              className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
            >
              ログインページへ
            </Link>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
