import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  isRouteErrorResponse,
  useRouteError,
} from 'react-router';
import type { LinksFunction } from 'react-router';

import './tailwind.css';
import Header from '~/commons/components/header/LoggedOutHeader';
import Footer from './commons/components/Footer';

// NOTE:暫定的にここにエラー画面を記載
export function ErrorBoundary() {
  const error = useRouteError();

  console.error(error);

  let errorMessage = '予期しないエラーが発生しました。';
  // NOTE: isRouteErrorResponseを使用してエラーレスポンスを確認
  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      errorMessage =
        'お探しのページが見つかりませんでした。URLをご確認ください。';
    } else {
      errorMessage = error.data || 'サーバーエラーが発生しました。';
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* NOTE: Header内で認証情報をuseLoaderDataで確認するが、
      ErrorBoundary経由ではLoaderからのデータがないため、
      一律でLoggedOutHeaderが表示される */}
      <Header />
      <main className="flex-grow bg-gray-100 flex items-center justify-center">
        <div className="w-full max-w-4xl bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            エラーが発生しました
          </h2>
          <p className="text-gray-600">{errorMessage}</p>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export const links: LinksFunction = () => [
  { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
  {
    rel: 'preconnect',
    href: 'https://fonts.gstatic.com',
    crossOrigin: 'anonymous',
  },
  {
    rel: 'stylesheet',
    href: 'https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap',
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
