// ログアウト処理をコマンド化
Cypress.Commands.add('logout', () => {
    // ユーザーメニューボタンをクリックしてメニューを表示
    cy.get('[data-cy="user-menu-button"]').should('be.visible').click();

    // ログアウトボタンをクリック
    cy.get('[data-cy="logout-button"]').should('be.visible').click();
    
    // ログアウト成功を待つ（ログインページにリダイレクトされる）
    cy.url().should('include', '/login', { timeout: 10000 });
    
    // 認証Cookieが削除されていることを確認
    cy.getCookie('authToken').should('be.null');
    cy.getCookie('refreshToken').should('be.null');
});

// Cookie確認専用のログアウトコマンド（テスト用）
Cypress.Commands.add('logoutAndVerifyCookies', () => {
    // ログアウト前のCookie確認
    cy.getCookie('authToken').should('exist');
    cy.getCookie('refreshToken').should('exist');
    
    // ログアウト実行
    cy.logout();
    
    // ログアウト後のCookie削除確認
    cy.getCookie('authToken').should('be.null');
    cy.getCookie('refreshToken').should('be.null');
});
