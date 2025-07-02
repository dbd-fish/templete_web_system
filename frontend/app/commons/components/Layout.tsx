// 基本のレイアウト
import Header from '~/commons/components/Header';
import Footer from '~/commons/components/Footer';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Header />
      {children}
      <Footer />
    </div>
  );
}
