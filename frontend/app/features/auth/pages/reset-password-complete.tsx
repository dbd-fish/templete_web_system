import { Link } from 'react-router';
import { CheckCircle, Lock } from 'lucide-react';
import Layout from '~/components/layout/Layout';
import Main from '~/components/layout/Main';
import SimpleCard from '~/components/common/SimpleCard';
import { Button } from '~/components/ui/button';

export default function ResetPasswordCompletePage() {
  return (
    <Layout>
      <Main>
        <SimpleCard>
          <div className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <h1 className="text-xl font-semibold mb-4">
              パスワードリセットが完了しました
            </h1>
          </div>

          <div className="text-center mb-6 space-y-3">
            <div className="flex items-center justify-center mb-4">
              <Lock className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">
              新しいパスワードでのログインが可能になりました。
            </p>
            <p className="text-sm font-medium">
              セキュリティ向上のため、すぐにログインをお試しください。
            </p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-6">
            <div className="text-xs text-green-800">
              <p className="font-medium mb-1">セキュリティのお知らせ</p>
              <ul className="space-y-1">
                <li>• 新しいパスワードは安全に設定されました</li>
                <li>• 今後はこのパスワードでログインしてください</li>
                <li>• パスワードは定期的に変更することをお勧めします</li>
              </ul>
            </div>
          </div>

          <div className="text-center">
            <Button asChild className="w-full">
              <Link to="/login">ログインページへ</Link>
            </Button>
          </div>
        </SimpleCard>
      </Main>
    </Layout>
  );
}
