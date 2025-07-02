// NOTE: ログイン処理をコマンド化
// Cypress.Commands.add('login', (email, password) => {
//   cy.visit('/login');

//   // NOTE: これがないと以降の操作ができない
//   // ページの読み込みを待つ
//   cy.wait(1000); // または適切な時間

//   // NOTE: ここで正しいemailとパスワードの組み合わせは別コンテナを参照する必要がある
//   cy.get('input#email')
//     .should('be.enabled') // 要素が有効になるまで待機
//     .type(email);

//   cy.get('input#password')
//     .should('be.enabled')
//     .type(password);

//   cy.get('button[type="submit"]').click();
// });
