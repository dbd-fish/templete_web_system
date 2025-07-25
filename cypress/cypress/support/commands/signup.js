// サインアップ処理をコマンド化
Cypress.Commands.add('signup', (username = 'testuser', email = 'newuser@example.com', password = 'Password123456+-') => {
  cy.visit('/signup');

  // ページの読み込みを待つ
  cy.get('[data-cy="signup-form"]').should('be.visible');
  
  // ユーザー情報を入力
  cy.get('[data-cy="signup-username-input"]')
    .should('be.enabled')
    .clear()
    .type(username);

  cy.get('[data-cy="signup-email-input"]')
    .should('be.enabled')
    .clear()
    .type(email);

  cy.get('[data-cy="signup-password-input"]')
    .should('be.enabled')
    .clear()
    .type(password);

  cy.get('[data-cy="signup-confirm-password-input"]')
    .should('be.enabled')
    .clear()
    .type(password);

  // フォーム入力完了後、ボタンが有効化されるまで待機
  cy.wait(500);
  
  // サインアップボタンをクリック
  cy.get('[data-cy="signup-submit-button"]').should('be.enabled', { timeout: 5000 }).click();
  
  // サインアップ成功を待つ
  cy.url().should('not.include', '/signup', { timeout: 10000 });
});

// パスワード検証エラーのテスト用コマンド
Cypress.Commands.add('testPasswordValidation', (password, confirmPassword = null) => {
  cy.visit('/signup');
  
  cy.get('[data-cy="signup-username-input"]').type('testuser');
  cy.get('[data-cy="signup-email-input"]').type('test@example.com');
  cy.get('[data-cy="signup-password-input"]').type(password);
  
  if (confirmPassword !== null) {
    cy.get('[data-cy="signup-confirm-password-input"]').type(confirmPassword);
  }
});