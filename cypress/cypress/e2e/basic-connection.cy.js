/**
 * 基本的な接続テスト
 * フロントエンドとバックエンドの基本的な動作を確認
 */
describe('基本接続テスト', () => {
  it('フロントエンドページが表示される', () => {
    cy.visit('/', { 
      failOnStatusCode: false,
      timeout: 30000
    });
    
    cy.get('body').should('exist');
    
    // ホームページのタイトルまたは要素が表示される
    cy.contains('Webシステム開発テンプレート', { timeout: 10000 }).should('be.visible');
  });

  it('ログインページに移動できる', () => {
    cy.visit('/login', { 
      failOnStatusCode: false,
      timeout: 30000
    });
    
    // ログインページの要素が表示される
    cy.get('[data-cy="login-title"]', { timeout: 10000 }).should('be.visible').and('contain', 'ログイン');
    cy.get('[data-cy="login-form"]').should('be.visible');
    cy.get('[data-cy="email-input"]').should('be.visible');
    cy.get('[data-cy="password-input"]').should('be.visible');
    cy.get('[data-cy="login-submit-button"]').should('be.visible');
  });

  it('フォーム要素が正しく動作する', () => {
    cy.visit('/login');
    
    // フォーム入力のテスト
    cy.get('[data-cy="email-input"]')
      .should('be.enabled')
      .type('test@example.com')
      .should('have.value', 'test@example.com');

    cy.get('[data-cy="password-input"]')
      .should('be.enabled')
      .type('testpassword')
      .should('have.value', 'testpassword');
      
    cy.get('[data-cy="login-submit-button"]').should('be.enabled');
  });

  it('バックエンドAPIに直接アクセスできる（Cypress内から）', () => {
    // Cypressコンテナからバックエンドへの接続テスト
    cy.request({
      method: 'GET',
      url: 'http://backend:8000/docs',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.be.oneOf([200, 404]); // Swagger UIまたは404
    });
  });
});