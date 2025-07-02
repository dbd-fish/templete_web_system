const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://frontend:5173', // テスト対象のURL
    specPattern: [
       'e2e/cypress/**/*.cy.js', //ローカル環境におけるE2Eテスト
      'front_st/**/*.cy.js',  //画面単位のテスト
    ], 
    // NOTE: supportFileでエラーのスキップや汎用操作のコマンド化を取り込む
    supportFile: 'cypress/support/index.js', 
  },
});
