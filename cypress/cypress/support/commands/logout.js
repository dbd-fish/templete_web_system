// ログアウト処理をコマンド化
Cypress.Commands.add('logout', () => {
    // ユーザーメニューボタンをクリックしてメニューを表示
    cy.get('[data-cy="user-menu-button"]').should('be.visible').click();

    // ログアウトボタンをクリック
    cy.get('[data-cy="logout-button"]').should('be.visible').click();
    
    // ログアウト成功を待つ（ログインページにリダイレクトされる）
    cy.url().should('include', '/login', { timeout: 10000 });
});
