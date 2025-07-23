// ログイン処理をコマンド化
Cypress.Commands.add('login', (email = 'test@example.com', password = 'TestPass123!') => {
  cy.visit('/login');

  // ページの読み込みを待つ
  cy.get('[data-cy="login-title"]').should('be.visible');
  
  // メールとパスワードを入力
  cy.get('[data-cy="email-input"]')
    .should('be.enabled')
    .clear()
    .type(email);

  cy.get('[data-cy="password-input"]')
    .should('be.enabled')
    .clear()
    .type(password);

  // ログインボタンをクリック
  cy.get('[data-cy="login-submit-button"]').click();
  
  // ログイン成功を待つ
  cy.url().should('not.include', '/login', { timeout: 10000 });
});

// Googleログインのモックコマンド
Cypress.Commands.add('loginWithGoogle', () => {
  cy.visit('/login');
  
  // Googleログインボタンが表示されるまで待つ
  cy.get('[data-cy="google-login-button"]').should('be.visible');
  
  // Google認証のモック処理
  cy.window().then((win) => {
    // Google認証サービスをモック
    win.google = {
      accounts: {
        id: {
          initialize: cy.stub(),
          prompt: cy.stub(),
          renderButton: cy.stub()
        }
      }
    };
  });
  
  // Googleログインボタンをクリック
  cy.get('[data-cy="google-login-button"]').click();
});

// 管理者としてログインするコマンド
Cypress.Commands.add('loginAsAdmin', () => {
  cy.login('admin@example.com', 'AdminPass123!');
});

// 一般ユーザーとしてログインするコマンド
Cypress.Commands.add('loginAsUser', () => {
  cy.login('user@example.com', 'UserPass123!');
});
