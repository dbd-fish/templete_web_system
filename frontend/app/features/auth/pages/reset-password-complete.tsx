import { Link } from 'react-router';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';

import SimpleCard from '~/components/common/SimpleCard';

export default function ResetPasswordCompletePage() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">
            パスワードリセットが完了しました！
          </h1>
          <p className="text-gray-600 text-center mb-6">
            新しいパスワードでログインできるかご確認ください。
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
