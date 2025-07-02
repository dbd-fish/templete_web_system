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
      usePolling: true,
    },
    // NOTE:HTTPSサーバーを起動するための設定
    proxy: {}, // NOTE: プロキシを使用しないがTypeError: Headers.append: ":method" is an invalid header name 対策に必要
    https: {
      key: './certs/key.pem',
      cert: './certs/cert.pem',
    },
  },
});
