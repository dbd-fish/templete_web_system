// react-router.config.ts
import type { Config } from '@react-router/dev/config';
import tsconfigPaths from 'vite-tsconfig-paths';

export default {
  ssr: true,
  vite: {
    plugins: [tsconfigPaths()],
  },
} satisfies Config;
