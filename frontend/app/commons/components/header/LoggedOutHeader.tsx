import { Button } from '~/components/ui/button';
import SiteTitle from '~/commons/components/SiteTitle';

export default function Header() {
  return (
    <header className="bg-gray-600 text-gray-100 py-3 shadow-md">
      <div className="container mx-auto px-4 flex justify-between items-center">
        {/* サイトタイトル */}
        <SiteTitle />

        {/* レスポンシブなナビゲーション */}
        <nav className="flex items-center space-x-2 sm:space-x-4">
          {/* ログインボタン */}
          <Button
            variant="default"
            asChild
            className="text-xs sm:text-sm bg-gray-800 px-3 py-2"
          >
            <a href="/login">ログイン</a>
          </Button>

          {/* 会員登録ボタン */}
          <Button
            variant="default"
            asChild
            className="text-xs sm:text-sm border border-gray-600 px-3 py-2"
          >
            <a href="/signup">会員登録</a>
          </Button>
        </nav>
      </div>
    </header>
  );
}
