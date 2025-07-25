import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import fs from 'fs';
import path from 'path';


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
    // HTTPS設定（環境変数で制御）
    https: process.env.DISABLE_HTTPS === 'true' ? false : {
      key: fs.readFileSync(path.join(__dirname, 'certs', 'key.pem')),
      cert: fs.readFileSync(path.join(__dirname, 'certs', 'cert.pem')),
    },
  },
});
