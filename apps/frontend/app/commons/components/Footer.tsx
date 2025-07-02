export default function Footer() {
  return (
    <footer className="bg-gray-600 text-gray-100 py-8">
      <div className="container mx-auto px-4 text-center">
        {/* コピーライト情報 */}
        <p className="text-sm mb-2 text-gray-100">
          &copy; 2024 My Website. All rights reserved.
        </p>
        <p className="text-xs mb-4 text-gray-100">
          このサイトは個人情報を適切に管理しています。
        </p>

        {/* ナビゲーションリンク */}
        <div className="flex flex-wrap justify-center gap-4 text-sm">
          <a
            href="/privacy-policy"
            className="text-gray-100 hover:text-white transition-colors"
          >
            プライバシーポリシー
          </a>
          <a
            href="/terms-of-service"
            className="text-gray-100 hover:text-white transition-colors"
          >
            利用規約
          </a>
          <a
            href="/e-commerce-law"
            className="text-gray-100 hover:text-white transition-colors"
          >
            特定商取引法に基づく表記
          </a>
          <a
            href="/about-us"
            className="text-gray-100 hover:text-white transition-colors"
          >
            運営者情報
          </a>
          <a
            href="/contact"
            className="text-gray-100 hover:text-white transition-colors"
          >
            お問い合わせ
          </a>
        </div>

        {/* サブコピー */}
        <p className="text-xs mt-4 text-gray-100">
          © 2024 My Website, Inc. またはその関連会社。
        </p>
      </div>
    </footer>
  );
}
