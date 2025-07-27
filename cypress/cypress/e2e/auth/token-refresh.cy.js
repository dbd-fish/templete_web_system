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

  describe('リフレッシュAPI直接テスト', () => {
    it('有効なリフレッシュトークンでリフレッシュが成功する', () => {
      // ログインしてリフレッシュトークンを取得
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // リフレッシュAPIを直接呼び出し
      cy.getCookie('refreshToken').then((cookie) => {
        cy.request({
          method: 'POST',
          url: 'http://backend:8000/api/v1/auth/refresh',
          headers: {
            'Cookie': `refreshToken=${cookie.value}`
          },
          failOnStatusCode: false
        }).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.have.property('message');
          
          // レスポンスヘッダーにSet-Cookieが含まれることを確認
          expect(response.headers).to.have.property('set-cookie');
          
          const cookies = response.headers['set-cookie'];
          const hasAuthToken = cookies.some(cookie => cookie.includes('authToken='));
          const hasRefreshToken = cookies.some(cookie => cookie.includes('refreshToken='));
          
          expect(hasAuthToken).to.be.true;
          expect(hasRefreshToken).to.be.true;
        });
      });
    });

    it('無効なリフレッシュトークンでリフレッシュが失敗する', () => {
      // リフレッシュAPIを無効なトークンで呼び出し
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/refresh',
        headers: {
          'Cookie': 'refreshToken=invalid_token_12345'
        },
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(401);
        expect(response.body).to.have.property('detail');
      });
    });

    it('リフレッシュトークンなしでリフレッシュが失敗する', () => {
      // CookieなしでリフレッシュAPIを呼び出し
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/refresh',
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(401);
        expect(response.body).to.have.property('detail');
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

    it('期限切れトークンでAPIアクセスすると401エラーが返される', () => {
      // 無効なトークンを設定
      cy.setCookie('authToken', 'expired_token_12345');
      
      // APIを直接呼び出し
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/auth/me',
        headers: {
          'Cookie': 'authToken=expired_token_12345'
        },
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(401);
        expect(response.body).to.have.property('detail');
      });
    });
  });

  describe('リフレッシュ後の動作確認', () => {
    it('リフレッシュ後に新しいトークンでAPIアクセスできる', () => {
      // ログイン
      cy.login('targetuser@example.com', 'Password123456+-');
      
      // リフレッシュトークンを取得してリフレッシュ実行
      cy.getCookie('refreshToken').then((refreshCookie) => {
        cy.request({
          method: 'POST',
          url: 'http://backend:8000/api/v1/auth/refresh',
          headers: {
            'Cookie': `refreshToken=${refreshCookie.value}`
          }
        }).then((refreshResponse) => {
          // 新しいトークンが発行されたことを確認
          expect(refreshResponse.status).to.eq(200);
          
          // 新しいトークンでユーザー情報を取得
          const setCookies = refreshResponse.headers['set-cookie'];
          const authTokenCookie = setCookies.find(cookie => cookie.includes('authToken='));
          const authToken = authTokenCookie.match(/authToken=([^;]+)/)[1];
          
          cy.request({
            method: 'POST',
            url: 'http://backend:8000/api/v1/auth/me',
            headers: {
              'Cookie': `authToken=${authToken}`
            }
          }).then((meResponse) => {
            expect(meResponse.status).to.eq(200);
            expect(meResponse.body).to.have.property('email');
            expect(meResponse.body.email).to.eq('targetuser@example.com');
          });
        });
      });
    });
  });
});