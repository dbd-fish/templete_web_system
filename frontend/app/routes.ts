import { type RouteConfig, route, index } from '@react-router/dev/routes';

export default [
  // ルートパスに対応するコンポーネント
  index('./features/auth/pages/home.tsx'), // NOTE: 同一のtsxファイルを異なるルーティングに指定できないため、home.tsxはここのみで使用

  // その他のルート
  route('login', './features/auth/pages/login.tsx'),
  route('mypage', './features/auth/pages/mypage.tsx'),

  // 会員登録
  route('signup', './features/auth/pages/signup.tsx'),
  route('send-signup-email', './features/auth/pages/send-signup-email.tsx'),
  route(
    'signup-vertify-complete',
    './features/auth/pages/signup-vertify-complete.tsx',
  ),

  // パスワードリセット
  route(
    'send-reset-password-email',
    './features/auth/pages/send-reset-password-email.tsx',
  ),
  route(
    'send-reset-password-email-complete',
    './features/auth/pages/send-reset-password-email-complete.tsx',
  ),
  route('reset-password', './features/auth/pages/reset-password.tsx'),
  route(
    'reset-password-complete',
    './features/auth/pages/reset-password-complete.tsx',
  ),

  // 静的ページ情報
  route('privacy-policy', './features/pages/pages/privacyPolicy.tsx'), // プライバシーポリシー
  route('terms-of-service', './features/pages/pages/termsOfService.tsx'), // 利用規約
  route('e-commerce-law', './features/pages/pages/eCommerceLaw.tsx'), // 特定商取引法に基づく表記
  route('about-us', './features/pages/pages/aboutUs.tsx'), // 運営者情報
  route('contact', './features/pages/pages/contact.tsx'), // お問い合わせ

  // 404 NotFoundページ（開発ツールやその他のマッチしないパスをキャッチ）
  route('*', './features/pages/pages/NotFound.tsx'),
] satisfies RouteConfig;
