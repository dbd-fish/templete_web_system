import { type RouteConfig, route, index } from '@react-router/dev/routes';

export default [
  // ルートパスに対応するコンポーネント
  index('./features/feature_auth/pages/home.tsx'), // NOTE: 同一のtsxファイルを異なるルーティングに指定できないため、home.tsxはここのみで使用

  // その他のルート
  route('login', './features/feature_auth/pages/login.tsx'),
  route('mypage', './features/feature_auth/pages/mypage.tsx'),

  // 会員登録
  route('signup', './features/feature_auth/pages/signup.tsx'),
  route(
    'send-signup-email',
    './features/feature_auth/pages/send-signup-email.tsx',
  ),
  route(
    'signup-vertify-complete',
    './features/feature_auth/pages/signup-vertify-complete.tsx',
  ),

  // パスワードリセット
  route(
    'send-reset-password-email',
    './features/feature_auth/pages/send-reset-password-email.tsx',
  ),
  route(
    'send-reset-password-email-complete',
    './features/feature_auth/pages/send-reset-password-email-complete.tsx',
  ),
  route('reset-password', './features/feature_auth/pages/reset-password.tsx'),
  route(
    'reset-password-complete',
    './features/feature_auth/pages/reset-password-complete.tsx',
  ),

  // 静的ページ情報
  route('privacy-policy', './features/feature_pages/routes/privacyPolicy.tsx'), // プライバシーポリシー
  route(
    'terms-of-service',
    './features/feature_pages/routes/termsOfService.tsx',
  ), // 利用規約
  route('e-commerce-law', './features/feature_pages/routes/eCommerceLaw.tsx'), // 特定商取引法に基づく表記
  route('about-us', './features/feature_pages/routes/aboutUs.tsx'), // 運営者情報
  route('contact', './features/feature_pages/routes/contact.tsx'), // お問い合わせ

  // 404 NotFoundページ（開発ツールやその他のマッチしないパスをキャッチ）
  route('*', './features/feature_pages/pages/NotFound.tsx'),
] satisfies RouteConfig;
