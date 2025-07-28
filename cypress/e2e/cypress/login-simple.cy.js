/**
 * シンプルなログインテスト
 * 基本的な接続確認とログイン機能のテスト
 */
describe('シンプルログインテスト', () => {
  it('フロントエンドに接続できる', () => {
    cy.visit('/', { timeout: 30000 });
    cy.get('body').should('exist');
  });

  it('ログインページが表示される', () => {
    cy.visit('/login', { timeout: 30000 });
    cy.get('[data-cy="login-title"]', { timeout: 10000 }).should('be.visible').and('contain', 'ログイン');
  });

  it('ログインフォームが存在する', () => {
    cy.visit('/login', { timeout: 30000 });
    cy.get('[data-cy="email-input"]', { timeout: 10000 }).should('be.visible');
    cy.get('[data-cy="password-input"]', { timeout: 10000 }).should('be.visible');
    cy.get('[data-cy="login-submit-button"]', { timeout: 10000 }).should('be.visible');
  });

  it('正しい認証情報でログインできる', () => {
    cy.visit('/login', { timeout: 30000 });
    
    // フォーム要素の読み込みを待機
    cy.get('[data-cy="login-title"]', { timeout: 10000 }).should('be.visible');
    
    // 正しいテストユーザーの認証情報を使用
    cy.get('[data-cy="email-input"]')
      .should('be.enabled')
      .clear()
      .type('testuser@example.com');

    cy.get('[data-cy="password-input"]')
      .should('be.enabled')
      .clear()
      .type('Password123456+-');

    // ログインボタンをクリック
    cy.get('[data-cy="login-submit-button"]').click();
    
    // リクエスト完了を待つ
    cy.wait(3000);
    
    // ログイン処理完了を待つ（より長いタイムアウト）
    cy.url({ timeout: 15000 }).should('not.include', '/login');
    
    // マイページが表示されることを確認
    cy.url({ timeout: 5000 }).should('include', '/mypage');
    
    // マイページのコンテンツが表示される
    cy.get('body').should('contain', 'マイページ');
  });
});