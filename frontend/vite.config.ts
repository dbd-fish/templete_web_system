import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';


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
    host: true,
    port: 5173,
    hmr: {
      overlay: true,  // エラーオーバーレイを表示
    },
    // NOTE:HTTPSサーバーを起動するための設定
    proxy: {}, // NOTE: プロキシを使用しないがTypeError: Headers.append: ":method" is an invalid header name 対策に必要
    https: {
      key: './certs/key.pem',
      cert: './certs/cert.pem',
    },
  },
});
