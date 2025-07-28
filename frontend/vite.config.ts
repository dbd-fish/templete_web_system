import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import fs from 'fs';
import path from 'path';

// HTTPS設定を判定する関数
const getHttpsConfig = () => {
  // 本番ビルド時はHTTPS設定を無効化
  if (process.env.NODE_ENV === 'production') {
    return false;
  }
  
  // DISABLE_HTTPSが設定されている場合は無効化
  if (process.env.DISABLE_HTTPS === 'true') {
    return false;
  }
  
  // 証明書ファイルの存在確認
  const keyPath = path.join(__dirname, 'certs', 'key.pem');
  const certPath = path.join(__dirname, 'certs', 'cert.pem');
  
  if (!fs.existsSync(keyPath) || !fs.existsSync(certPath)) {
    console.warn('HTTPS certificates not found. Running in HTTP mode.');
    return false;
  }
  
  // 証明書が存在する場合のみHTTPS設定を返す
  return {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath),
  };
};

export default defineConfig({
  plugins: [reactRouter(), tsconfigPaths()],  //NOTE: react-router7ではこれを追加しないとTailWindが機能しない
  css: {
    postcss: {
      plugins: [tailwindcss, autoprefixer],
    },
  },
  server: {
    watch: {
      usePolling: process.env.CHOKIDAR_USEPOLLING === 'true',
      interval: 1000,  // ポーリング間隔（ミリ秒）
      ignored: ['**/node_modules/**', '**/.git/**'],  // 監視対象から除外
    },
    host: '0.0.0.0',  // すべてのIPアドレスからのアクセスを許可（Dockerコンテナ間通信対応）
    port: 5173,
    strictPort: true,  // ポートが使用中の場合エラーで停止
    hmr: {
      overlay: true,  // エラーオーバーレイを表示
    },
    // NOTE:HTTPSサーバーを起動するための設定
    proxy: {}, // NOTE: プロキシを使用しないがTypeError: Headers.append: ":method" is an invalid header name 対策に必要
    cors: {
      origin: true,  // すべてのオリジンからのアクセスを許可
      credentials: false,
    },
    // HTTPS設定（開発環境のみ、証明書が存在する場合のみ有効）
    https: getHttpsConfig(),
  },
});
