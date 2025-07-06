import { type RouteConfig, route, index } from '@react-router/dev/routes';

export default [
  // ルートパスに対応するコンポーネント
  index('./features/feature_auth/routes/home.tsx'), // NOTE: 同一のtsxファイルを異なるルーティングに指定できないため、home.tsxはここのみで使用

  // その他のルート
  route('login', './features/feature_auth/routes/login.tsx'),
  route('mypage', './features/feature_auth/routes/mypage.tsx'),

  // 会員登録
  route('signup', './features/feature_auth/routes/signup.tsx'),
  route(
    'send-signup-email',
    './features/feature_auth/routes/send-signup-email.tsx',
  ),
  route(
    'signup-vertify-complete',
    './features/feature_auth/routes/signup-vertify-complete.tsx',
  ),

  // パスワードリセット
  route(
    'send-reset-password-email',
    './features/feature_auth/routes/send-reset-password-email.tsx',
  ),
  route(
    'send-reset-password-email-complete',
    './features/feature_auth/routes/send-reset-password-email-complete.tsx',
  ),
  route('reset-password', './features/feature_auth/routes/reset-password.tsx'),
  route(
    'reset-password-complete',
    './features/feature_auth/routes/reset-password-complete.tsx',
  ),

  // フッター情報
  route('privacy-policy', './commons/routes/privacyPolicy.tsx'), // プライバシーポリシー
  route('terms-of-service', './commons/routes/termsOfService.tsx'), // 利用規約
  route('e-commerce-law', './commons/routes/eCommerceLaw.tsx'), // 特定商取引法に基づく表記
  route('about-us', './commons/routes/aboutUs.tsx'), // 運営者情報
  route('contact', './commons/routes/contact.tsx'), // お問い合わせ
] satisfies RouteConfig;
