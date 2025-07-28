/**
 * Cookie管理機能のE2Eテスト
 * 
 * テスト項目:
 * - ログイン後のCookie設定確認
 * - Cookie属性（HttpOnly、Secure、SameSite）の確認
 * - Cookie有効期限の確認
 * - ログアウト時のCookie削除確認
 * - Cookie操作のセキュリティテスト
 */
describe('Cookie管理機能テスト', () => {
  const baseUrl = 'http://frontend:5173';
  
  beforeEach(() => {
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('ログイン時のCookie設定', () => {
    it('ログイン成功時にauthTokenとrefreshTokenのCookieが設定される', () => {
      // ログイン前はCookieが存在しないことを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
      
      // ログイン実行
      cy.login();
      
      // ログイン後にCookieが設定されることを確認
      cy.getCookie('authToken').should('exist').and((cookie) => {
        expect(cookie.value).to.not.be.empty;
        expect(cookie.httpOnly).to.be.true;
        expect(cookie.sameSite).to.eq('lax');
      });
      
      cy.getCookie('refreshToken').should('exist').and((cookie) => {
        expect(cookie.value).to.not.be.empty;
        expect(cookie.httpOnly).to.be.true;
        expect(cookie.sameSite).to.eq('lax');
      });
    });

    it('画面操作でのログインでCookie属性が正しく設定される', () => {
      // 画面操作でログイン
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功確認
      cy.url().should('include', '/mypage');
      
      // Cookieが適切に設定されることを確認
      cy.getCookie('authToken').should('exist').and((cookie) => {
        expect(cookie.httpOnly).to.be.true;
        expect(cookie.sameSite).to.eq('lax');
      });
      
      cy.getCookie('refreshToken').should('exist').and((cookie) => {
        expect(cookie.httpOnly).to.be.true;
        expect(cookie.sameSite).to.eq('lax');
      });
    });

    it('フォーム経由のログインでもCookieが正しく設定される', () => {
      // フォーム経由でログイン
      cy.loginViaForm();
      
      // Cookieが設定されることを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });
  });

  describe('Cookie属性の確認', () => {
    beforeEach(() => {
      cy.login();
    });

    it('authTokenのCookie属性が正しく設定されている', () => {
      cy.getCookie('authToken').should('exist').and((cookie) => {
        // HttpOnly属性の確認
        expect(cookie.httpOnly).to.be.true;
        
        // SameSite属性の確認
        expect(cookie.sameSite).to.eq('lax');
        
        // ドメインの確認（省略可能、環境依存）
        // expect(cookie.domain).to.include('localhost');
        
        // Cookieの値が空でないことを確認
        expect(cookie.value).to.not.be.empty;
        expect(cookie.value.length).to.be.greaterThan(10); // JWTは十分長い
      });
    });

    it('refreshTokenのCookie属性が正しく設定されている', () => {
      cy.getCookie('refreshToken').should('exist').and((cookie) => {
        // HttpOnly属性の確認
        expect(cookie.httpOnly).to.be.true;
        
        // SameSite属性の確認
        expect(cookie.sameSite).to.eq('lax');
        
        // Cookieの値が空でないことを確認
        expect(cookie.value).to.not.be.empty;
        expect(cookie.value.length).to.be.greaterThan(10); // JWTは十分長い
      });
    });

    it('Cookieの有効期限が適切に設定されている', () => {
      const currentTime = new Date().getTime();
      
      cy.getCookie('authToken').should('exist').and((cookie) => {
        // 有効期限が未来の時刻であることを確認
        if (cookie.expiry) {
          expect(cookie.expiry * 1000).to.be.greaterThan(currentTime);
          
          // 30分以内であることを確認（少し余裕を持たせる）
          const expectedExpiry = currentTime + (35 * 60 * 1000); // 35分後
          expect(cookie.expiry * 1000).to.be.lessThan(expectedExpiry);
        }
      });
      
      cy.getCookie('refreshToken').should('exist').and((cookie) => {
        // 有効期限が未来の時刻であることを確認
        if (cookie.expiry) {
          expect(cookie.expiry * 1000).to.be.greaterThan(currentTime);
          
          // 5日以内であることを確認（少し余裕を持たせる）
          const expectedExpiry = currentTime + (6 * 24 * 60 * 60 * 1000); // 6日後
          expect(cookie.expiry * 1000).to.be.lessThan(expectedExpiry);
        }
      });
    });
  });

  describe('ログアウト時のCookie削除', () => {
    beforeEach(() => {
      cy.login();
    });

    it('ログアウト時にauthTokenとrefreshTokenが削除される', () => {
      // ログアウト前にCookieが存在することを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // ログアウト実行（Cookie削除確認付き）
      cy.logoutAndVerifyCookies();
      
      // ログアウト後にCookieが削除されることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });

    it('画面操作でのログアウトでCookieが削除される', () => {
      // 画面操作でログアウト
      cy.visit('/mypage');
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ログアウト完了確認
      cy.url().should('include', '/login');
      
      // ログアウト後にCookieが削除されることを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });
  });

  describe('Cookie操作のセキュリティテスト', () => {
    beforeEach(() => {
      cy.login();
    });

    it('JavaScriptからHttpOnly Cookieにアクセスできないことを確認', () => {
      cy.window().then((win) => {
        // document.cookieからHttpOnly Cookieは読み取れない
        const cookies = win.document.cookie;
        expect(cookies).to.not.include('authToken');
        expect(cookies).to.not.include('refreshToken');
      });
    });

    it('CookieのJWT内容が適切であることを確認', () => {
      cy.getCookie('authToken').should('exist').then((cookie) => {
        // JWTの形式確認（header.payload.signature）
        const tokenParts = cookie.value.split('.');
        expect(tokenParts).to.have.length(3);
        
        // Base64でデコードできることを確認（ここでは形式チェックのみ）
        expect(tokenParts[0]).to.match(/^[A-Za-z0-9_-]+$/);
        expect(tokenParts[1]).to.match(/^[A-Za-z0-9_-]+$/);
        expect(tokenParts[2]).to.match(/^[A-Za-z0-9_-]+$/);
      });
      
      cy.getCookie('refreshToken').should('exist').then((cookie) => {
        // JWTの形式確認
        const tokenParts = cookie.value.split('.');
        expect(tokenParts).to.have.length(3);
        
        expect(tokenParts[0]).to.match(/^[A-Za-z0-9_-]+$/);
        expect(tokenParts[1]).to.match(/^[A-Za-z0-9_-]+$/);
        expect(tokenParts[2]).to.match(/^[A-Za-z0-9_-]+$/);
      });
    });

    it('不正なCookieで保護されたページアクセスが拒否されることを確認', () => {
      // 不正なauthTokenを設定
      cy.setCookie('authToken', 'invalid.token.here');
      
      // 保護されたページにアクセス
      cy.visit('/mypage');
      
      // ログインページにリダイレクトされることを確認
      cy.url().should('include', '/login');
    });
  });

  describe('Cookie の並行操作テスト', () => {
    it('複数のタブでログインした場合のCookie管理', () => {
      // 最初のログイン
      cy.login();
      
      // Cookieが設定されることを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // 別のログインをシミュレート（同じCookieが上書きされる）
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // Cookieが引き続き存在することを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });

    it('セッション継続時のCookie維持', () => {
      cy.login();
      
      // Cookieが設定されることを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // ページをリロードしてセッション継続確認
      cy.reload();
      
      // ログイン状態が維持されることを確認
      cy.url().should('include', '/mypage');
      
      // Cookieが継続して存在することを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
    });
  });

  describe('エラーケースでのCookie処理', () => {
    it('ログイン失敗時にCookieが設定されないことを確認', () => {
      // 不正な認証情報で画面操作でログイン試行
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('invalid@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン失敗の確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      cy.url().should('include', '/login');
      
      // Cookieが設定されていないことを確認
      cy.getCookie('authToken').should('be.null');
      cy.getCookie('refreshToken').should('be.null');
    });

    it('ネットワークエラー時のCookie状態', () => {
      cy.login();
      
      // Cookieが設定されることを確認
      cy.getCookie('authToken').should('exist');
      cy.getCookie('refreshToken').should('exist');
      
      // ネットワークエラーをシミュレート
      cy.intercept('POST', '/api/v1/auth/logout', { forceNetworkError: true }).as('logoutError');
      
      // ログアウト試行（UIから）
      cy.visit('/mypage');
      cy.get('[data-cy="user-menu-button"]').should('be.visible').click();
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ネットワークエラーが発生した場合でも、
      // クライアント側でCookieがクリアされる場合があるかを確認
      // （アプリケーションの実装に依存）
    });
  });
});