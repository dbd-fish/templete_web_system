/**
 * デバッグ用接続テスト
 * Cypressからフロントエンドへの接続をテスト
 */
describe('デバッグ - フロントエンド接続テスト', () => {
  it('フロントエンドに接続できることを確認', () => {
    // 最もシンプルな接続テスト
    cy.request({
      method: 'GET',
      url: 'http://frontend:5173',
      failOnStatusCode: false,
      timeout: 10000
    }).then((response) => {
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      expect(response.status).to.be.oneOf([200, 404]); // 200もしくは404であれば接続OK
    });
  });

  it('cy.visitでフロントエンドにアクセス', () => {
    cy.visit('/', {
      failOnStatusCode: false,
      timeout: 10000
    });
    // ページが読み込まれればOK（エラーページでも可）
    cy.get('html').should('exist');
  });
});