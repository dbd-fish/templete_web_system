/**
 * 認証機能のE2Eテスト
 * 
 * 操作パターン:
 * - ユーザー登録フローの確認
 * - ログイン・ログアウト機能の検証
 * - セッション管理とリダイレクト処理
 */
describe('認証機能テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('ログイン機能', () => {
    it('ログインページが正常に表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="login-title"]').should('be.visible').and('contain', 'ログイン');
      cy.get('[data-cy="login-form"]').should('be.visible');
      cy.get('[data-cy="email-input"]').should('be.visible');
      cy.get('[data-cy="password-input"]').should('be.visible');
      cy.get('[data-cy="login-submit-button"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('be.visible');
    });

    it('有効な認証情報でログインできる', () => {
      cy.login('test@example.com', 'TestPass123!');
      // ログイン成功後マイページにリダイレクト
      cy.url().should('include', '/mypage');
    });

    it('無効な認証情報でログインに失敗する', () => {
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('invalid@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // エラーメッセージが表示される
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
    });

    it('必須フィールドが空の場合バリデーションエラーが表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // HTML5バリデーションが働く
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
    });

    it('Googleログインボタンが表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="google-login-button"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('contain', 'Googleでログイン');
    });

    it('フォームリンクが正しく動作する', () => {
      cy.visit('/login');
      
      // パスワード忘れた場合のリンク
      cy.get('[data-cy="forgot-password-link"]').click();
      cy.url().should('include', '/send-reset-password-email');
      
      // 新規会員登録のリンク
      cy.visit('/login');
      cy.get('[data-cy="signup-link"]').click();
      cy.url().should('include', '/signup');
    });
  });

  describe('ログアウト機能', () => {
    beforeEach(() => {
      // テスト前にログイン
      cy.login();
    });

    it('ログアウトが正常に動作する', () => {
      // マイページにアクセス
      cy.visit('/mypage');
      
      // ログアウト実行
      cy.logout();
      
      // ログインページにリダイレクトされる
      cy.url().should('include', '/login');
    });

    it('ログアウト後は保護されたページにアクセスできない', () => {
      cy.visit('/mypage');
      cy.logout();
      
      // 保護されたページに再アクセスを試みる
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });
  });

  describe('サインアップ機能', () => {
    it('サインアップページが正常に表示される', () => {
      cy.visit('/signup');
      cy.get('[data-cy="signup-form"]').should('be.visible');
      cy.get('[data-cy="signup-username-input"]').should('be.visible');
      cy.get('[data-cy="signup-email-input"]').should('be.visible');
      cy.get('[data-cy="signup-password-input"]').should('be.visible');
      cy.get('[data-cy="signup-confirm-password-input"]').should('be.visible');
      cy.get('[data-cy="signup-submit-button"]').should('be.visible');
    });

    it('有効な情報でサインアップができる', () => {
      const timestamp = Date.now();
      cy.signup(`testuser${timestamp}`, `test${timestamp}@example.com`, 'ValidPass123!');
      
      // サインアップ成功後の適切なページに遷移
      cy.url().should('not.include', '/signup');
    });

    it('パスワードバリデーションが正常に動作する', () => {
      cy.visit('/signup');
      
      // 弱いパスワードを入力
      cy.get('[data-cy="signup-password-input"]').type('weak');
      cy.get('[data-cy="signup-confirm-password-input"]').click();
      
      // バリデーションエラーが表示される
      cy.contains('パスワードが条件を満たしていません').should('be.visible');
    });

    it('パスワード確認が一致しない場合エラーが表示される', () => {
      cy.visit('/signup');
      
      cy.get('[data-cy="signup-password-input"]').type('ValidPass123!');
      cy.get('[data-cy="signup-confirm-password-input"]').type('DifferentPass123!');
      
      // パスワード不一致エラーが表示される
      cy.contains('パスワードが一致しません').should('be.visible');
    });

    it('必須フィールドが空の場合サインアップボタンが無効になる', () => {
      cy.visit('/signup');
      
      // サインアップボタンが無効状態
      cy.get('[data-cy="signup-submit-button"]').should('be.disabled');
      
      // フィールドを埋めていくとボタンが有効になる
      cy.get('[data-cy="signup-username-input"]').type('testuser');
      cy.get('[data-cy="signup-email-input"]').type('test@example.com');
      cy.get('[data-cy="signup-password-input"]').type('ValidPass123!');
      cy.get('[data-cy="signup-confirm-password-input"]').type('ValidPass123!');
      
      cy.get('[data-cy="signup-submit-button"]').should('be.enabled');
    });
  });

  describe('認証状態管理', () => {
    it('未認証状態では保護されたページにアクセスできない', () => {
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });

    it('認証状態が正常に維持される', () => {
      cy.login();
      cy.visit('/mypage');
      cy.url().should('include', '/mypage');
      
      // ページをリロードしても認証状態が維持される
      cy.reload();
      cy.url().should('include', '/mypage');
    });
  });
});