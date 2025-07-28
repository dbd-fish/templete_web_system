/**
 * ログイン機能の基本動作テスト
 * 
 * 注意: このファイルは基本的なログイン機能の動作確認用です。
 * 顧客シナリオベースのE2Eテストは以下を参照してください:
 * - /cypress/e2e/user-scenarios/user-journey.cy.js
 * - /cypress/e2e/user-scenarios/authentication-flow.cy.js
 * - /cypress/e2e/user-scenarios/error-recovery.cy.js
 */
describe('ログイン機能テスト（実API使用）', () => {
  beforeEach(() => {
    cy.visit('/', { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('ログインページの表示', () => {
    it('ログインページが正常に表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="login-title"]').should('be.visible').and('contain', 'ログイン');
      cy.get('[data-cy="login-form"]').should('be.visible');
      cy.get('[data-cy="email-input"]').should('be.visible');
      cy.get('[data-cy="password-input"]').should('be.visible');
      cy.get('[data-cy="login-submit-button"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('be.visible');
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

  describe('実APIを使用したログイン機能', () => {
    it('基本的なログインフローをテスト', () => {
      // ログインページを訪問
      cy.visit('/login');
      
      // ページの読み込みを待つ
      cy.get('[data-cy="login-title"]').should('be.visible');
      cy.get('[data-cy="login-form"]').should('be.visible');
      
      // フォーム要素が有効になるまで待つ
      cy.get('[data-cy="email-input"]').should('be.enabled');
      cy.get('[data-cy="password-input"]').should('be.enabled');
      cy.get('[data-cy="login-submit-button"]').should('be.enabled');
      
      // メールアドレスとパスワードを入力
      cy.get('[data-cy="email-input"]')
        .clear()
        .type('targetuser@example.com');
      
      cy.get('[data-cy="password-input"]')
        .clear()
        .type('Password123456+-');
      
      // React Router v7のFormコンポーネントを使用してフォーム送信
      cy.get('[data-cy="login-form"]').submit();
      
      // ページ遷移の確認（長めのタイムアウト）
      cy.url({ timeout: 30000 }).should('not.include', '/login');
      cy.url({ timeout: 30000 }).should('include', '/mypage');
      
      // マイページのタイトルが表示されることを確認
      cy.get('[data-cy="mypage-title"]', { timeout: 15000 }).should('be.visible');
    });

    it('ログインコマンド（画面操作版）が成功する', () => {
      // 画面操作でのログイン
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // マイページが表示される
      cy.url().should('include', '/mypage');
      
      // マイページのコンテンツが表示されることを確認
      cy.get('[data-cy="mypage-title"]', { timeout: 10000 }).should('be.visible');
    });

    it('無効な認証情報でログインに失敗する', () => {
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('invalid@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword');
      cy.get('[data-cy="login-form"]').submit();
      
      // エラーメッセージが表示される
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // Cookieが設定されていないことを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });
  });

  describe('Cookie設定の確認', () => {
    it('ログイン成功時にCookieが設定される', () => {
      cy.loginViaForm('targetuser@example.com', 'Password123456+-');
      
      // マイページが表示されることを確認
      cy.url().should('include', '/mypage');
      
      // 基本的なCookieの存在確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });
  });

  describe('バリデーション', () => {
    it('必須フィールドが空の場合バリデーションエラーが表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="login-form"]').submit();
      
      // HTML5バリデーションが働く
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
    });

    it('不正なメールフォーマットでバリデーションエラーが表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('invalid-email');
      cy.get('[data-cy="password-input"]').type('password123');
      cy.get('[data-cy="login-form"]').submit();
      
      // HTML5バリデーションが働く
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
    });
  });

  describe('Googleログイン', () => {
    it('Googleログインボタンが表示される', () => {
      cy.visit('/login');
      cy.get('[data-cy="google-login-button"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('contain', 'Googleでログイン');
    });

    it('Googleログインボタンをクリックできる', () => {
      cy.visit('/login');
      cy.get('[data-cy="google-login-button"]').should('be.visible').click();
      
      // Google認証フローの開始（実際の実装に依存）
      // 実際のGoogle OAuth画面へのリダイレクトは環境により異なる
    });
  });

  describe('リダイレクト処理', () => {
    it('ログイン成功後に適切なページにリダイレクトされる', () => {
      cy.loginViaForm('targetuser@example.com', 'Password123456+-');
      
      // デフォルトではマイページにリダイレクト
      cy.url().should('include', '/mypage');
      
      // マイページのコンテンツが表示されることを確認
      cy.get('[data-cy="mypage-title"]', { timeout: 10000 }).should('be.visible');
    });

    it('保護されたページアクセス後のログインで元のページに戻る', () => {
      // 保護されたページに直接アクセス
      cy.visit('/mypage', { failOnStatusCode: false });
      
      // ログインページにリダイレクトされる（時間を短縮）
      cy.url().should('include', '/login', { timeout: 10000 });
      
      // ログイン実行
      cy.loginViaForm('targetuser@example.com', 'Password123456+-');
      
      // 元のページ（マイページ）にリダイレクトされる
      cy.url().should('include', '/mypage');
      
      // マイページのコンテンツが表示されることを確認
      cy.get('[data-cy="mypage-title"]', { timeout: 10000 }).should('be.visible');
    });
  });
});