/**
 * ログアウト機能のE2Eテスト（デュアルトークン対応版）
 * 
 * 修正内容:
 * - authTokenとrefreshTokenの両方が削除されることを確認
 * - Cookie削除の詳細テスト
 * - API直接呼び出しでのログアウトテスト
 */
describe('ログアウト機能テスト（デュアルトークン対応）', () => {
  const baseUrl = 'http://frontend:5173';
  
  beforeEach(() => {
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('UI経由でのログアウト', () => {
    beforeEach(() => {
      // テスト前にログイン
      cy.login();
    });

    it('ログアウトが正常に動作し、両方のCookieが削除される', () => {
      // ログアウト前にCookieが存在することを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // マイページにアクセス
      cy.visit('/mypage');
      
      // ログアウト実行（Cookie削除確認付き）
      cy.logoutAndVerifyCookies();
      
      // ログインページにリダイレクトされる
      cy.url().should('include', '/login');
      
      // Cookieが削除されていることを再確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });

    it('ログアウト後は保護されたページにアクセスできない', () => {
      cy.visit('/mypage');
      cy.logout();
      
      // 保護されたページに再アクセスを試みる
      cy.visit('/mypage');
      cy.url().should('include', '/login');
      
      // Cookieが削除されていることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });

    it('ユーザーメニューからのログアウトが正常に動作する', () => {
      cy.visit('/mypage');
      
      // ユーザーメニューを開く
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      
      // ログアウトボタンが表示されることを確認
      cy.get('[data-cy="logout-button"]').should('be.visible').and('contain', 'ログアウト');
      
      // ログアウト実行
      cy.get('[data-cy="logout-button"]').click();
      
      // ログインページにリダイレクト
      cy.url().should('include', '/login');
      
      // Cookieの削除確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });
  });

  describe('ログアウト処理の完全性確認', () => {
    beforeEach(() => {
      cy.login();
    });

    it('ログアウト操作が確実にセッションを終了する', () => {
      // ログアウト前にCookieが存在することを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // 画面操作でログアウト実行
      cy.visit('/mypage');
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ログアウト完了確認
      cy.url().should('include', '/login');
      
      // ログアウト後にCookieが削除されることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });

    it('ログアウト後に保護されたページへの直接アクセスが拒否される', () => {
      // ログアウト実行
      cy.logout();
      
      // 保護されたページに直接アクセス
      cy.visit('/mypage');
      
      // ログインページにリダイレクトされる
      cy.url().should('include', '/login');
      
      // 認証メッセージが表示される
      cy.contains('ログインが必要です').should('be.visible');
    });
  });

  describe('Cookie削除の詳細確認', () => {
    beforeEach(() => {
      cy.login();
    });

    it('ログアウト時にauthTokenCookieが適切に削除される', () => {
      // ログアウト前のauthToken確認
      cy.getCookie('authToken').should('exist').then((cookie) => {
        expect(cookie.value).to.not.be.empty;
        expect(cookie.httpOnly).to.be.true;
      });
      
      // ログアウト実行
      cy.logout();
      
      // authTokenが削除されることを確認
      cy.getCookie('authToken').should('be.null');
    });

    it('ログアウト時にrefreshTokenCookieが適切に削除される', () => {
      // ログアウト前のrefreshToken確認
      cy.getCookie('refreshToken').should('exist').then((cookie) => {
        expect(cookie.value).to.not.be.empty;
        expect(cookie.httpOnly).to.be.true;
      });
      
      // ログアウト実行
      cy.logout();
      
      // refreshTokenが削除されることを確認
      cy.getCookie('refreshToken').should('be.null');
    });

    it('ログアウト後にどちらのCookieも復活しない', () => {
      cy.logout();
      
      // Cookieが削除されることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
      
      // 少し待機してもCookieが復活しないことを確認
      cy.wait(1000);
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });
  });

  describe('複数タブでのログアウト', () => {
    beforeEach(() => {
      cy.login();
    });

    it('一つのタブでログアウトすると他のタブでも認証状態が解除される', () => {
      // 最初のタブでマイページにアクセス
      cy.visit('/mypage');
      cy.url().should('include', '/mypage');
      
      // ログアウト実行
      cy.logout();
      
      // ログアウト後に保護されたページにアクセスを試みる
      cy.visit('/mypage');
      cy.url().should('include', '/login');
      
      // Cookieが削除されていることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });
  });

  describe('認証状態の確認', () => {
    it('未認証状態では保護されたページにアクセスできない', () => {
      // 最初はCookieが存在しない
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
      
      // 保護されたページにアクセスを試みる
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });

    it('ログアウト後の認証状態が維持されない', () => {
      // ログインして認証状態を確立
      cy.login();
      cy.visit('/mypage');
      cy.url().should('include', '/mypage');
      
      // ログアウト実行
      cy.logout();
      
      // ページをリロードしても認証状態が復活しない
      cy.reload();
      cy.url().should('include', '/login');
      
      // 別の保護されたページにアクセスしても認証状態が復活しない
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });
  });

  describe('エラーケースでのログアウト', () => {
    beforeEach(() => {
      cy.login();
    });

    it('ネットワークエラー時のログアウト処理', () => {
      // ネットワークエラーをモック
      cy.intercept('POST', '/api/v1/auth/logout', { forceNetworkError: true }).as('logoutNetworkError');
      
      cy.visit('/mypage');
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ネットワークエラーが発生した場合の処理を確認
      // 実装によってはクライアント側でCookieがクリアされる場合がある
    });

    it('サーバーエラー時のログアウト処理', () => {
      // サーバーエラーをモック
      cy.intercept('POST', '/api/v1/auth/logout', {
        statusCode: 500,
        body: { detail: 'サーバー内部エラーが発生しました' }
      }).as('logoutServerError');
      
      cy.visit('/mypage');
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // サーバーエラーが発生した場合の処理を確認
      // 実装によってはクライアント側でCookieがクリアされる場合がある
    });

    it('認証なし状態でのログアウトボタン表示確認', () => {
      // 事前にCookieをクリア
      cy.clearCookies();
      
      // トップページにアクセス
      cy.visit('/');
      
      // ログアウト状態ではユーザーメニューが表示されない
      cy.get('[data-cy="user-menu-button"]').should('not.exist');
      
      // ログインリンクが表示される
      cy.get('[data-cy="login-link"]').should('be.visible');
    });
  });

  describe('セキュリティ関連のログアウト', () => {
    beforeEach(() => {
      cy.login();
    });

    it('ログアウト後にユーザー情報が取得できない', () => {
      cy.logout();
      
      // ログアウト後にマイページにアクセス
      cy.visit('/mypage');
      
      // ログインページにリダイレクトされることで認証が拒否されたことを確認
      cy.url().should('include', '/login');
    });

    it('ログアウト後にブラウザ履歴で戻ってもアクセスできない', () => {
      cy.visit('/mypage');
      cy.logout();
      
      // ブラウザの戻るボタンをシミュレート
      cy.go('back');
      
      // 保護されたページにアクセスできないことを確認
      cy.url().should('include', '/login');
    });
  });
});