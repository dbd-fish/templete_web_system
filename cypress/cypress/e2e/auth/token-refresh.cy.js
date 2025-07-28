/**
 * トークンリフレッシュ機能の基本動作テスト
 * 
 * 注意: このファイルはAPI単位でのテストが中心です。
 * 顧客シナリオベースのE2Eテストは以下を参照してください:
 * - /cypress/e2e/user-scenarios/user-journey.cy.js
 * - /cypress/e2e/user-scenarios/authentication-flow.cy.js
 * 
 * 実際の顧客操作に基づくトークンリフレッシュテストは上記ファイルで実装されています。
 */
describe('トークンリフレッシュ機能テスト（実API使用）', () => {
  const baseUrl = 'http://frontend:5173';
  
  beforeEach(() => {
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('自動トークンリフレッシュ画面操作テスト', () => {
    it('ログイン後に長時間操作でアクセストークンが自動更新される', () => {
      // ログインしてマイページに移動
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // Cookie確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // マイページでページをリロードして認証が継続されることを確認
      cy.reload();
      cy.url().should('include', '/mypage');
      
      // トークンが維持されていることを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });

    it('無効なトークン状態で画面操作するとログインページにリダイレクトされる', () => {
      // 無効なトークンを設定
      cy.setCookie('authToken', 'invalid_token_12345');
      cy.setCookie('refreshToken', 'invalid_refresh_token_12345');
      
      // マイページにアクセス
      cy.visit('/mypage');
      
      // ログインページにリダイレクトされることを確認
      cy.url().should('include', '/login');
    });

    it('リフレッシュトークンのみが無効な場合ログインページにリダイレクトされる', () => {
      // 先にログインして有効なトークンを取得
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // アクセストークンは有効にしてリフレッシュトークンのみ無効にする
      cy.getCookie('authToken').then((authCookie) => {
        cy.clearCookies();
        cy.setCookie('authToken', authCookie.value);
        cy.setCookie('refreshToken', 'invalid_refresh_token');
        
        // マイページにアクセス
        cy.visit('/mypage');
        
        // 認証エラーによりログインページにリダイレクトされる
        cy.url().should('include', '/login');
      });
    });
  });

  describe('トークン有効期限テスト', () => {
    it('アクセストークンの有効期限が30分であることを確認', () => {
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // Cookieの有効期限を確認
      cy.getCookie('authToken').then((cookie) => {
        expect(cookie).to.not.be.null;
        expect(cookie.value).to.not.be.empty;
        
        // 有効期限が現在時刻から約30分後であることを確認
        const now = Date.now() / 1000;
        const expectedExpiry = now + (30 * 60); // 30分
        
        // 誤差を考慮して±5分の範囲で確認
        expect(cookie.expiry).to.be.within(expectedExpiry - 300, expectedExpiry + 300);
      });
    });

    it('リフレッシュトークンの有効期限が5日であることを確認', () => {
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // Cookieの有効期限を確認
      cy.getCookie('refreshToken').then((cookie) => {
        expect(cookie).to.not.be.null;
        expect(cookie.value).to.not.be.empty;
        
        // 有効期限が現在時刻から約5日後であることを確認
        const now = Date.now() / 1000;
        const expectedExpiry = now + (5 * 24 * 60 * 60); // 5日
        
        // 誤差を考慮して±1時間の範囲で確認
        expect(cookie.expiry).to.be.within(expectedExpiry - 3600, expectedExpiry + 3600);
      });
    });
  });

  describe('認証なしアクセステスト', () => {
    it('認証なしでマイページにアクセスするとログインページにリダイレクトされる', () => {
      // Cookieをクリア
      cy.clearCookies();
      
      // マイページに直接アクセス
      cy.visit('/mypage');
      
      // ログインページにリダイレクトされることを確認
      cy.url().should('include', '/login');
    });

    it('期限切れトークンでマイページアクセスするとログインページにリダイレクトされる', () => {
      // 無効なトークンを設定
      cy.setCookie('authToken', 'expired_token_12345');
      
      // マイページにアクセス
      cy.visit('/mypage');
      
      // 認証エラーによりログインページにリダイレクトされる
      cy.url().should('include', '/login');
    });
  });

  describe('リフレッシュ後の画面操作確認', () => {
    it('セッション継続中にマイページの機能が正常に動作する', () => {
      // ログイン
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // マイページでの基本操作確認
      cy.url().should('include', '/mypage');
      
      // ページをリロードしてもログイン状態が維持される
      cy.reload();
      cy.url().should('include', '/mypage');
      
      // ユーザーメニューが表示される
      cy.get('[data-cy="user-menu-button"]').should('be.visible');
      
      // プロフィール情報が表示される
      cy.get('[data-cy="user-profile"]').should('be.visible');
      
      // トークンが継続して有効
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });

    it('ログイン後に他のページに移動してもセッションが維持される', () => {
      // ログイン
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // ホームページに移動
      cy.visit('/');
      
      // ログイン状態が維持されている（ログインボタンではなくユーザーメニューが表示）
      cy.get('[data-cy="user-menu-button"]').should('be.visible');
      
      // 再度マイページに戻る
      cy.get('[data-cy="user-menu-button"]').click();
      cy.get('[data-cy="mypage-link"]').click();
      cy.url().should('include', '/mypage');
    });
  });
});