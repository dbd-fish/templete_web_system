// ログイン処理をコマンド化（画面操作版）
Cypress.Commands.add('login', (email = 'targetuser@example.com', password = 'Password123456+-') => {
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
  
  // リクエスト完了を待つ
  cy.wait(3000);
  
  // ログイン処理完了を待つ（より長いタイムアウト）
  cy.url().should('not.include', '/login', { timeout: 15000 });
  
  // マイページが表示されることを確認
  cy.url().should('include', '/mypage', { timeout: 5000 });
});

// フォーム経由のログインテスト用コマンド（UIテスト用）
Cypress.Commands.add('loginViaForm', (email = 'targetuser@example.com', password = 'Password123456+-') => {
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
  
  // リクエスト完了を待つ
  cy.wait(3000);
  
  // ログイン処理完了を待つ（より長いタイムアウト）
  cy.url().should('not.include', '/login', { timeout: 15000 });
  
  // マイページが表示されることを確認
  cy.url().should('include', '/mypage', { timeout: 5000 });
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

// 管理者としてログインするコマンド（画面操作版）
Cypress.Commands.add('loginAsAdmin', () => {
  cy.loginViaForm('admin@example.com', 'adminpassword');
});

// 一般ユーザーとしてログインするコマンド（画面操作版）
Cypress.Commands.add('loginAsUser', () => {
  cy.loginViaForm('targetuser@example.com', 'Password123456+-');
});
