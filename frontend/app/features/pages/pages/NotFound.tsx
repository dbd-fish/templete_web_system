import { Link } from 'react-router';
import Layout from '~/components/layout/Layout';
import { Button } from '~/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/Card';

export default function NotFound() {
  return (
    <Layout>
      <main className="flex-grow flex items-center justify-center py-8 px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-destructive">404</span>
            </div>
            <CardTitle className="text-2xl font-bold text-foreground">
              ページが見つかりません
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-muted-foreground">
              お探しのページは存在しないか、移動した可能性があります。
            </p>
            <div className="flex flex-col sm:flex-row gap-2 justify-center">
              <Button asChild>
                <Link to="/">ホームに戻る</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/login">ログインページ</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </Layout>
  );
}
