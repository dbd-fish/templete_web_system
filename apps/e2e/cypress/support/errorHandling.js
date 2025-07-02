// NOTE: 原因不明なエラーで悩まされる場合はこのファイルでスキップするように定義する。
Cypress.on('uncaught:exception', (err) => {
  // NOTE: CypressとReact(Remixなど)の相性問題？
  // https://github.com/cypress-io/cypress/issues/27204#issuecomment-1927093633
  // NOTE: includesで指定した文字列がエラーメッセージに含まれている場合は無視する
  if (err.message.includes('The following error originated from your application code, not from Cypress.')) {
    return false; // テストの失敗を回避
  }
  return true; // 他のエラーは通常通り失敗として扱う


  console.log('Uncaught Exception:', err.message); // エラーメッセージをログに出力
  // return false; // NOTE: 一時的にすべてのエラーを無視
});
