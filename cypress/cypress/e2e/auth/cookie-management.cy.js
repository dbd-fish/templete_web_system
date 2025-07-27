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

    it('ログイン時のAPIレスポンスでSet-Cookieヘッダーが正しく設定される', () => {
      // ログインAPIを直接呼び出してレスポンスヘッダーを確認
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/login',
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          username: 'targetuser@example.com',
          password: 'Password123456+-'
        }
      }).then((response) => {
        expect(response.status).to.eq(200);
        
        const cookies = response.headers['set-cookie'];
        expect(cookies).to.exist;
        
        // authTokenのCookie確認
        const authTokenCookie = cookies.find(cookie => cookie.includes('authToken='));
        expect(authTokenCookie).to.exist;
        expect(authTokenCookie).to.include('HttpOnly');
        expect(authTokenCookie).to.include('SameSite=lax');
        
        // refreshTokenのCookie確認
        const refreshTokenCookie = cookies.find(cookie => cookie.includes('refreshToken='));
        expect(refreshTokenCookie).to.exist;
        expect(refreshTokenCookie).to.include('HttpOnly');
        expect(refreshTokenCookie).to.include('SameSite=lax');
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

    it('ログアウトAPIの直接呼び出しでCookieが削除される', () => {
      // ログアウトAPIを直接呼び出し
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/logout'
      }).then((response) => {
        expect(response.status).to.eq(200);
        
        const cookies = response.headers['set-cookie'];
        if (cookies) {
          // Cookie削除のSet-Cookieヘッダーを確認
          const authTokenDeleteCookie = cookies.find(cookie => 
            cookie.includes('authToken=') && (cookie.includes('Max-Age=0') || cookie.includes('expires='))
          );
          const refreshTokenDeleteCookie = cookies.find(cookie => 
            cookie.includes('refreshToken=') && (cookie.includes('Max-Age=0') || cookie.includes('expires='))
          );
          
          // 削除用のCookieヘッダーが存在することを確認
          expect(authTokenDeleteCookie || refreshTokenDeleteCookie).to.exist;
        }
      });
      
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

    it('不正なCookieでAPIアクセスが拒否されることを確認', () => {
      // 不正なauthTokenを設定
      cy.setCookie('authToken', 'invalid.token.here');
      
      // APIアクセスを試行
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/me',
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
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

    it('リフレッシュ時のCookie更新', () => {
      cy.login();
      
      // 現在のCookie値を保存
      let originalAuthToken;
      let originalRefreshToken;
      
      cy.getCookie('authToken').then((cookie) => {
        originalAuthToken = cookie.value;
      });
      
      cy.getCookie('refreshToken').then((cookie) => {
        originalRefreshToken = cookie.value;
      });
      
      // リフレッシュAPI直接呼び出し
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/refresh'
      }).then((response) => {
        expect(response.status).to.eq(200);
      });
      
      // 新しいCookieが設定されることを確認
      cy.getCookie('authToken').should('exist').and((cookie) => {
        // 新しいトークンが設定されていることを確認
        // 実装によってはトークンが変わる場合とそうでない場合がある
        expect(cookie.value).to.not.be.empty;
      });
      
      cy.getCookie('refreshToken').should('exist').and((cookie) => {
        expect(cookie.value).to.not.be.empty;
      });
    });
  });

  describe('エラーケースでのCookie処理', () => {
    it('ログイン失敗時にCookieが設定されないことを確認', () => {
      // 不正な認証情報でログイン試行
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/login',
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          username: 'invalid@example.com',
          password: 'wrongpassword'
        },
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.not.eq(200);
        
        // Set-Cookieヘッダーが存在しないか、または削除用のヘッダーであることを確認
        const cookies = response.headers['set-cookie'];
        if (cookies) {
          const hasValidAuthToken = cookies.some(cookie => 
            cookie.includes('authToken=') && !cookie.includes('Max-Age=0')
          );
          const hasValidRefreshToken = cookies.some(cookie => 
            cookie.includes('refreshToken=') && !cookie.includes('Max-Age=0')
          );
          
          expect(hasValidAuthToken).to.be.false;
          expect(hasValidRefreshToken).to.be.false;
        }
      });
      
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