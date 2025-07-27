const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://frontend:5173', // テスト対象のURL（HTTPS接続）
    specPattern: [
       'e2e/cypress/**/*.cy.js', //ローカル環境におけるE2Eテスト
       'cypress/e2e/auth/**/*.cy.js',    //認証関連E2Eテスト
      'front_st/**/*.cy.js',  //画面単位のテスト
    ], 
    // NOTE: supportFileでエラーのスキップや汎用操作のコマンド化を取り込む
    supportFile: 'cypress/support/index.js',
    // HTTPS証明書エラーを無視（コンテナ間通信の自己署名証明書対応）
    chromeWebSecurity: false,
    // Cookieとlocal storageを保持
    experimentalSessionAndOrigin: true,
    // Cookie設定
    blockHosts: [],
  },
});
