// 基本のレイアウト
import Header from '~/components/layout/Header';
import Footer from '~/components/layout/Footer';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Header />
      {children}
      <Footer />
    </div>
  );
}
