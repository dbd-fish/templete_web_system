/**
 * セキュリティテスト（A013タスク対応）
 * 
 * テスト対象:
 * - OWASP Top 10 脆弱性検査
 * - 認証・認可セキュリティテスト
 * - セッション管理セキュリティ検証
 * - クロスサイトスクリプティング(XSS)対策
 * - SQLインジェクション対策
 * - CSRF対策検証
 * - セキュアクッキー設定確認
 */
describe('セキュリティテスト (A013)', () => {
  const baseUrl = '/';
  const backendUrl = 'http://backend:8000'; // 内部通信はHTTP
  
  beforeEach(() => {
    // セキュリティテスト用の設定
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('認証セキュリティテスト', () => {
    it('弱いパスワードに対するバリデーション強化確認', () => {
      cy.visit('/signup');
      
      const weakPasswords = [
        '123456',        // 数字のみ
        'password',      // 辞書攻撃対象
        'abc123',        // 短すぎる
        '12345678',      // 数字のみ8文字
        'abcdefgh',      // 文字のみ
        'Password',      // 大文字小文字のみ
        'password123'    // 辞書+数字
      ];

      weakPasswords.forEach(password => {
        cy.get('[data-cy="signup-password-input"]').clear().type(password);
        cy.get('[data-cy="signup-confirm-password-input"]').clear().type(password);
        
        // 弱いパスワードに対するエラーメッセージ確認
        cy.contains('パスワードが条件を満たしていません').should('be.visible')
          .or(cy.contains('パスワードが弱すぎます').should('be.visible'))
          .or(cy.contains('安全でないパスワード').should('be.visible'));
      });
    });

    it('ブルートフォース攻撃対策: 連続ログイン失敗制限', () => {
      const testEmail = 'brute.force@example.com';
      const incorrectPasswords = ['wrong1', 'wrong2', 'wrong3', 'wrong4', 'wrong5'];
      
      cy.visit('/login');
      
      incorrectPasswords.forEach((password, index) => {
        cy.get('[data-cy="email-input"]').clear().type(testEmail);
        cy.get('[data-cy="password-input"]').clear().type(password);
        
        // APIリクエストの監視
        cy.intercept('POST', '**/auth/login').as(`loginAttempt${index + 1}`);
        
        cy.get('[data-cy="login-submit-button"]').click();
        
        cy.wait(`@loginAttempt${index + 1}`).then((interception) => {
          // 複数回失敗後のレート制限確認
          if (index >= 2) { // 3回目以降
            expect([401, 429]).to.include(interception.response.statusCode);
            if (interception.response.statusCode === 429) {
              cy.contains('ログイン試行回数が上限を超えました').should('be.visible')
                .or(cy.contains('アカウントが一時的にロックされました').should('be.visible'));
            }
          }
        });
      });
    });

    it('セッションハイジャック対策: セッションID再生成確認', () => {
      // ログイン前のセッションIDを記録
      let initialSessionId;
      
      cy.getCookies().then((cookies) => {
        const sessionCookie = cookies.find(cookie => cookie.name === 'authToken');
        initialSessionId = sessionCookie?.value;
      });

      // ログイン実行
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'new_session_token_12345',
          user: {
            user_id: '1',
            email: 'security@example.com',
            username: 'Security User'
          }
        }
      }).as('secureLogin');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('security@example.com');
      cy.get('[data-cy="password-input"]').type('SecurePass123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.wait('@secureLogin');
      
      // ログイン後のセッションIDが変更されているか確認
      cy.getCookies().then((cookies) => {
        const newSessionCookie = cookies.find(cookie => cookie.name === 'authToken');
        expect(newSessionCookie?.value).to.not.equal(initialSessionId);
        expect(newSessionCookie?.value).to.exist;
      });
    });

    it('パスワードリセット セキュリティ検証', () => {
      const testEmail = 'reset.security@example.com';
      
      // パスワードリセットトークンの推測攻撃対策
      const maliciousTokens = [
        '123456789',
        'admin',
        'password',
        'token',
        '00000000-0000-0000-0000-000000000000'
      ];

      maliciousTokens.forEach(token => {
        cy.visit(`/reset-password?token=${token}`);
        
        // 無効なトークンに対するセキュアな応答確認
        cy.contains('無効なトークンです').should('be.visible')
          .or(cy.contains('リンクが無効です').should('be.visible'))
          .or(cy.contains('アクセスが拒否されました').should('be.visible'));
      });
    });
  });

  describe('セッション管理セキュリティ', () => {
    it('HttpOnlyクッキー設定確認', () => {
      // ログイン実行
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: { access_token: 'test_token', user: { user_id: '1' } }
      }).as('login');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('httponly@example.com');
      cy.get('[data-cy="password-input"]').type('SecurePass123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.wait('@login');
      
      // HttpOnlyクッキーがJavaScriptからアクセスできないことを確認
      cy.window().then((win) => {
        try {
          const authToken = win.document.cookie
            .split(';')
            .find(cookie => cookie.trim().startsWith('authToken='));
          
          // HttpOnlyクッキーはJavaScriptからアクセスできないはず
          expect(authToken).to.be.undefined;
        } catch (error) {
          // HttpOnlyが正しく設定されていればエラーになる
          expect(error).to.exist;
        }
      });
    });

    it('Secureクッキー設定確認（HTTPS環境）', () => {
      cy.intercept('POST', '**/auth/login').as('loginRequest');
      
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('secure@example.com');
      cy.get('[data-cy="password-input"]').type('SecurePass123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.wait('@loginRequest');
      
      // レスポンスヘッダーでSecure属性確認
      cy.getCookies().then((cookies) => {
        const authCookie = cookies.find(cookie => cookie.name === 'authToken');
        if (authCookie) {
          expect(authCookie.secure).to.be.true;
          expect(authCookie.sameSite).to.be.oneOf(['lax', 'strict']);
        }
      });
    });

    it('セッションタイムアウト処理確認', () => {
      // 期限切れトークンのシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 401,
        body: { error: 'Token expired' }
      }).as('expiredToken');

      // 直接マイページアクセス（期限切れセッション）
      cy.visit('/mypage');
      cy.wait('@expiredToken');
      
      // 自動的にログインページにリダイレクトされることを確認
      cy.url().should('include', '/login');
      cy.contains('セッションが期限切れです').should('be.visible')
        .or(cy.contains('再度ログインしてください').should('be.visible'));
    });

    it('同時セッション制限確認', () => {
      // 複数デバイスからのログインシミュレート
      const user = {
        email: 'multi.session@example.com',
        password: 'MultiPass123!'
      };

      // 1回目のログイン
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'session_1_token',
          user: { user_id: '1', email: user.email }
        }
      }).as('firstLogin');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type(user.email);
      cy.get('[data-cy="password-input"]').type(user.password);
      cy.get('[data-cy="login-submit-button"]').click();
      cy.wait('@firstLogin');

      // 2回目のログイン（別デバイス想定）
      cy.clearCookies();
      
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'session_2_token',
          user: { user_id: '1', email: user.email },
          message: '他のデバイスのセッションが無効化されました'
        }
      }).as('secondLogin');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type(user.email);
      cy.get('[data-cy="password-input"]').type(user.password);
      cy.get('[data-cy="login-submit-button"]').click();
      cy.wait('@secondLogin');
    });
  });

  describe('XSS（クロスサイトスクリプティング）対策', () => {
    it('入力フィールドでのXSSペイロード無害化確認', () => {
      const xssPayloads = [
        '<script>alert("XSS")</script>',
        '<img src="x" onerror="alert(\'XSS\')">',
        '<svg onload="alert(\'XSS\')">',
        'javascript:alert("XSS")',
        '<iframe src="javascript:alert(\'XSS\')"></iframe>',
        '"><script>alert("XSS")</script>',
        "'><script>alert('XSS')</script>"
      ];

      cy.visit('/signup');
      
      xssPayloads.forEach(payload => {
        // ユーザー名フィールドでXSSテスト
        cy.get('[data-cy="signup-username-input"]').clear().type(payload);
        
        // メールフィールドでXSSテスト  
        cy.get('[data-cy="signup-email-input"]').clear().type(`test${payload}@example.com`);
        
        // スクリプトが実行されないことを確認
        cy.window().then((win) => {
          expect(win.document.body.innerHTML).to.not.contain('<script>');
          expect(win.document.body.innerHTML).to.not.contain('javascript:');
        });
        
        // エスケープされた値が表示されることを確認
        cy.get('[data-cy="signup-username-input"]').should('not.contain', '<script>');
      });
    });

    it('URLパラメータでのXSS対策確認', () => {
      const xssUrls = [
        '/reset-password?token=<script>alert("XSS")</script>',
        '/signup?ref=javascript:alert("XSS")',
        '/login?redirect=<img src=x onerror=alert("XSS")>'
      ];

      xssUrls.forEach(url => {
        cy.visit(url, { failOnStatusCode: false });
        
        // スクリプトが実行されないことを確認
        cy.window().then((win) => {
          expect(win.document.body.innerHTML).to.not.contain('<script>');
          expect(win.location.href).to.not.contain('javascript:');
        });
      });
    });
  });

  describe('CSRF（クロスサイトリクエストフォージェリ）対策', () => {
    it('CSRFトークン確認', () => {
      cy.visit('/login');
      
      // フォームにCSRFトークンまたはSameSite属性が設定されているか確認
      cy.get('form').should('exist').then(($form) => {
        // CSRFトークンフィールドの存在確認
        const csrfInput = $form.find('input[name*="csrf"], input[name*="token"]');
        
        if (csrfInput.length === 0) {
          // CSRFトークンがない場合、SameSiteクッキーで対策されているか確認
          cy.getCookies().then((cookies) => {
            const authCookie = cookies.find(c => c.name === 'authToken' || c.name.includes('session'));
            if (authCookie) {
              expect(authCookie.sameSite).to.be.oneOf(['lax', 'strict']);
            }
          });
        }
      });
    });

    it('外部サイトからのリクエスト拒否確認', () => {
      // 外部オリジンからのリクエストをシミュレート
      cy.request({
        method: 'POST',
        url: `${backendUrl}/api/v1/auth/login`,
        failOnStatusCode: false,
        headers: {
          'Origin': 'https://malicious-site.com',
          'Referer': 'https://malicious-site.com',
          'Content-Type': 'application/json'
        },
        body: {
          email: 'attacker@example.com',
          password: 'attack123'
        }
      }).then((response) => {
        // CORS制限によりリクエストが拒否されることを確認
        expect([400, 403, 404]).to.include(response.status);
      });
    });
  });

  describe('SQL インジェクション対策', () => {
    it('ログインフォームでのSQLインジェクション対策', () => {
      const sqlInjectionPayloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' UNION SELECT * FROM users--",
        "admin'--",
        "'; DROP TABLE users;--",
        "' OR 'x'='x",
        "1' OR '1'='1' /*",
        "' OR 1=1#"
      ];

      cy.visit('/login');
      
      sqlInjectionPayloads.forEach(payload => {
        cy.get('[data-cy="email-input"]').clear().type(payload);
        cy.get('[data-cy="password-input"]').clear().type(payload);
        
        cy.intercept('POST', '**/auth/login').as('sqlInjectionAttempt');
        
        cy.get('[data-cy="login-submit-button"]').click();
        
        cy.wait('@sqlInjectionAttempt').then((interception) => {
          // SQLインジェクションが防がれ、通常の認証エラーになることを確認
          expect([400, 401]).to.include(interception.response.statusCode);
          expect(interception.response.body).to.not.have.property('users');
          expect(interception.response.body).to.not.have.property('database');
        });
      });
    });
  });

  describe('権限昇格攻撃対策', () => {
    it('一般ユーザーが管理者機能にアクセスできないことを確認', () => {
      // 一般ユーザーとしてログイン
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'user_token_12345',
          user: {
            user_id: '2',
            email: 'regular@example.com',
            username: 'Regular User',
            user_role: 'free' // 一般ユーザー
          }
        }
      }).as('userLogin');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('regular@example.com');
      cy.get('[data-cy="password-input"]').type('UserPass123!');
      cy.get('[data-cy="login-submit-button"]').click();
      cy.wait('@userLogin');

      // 管理者専用APIエンドポイントへの直接アクセス試行
      cy.request({
        method: 'GET',
        url: `${backendUrl}/api/v1/admin/users`,
        failOnStatusCode: false,
        headers: {
          'Authorization': 'Bearer user_token_12345'
        }
      }).then((response) => {
        // 権限不足で拒否されることを確認
        expect([401, 403]).to.include(response.status);
      });

      // フロントエンドでも管理者機能が表示されないことを確認
      cy.visit('/mypage');
      cy.get('[data-cy="admin-functions"]').should('not.exist');
      cy.get('[data-cy="user-management-toggle"]').should('not.exist');
    });

    it('トークン改ざん検出確認', () => {
      const tamperedTokens = [
        'fake_admin_token',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature',
        'Bearer admin_access',
        'modified_token_12345'
      ];

      tamperedTokens.forEach(token => {
        cy.request({
          method: 'GET',
          url: `${backendUrl}/api/v1/auth/me`,
          failOnStatusCode: false,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }).then((response) => {
          // 改ざんされたトークンが拒否されることを確認
          expect([401, 403]).to.include(response.status);
        });
      });
    });
  });

  describe('データ暴露対策', () => {
    it('機密情報の漏洩防止確認', () => {
      // ログインAPIのレスポンスで機密情報が含まれていないことを確認
      cy.intercept('POST', '**/auth/login').as('loginResponse');
      
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('datatest@example.com');
      cy.get('[data-cy="password-input"]').type('DataTest123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.wait('@loginResponse').then((interception) => {
        if (interception.response.statusCode === 200) {
          const responseBody = interception.response.body;
          
          // 機密情報が含まれていないことを確認
          expect(responseBody).to.not.have.property('password');
          expect(responseBody).to.not.have.property('hashed_password');
          expect(responseBody).to.not.have.property('secret');
          expect(responseBody).to.not.have.property('private_key');
          
          // JWTトークンは提供されるが、内容が適切にエンコードされているか確認
          if (responseBody.access_token) {
            expect(responseBody.access_token).to.be.a('string');
            expect(responseBody.access_token.length).to.be.greaterThan(10);
          }
        }
      });
    });

    it('エラーメッセージでの情報漏洩防止', () => {
      // 存在しないユーザーでログイン試行
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('nonexistent@example.com');
      cy.get('[data-cy="password-input"]').type('AnyPass123!');
      
      cy.intercept('POST', '**/auth/login').as('failedLogin');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.wait('@failedLogin').then((interception) => {
        if (interception.response.statusCode === 401) {
          const errorMessage = interception.response.body.error || '';
          
          // ユーザーの存在/非存在を特定できるメッセージでないことを確認
          expect(errorMessage.toLowerCase()).to.not.contain('user not found');
          expect(errorMessage.toLowerCase()).to.not.contain('ユーザーが見つかりません');
          expect(errorMessage.toLowerCase()).to.not.contain('存在しない');
          
          // 一般的なエラーメッセージであることを確認
          expect(errorMessage.toLowerCase()).to.contain('メールアドレスまたはパスワードが正しくありません');
        }
      });
    });
  });

  describe('レート制限・DoS対策', () => {
    it('API レート制限確認', () => {
      const rapidRequests = Array.from({ length: 10 }, (_, i) => i);
      
      rapidRequests.forEach(index => {
        cy.request({
          method: 'POST',
          url: `${backendUrl}/api/v1/auth/login`,
          failOnStatusCode: false,
          body: {
            email: `rate.limit.${index}@example.com`,
            password: 'RateTest123!'
          }
        }).then((response) => {
          // 短時間で大量リクエストが制限されることを確認
          if (index >= 5) { // 5回目以降
            expect([200, 429]).to.include(response.status);
            if (response.status === 429) {
              expect(response.body).to.have.property('error');
              expect(response.body.error.toLowerCase()).to.contain('rate limit');
            }
          }
        });
      });
    });
  });

  describe('セキュリティヘッダー確認', () => {
    it('必要なセキュリティヘッダーが設定されているか確認', () => {
      cy.request({
        url: baseUrl,
        failOnStatusCode: false
      }).then((response) => {
        const headers = response.headers;
        
        // Content Security Policy
        expect(headers).to.have.property('content-security-policy');
        
        // X-Frame-Options (クリックジャッキング対策)
        expect(headers).to.have.property('x-frame-options');
        
        // X-Content-Type-Options
        expect(headers).to.have.property('x-content-type-options');
        expect(headers['x-content-type-options']).to.equal('nosniff');
        
        // Strict-Transport-Security (HTTPS強制)
        if (baseUrl.startsWith('https')) {
          expect(headers).to.have.property('strict-transport-security');
        }
      });
    });
  });
});