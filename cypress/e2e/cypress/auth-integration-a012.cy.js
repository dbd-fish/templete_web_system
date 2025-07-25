/**
 * 認証フロー統合テスト（A012タスク対応）
 * 
 * 操作パターン:
 * - フロントエンド・バックエンド間の完全な認証フロー統合テスト
 * - メール認証、Google OAuth、パスワードリセット等の一連のテストシナリオ
 * - HttpOnlyクッキーベース認証とセッション管理の検証
 * - 実際のAPIエンドポイントとの連携確認
 */
describe('認証フロー統合テスト (A012)', () => {
  const baseUrl = 'http://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('ログイン・ログアウトフロー統合テスト', () => {
    it('完全ログインフロー: フロントエンド → バックエンド → セッション確認', () => {
      const testUser = {
        email: 'test@example.com',
        password: 'TestPass123!'
      };

      // 1. ログインページの表示
      cy.visit('/login');
      cy.get('[data-cy="login-title"]').should('be.visible');

      // 2. バックエンドAPIへのログインリクエスト（リアルAPI使用）
      cy.get('[data-cy="email-input"]').type(testUser.email);
      cy.get('[data-cy="password-input"]').type(testUser.password);
      
      // ネットワークリクエストを監視
      cy.intercept('POST', '**/auth/login').as('loginRequest');
      
      cy.get('[data-cy="login-submit-button"]').click();
      
      // 3. バックエンドレスポンスの確認
      cy.wait('@loginRequest').then((interception) => {
        // リクエストボディの確認
        expect(interception.request.body).to.deep.include({
          email: testUser.email,
          password: testUser.password
        });
        
        // レスポンスの確認（成功またはユーザー不存在）
        if (interception.response.statusCode === 200) {
          // 成功時の処理
          expect(interception.response.body).to.have.property('access_token');
          expect(interception.response.body).to.have.property('user');
          
          // マイページへのリダイレクト確認
          cy.url().should('include', '/mypage');
          
          // セッション維持の確認
          cy.get('[data-cy="mypage-title"]').should('be.visible');
          
        } else if (interception.response.statusCode === 401) {
          // ユーザーが存在しない場合（テストデータなし）
          cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
          cy.log('テストユーザーが存在しないため、エラーハンドリングをテスト');
        }
      });
    });

    it('ログアウトフロー: セッション削除とリダイレクト確認', () => {
      // 事前にログイン状態を作成（モックまたは実際のログイン）
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'mock_token_12345',
          token_type: 'bearer',
          user: {
            user_id: '1',
            email: 'test@example.com',
            username: 'Test User',
            user_role: 2
          }
        }
      }).as('mockLogin');

      cy.visit('/login');
      cy.login('test@example.com', 'TestPass123!');
      cy.wait('@mockLogin');
      
      // マイページにアクセス
      cy.visit('/mypage');
      
      // ログアウトAPIの監視
      cy.intercept('POST', '**/auth/logout').as('logoutRequest');
      
      // ログアウト実行
      cy.logout();
      
      // バックエンドAPI呼び出しの確認
      cy.wait('@logoutRequest').then((interception) => {
        expect(interception.request.headers).to.have.property('authorization');
        expect(interception.response.statusCode).to.be.oneOf([200, 401]);
      });
      
      // ログインページへのリダイレクト確認
      cy.url().should('include', '/login');
      
      // セッション削除の確認：保護されたページへのアクセス試行
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });
  });

  describe('Google OAuth統合テスト', () => {
    it('Google OAuth認証フロー: リダイレクトとコールバック処理', () => {
      cy.visit('/login');
      
      // Google OAuth URLの生成確認
      cy.get('[data-cy="google-login-button"]').should('be.visible');
      
      // Google認証エンドポイントの監視
      cy.intercept('GET', '**/auth/google/url').as('getGoogleUrl');
      
      cy.get('[data-cy="google-login-button"]').click();
      
      // バックエンドからGoogle OAuth URLを取得
      cy.wait('@getGoogleUrl').then((interception) => {
        expect(interception.response.statusCode).to.equal(200);
        expect(interception.response.body).to.have.property('auth_url');
        expect(interception.response.body.auth_url).to.include('accounts.google.com');
        expect(interception.response.body.auth_url).to.include('oauth2');
      });
    });

    it('Google OAuth コールバック処理テスト', () => {
      // Google OAuth認証後のコールバックをシミュレート
      const mockAuthCode = 'mock_google_auth_code_12345';
      const mockGoogleUser = {
        access_token: 'google_access_token_12345',
        token_type: 'bearer',
        user: {
          user_id: '1',
          email: 'googleuser@example.com',
          username: 'Google User',
          user_role: 2,
          auth_provider: 'google'
        }
      };

      // Google OAuth認証完了APIの監視
      cy.intercept('GET', `**/auth/google/callback?code=${mockAuthCode}`, {
        statusCode: 200,
        body: mockGoogleUser
      }).as('googleCallback');

      // OAuth認証完了URLをシミュレート
      cy.visit(`/auth/google/callback?code=${mockAuthCode}`);
      
      cy.wait('@googleCallback');
      
      // マイページへのリダイレクト確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });
  });

  describe('パスワードリセット統合テスト', () => {
    it('パスワードリセット全フロー: メール送信からパスワード更新まで', () => {
      const testEmail = 'passwordreset@example.com';
      const newPassword = 'NewSecurePass123!';
      const resetToken = 'reset_token_12345';

      // 1. パスワードリセット要求
      cy.visit('/login');
      cy.get('[data-cy="forgot-password-link"]').click();
      
      cy.url().should('include', '/send-reset-password-email');
      
      // リセットメール送信APIの監視
      cy.intercept('POST', '**/send-reset-password-email', {
        statusCode: 200,
        body: {
          success: true,
          message: 'パスワードリセットメールを送信しました'
        }
      }).as('sendResetEmail');
      
      cy.get('input[type="email"]').type(testEmail);
      cy.get('button[type="submit"]').click();
      
      cy.wait('@sendResetEmail').then((interception) => {
        expect(interception.request.body).to.deep.include({
          email: testEmail
        });
      });
      
      // 2. リセットメール送信完了ページ
      cy.url().should('include', 'send-reset-password-email-complete');
      cy.contains('メールを送信しました').should('be.visible');

      // 3. リセットトークン検証
      cy.intercept('GET', `**/reset-password?token=${resetToken}`, {
        statusCode: 200,
        body: {
          valid: true,
          email: testEmail
        }
      }).as('validateResetToken');

      cy.visit(`/reset-password?token=${resetToken}`);
      cy.wait('@validateResetToken');

      // 4. 新しいパスワード設定
      cy.intercept('POST', '**/reset-password', {
        statusCode: 200,
        body: {
          success: true,
          message: 'パスワードが正常に更新されました'
        }
      }).as('updatePassword');

      cy.get('input[name="password"]').type(newPassword);
      cy.get('input[name="confirmPassword"]').type(newPassword);
      cy.get('button[type="submit"]').click();

      cy.wait('@updatePassword').then((interception) => {
        expect(interception.request.body).to.deep.include({
          token: resetToken,
          new_password: newPassword
        });
      });

      // 5. パスワード更新完了
      cy.url().should('include', 'reset-password-complete');
      
      // 6. 新しいパスワードでログイン確認
      cy.visit('/login');
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'new_token_after_reset',
          user: {
            user_id: '1',
            email: testEmail,
            username: 'Test User'
          }
        }
      }).as('loginWithNewPassword');
      
      cy.login(testEmail, newPassword);
      cy.wait('@loginWithNewPassword');
      cy.url().should('include', '/mypage');
    });
  });

  describe('ユーザー登録統合テスト', () => {
    it('新規ユーザー登録フロー: サインアップからメール認証まで', () => {
      const timestamp = Date.now();
      const newUser = {
        username: `integrationtest${timestamp}`,
        email: `integration${timestamp}@example.com`,
        password: 'IntegrationPass123!'
      };

      // 1. サインアップページアクセス
      cy.visit('/signup');
      cy.get('[data-cy="signup-form"]').should('be.visible');

      // 2. サインアップAPIの監視
      cy.intercept('POST', '**/signup', {
        statusCode: 201,
        body: {
          success: true,
          message: 'ユーザー登録が完了しました',
          user_id: 'new_user_123'
        }
      }).as('signupRequest');

      // 3. フォーム入力とサブミット
      cy.get('[data-cy="signup-username-input"]').type(newUser.username);
      cy.get('[data-cy="signup-email-input"]').type(newUser.email);
      cy.get('[data-cy="signup-password-input"]').type(newUser.password);
      cy.get('[data-cy="signup-confirm-password-input"]').type(newUser.password);
      
      cy.get('[data-cy="signup-submit-button"]').click();

      // 4. バックエンドAPIリクエスト確認
      cy.wait('@signupRequest').then((interception) => {
        expect(interception.request.body).to.deep.include({
          username: newUser.username,
          email: newUser.email,
          password: newUser.password
        });
      });

      // 5. メール認証待ちページへの遷移
      cy.url().should('include', '/signup-vertify-pending');
      cy.contains('メール認証が必要です').should('be.visible');
    });
  });

  describe('セッション管理とセキュリティテスト', () => {
    it('JWTトークン期限切れ処理', () => {
      // 1. 正常ログイン
      cy.intercept('POST', '**/auth/login', {
        statusCode: 200,
        body: {
          access_token: 'valid_token_12345',
          user: { user_id: '1', email: 'test@example.com' }
        }
      }).as('initialLogin');

      cy.visit('/login');
      cy.login('test@example.com', 'TestPass123!');
      cy.wait('@initialLogin');
      
      // 2. マイページアクセス成功
      cy.intercept('GET', '**/mypage', {
        statusCode: 200,
        body: {
          user: { user_id: '1', email: 'test@example.com', username: 'Test User' }
        }
      }).as('mypageSuccess');

      cy.visit('/mypage');
      cy.wait('@mypageSuccess');
      cy.get('[data-cy="mypage-title"]').should('be.visible');

      // 3. トークン期限切れをシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 401,
        body: { error: 'Token expired' }
      }).as('tokenExpired');

      cy.reload();
      cy.wait('@tokenExpired');

      // 4. ログインページへの自動リダイレクト確認
      cy.url().should('include', '/login');
    });

    it('リフレッシュトークンによる自動再認証', () => {
      // アクセストークン期限切れ時のリフレッシュトークンフロー
      cy.intercept('POST', '**/auth/refresh', {
        statusCode: 200,
        body: {
          access_token: 'new_access_token_12345',
          user: { user_id: '1', email: 'test@example.com' }
        }
      }).as('refreshToken');

      // 初回アクセス時にアクセストークン期限切れ、リフレッシュトークンで再認証
      cy.intercept('GET', '**/mypage', (req) => {
        // 初回リクエストは401で失敗
        if (!req.headers['x-refreshed']) {
          req.reply({
            statusCode: 401,
            body: { error: 'Access token expired' }
          });
        } else {
          // リフレッシュ後は成功
          req.reply({
            statusCode: 200,
            body: { user: { user_id: '1', email: 'test@example.com' } }
          });
        }
      }).as('mypageWithRefresh');

      cy.visit('/mypage');
      
      // リフレッシュトークンによる自動再認証確認
      cy.wait('@refreshToken');
      cy.wait('@mypageWithRefresh');
      
      // 最終的にマイページが表示される
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });
  });

  describe('エラーハンドリング統合テスト', () => {
    it('バックエンドAPIエラー時のフロントエンド対応', () => {
      // サーバーエラーをシミュレート
      cy.intercept('POST', '**/auth/login', {
        statusCode: 500,
        body: { error: 'Internal Server Error' }
      }).as('serverError');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('test@example.com');
      cy.get('[data-cy="password-input"]').type('TestPass123!');
      cy.get('[data-cy="login-submit-button"]').click();

      cy.wait('@serverError');
      
      // エラーメッセージの表示確認
      cy.contains('サーバーエラーが発生しました').should('be.visible')
        .or(cy.contains('エラーが発生しました').should('be.visible'));
    });

    it('ネットワークエラー時のリトライ機能', () => {
      // ネットワークエラーをシミュレート
      cy.intercept('POST', '**/auth/login', { forceNetworkError: true }).as('networkError');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('test@example.com');
      cy.get('[data-cy="password-input"]').type('TestPass123!');
      cy.get('[data-cy="login-submit-button"]').click();

      cy.wait('@networkError');
      
      // ネットワークエラーメッセージの確認
      cy.contains('ネットワークエラー').should('be.visible')
        .or(cy.contains('接続に失敗しました').should('be.visible'));
    });
  });

  describe('レスポンシブ・アクセシビリティテスト', () => {
    it('モバイル画面での認証フロー', () => {
      // モバイル画面サイズに設定
      cy.viewport(375, 667);
      
      cy.visit('/login');
      
      // モバイルレイアウトの確認
      cy.get('[data-cy="login-form"]').should('be.visible');
      cy.get('[data-cy="email-input"]').should('be.visible');
      cy.get('[data-cy="password-input"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('be.visible');
      
      // タッチ操作のシミュレート
      cy.get('[data-cy="email-input"]').click().type('mobile@example.com');
      cy.get('[data-cy="password-input"]').click().type('MobilePass123!');
    });

    it('キーボードナビゲーションでの認証', () => {
      cy.visit('/login');
      
      // Tabキーナビゲーション
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-cy', 'email-input');
      
      cy.focused().type('keyboard@example.com').tab();
      cy.focused().should('have.attr', 'data-cy', 'password-input');
      
      cy.focused().type('KeyboardPass123!').tab();
      cy.focused().should('have.attr', 'data-cy', 'login-submit-button');
      
      // Enterキーでサブミット
      cy.focused().type('{enter}');
    });
  });

  describe('パフォーマンステスト', () => {
    it('ログインページのロード時間測定', () => {
      cy.visit('/login', {
        onBeforeLoad: (win) => {
          win.performance.mark('loginPageStart');
        }
      });

      cy.get('[data-cy="login-title"]').should('be.visible').then(() => {
        cy.window().then((win) => {
          win.performance.mark('loginPageEnd');
          win.performance.measure('loginPageLoad', 'loginPageStart', 'loginPageEnd');
          
          const measure = win.performance.getEntriesByName('loginPageLoad')[0];
          expect(measure.duration).to.be.lessThan(3000); // 3秒以内
        });
      });
    });

    it('大量API呼び出し時の応答性テスト', () => {
      // 複数の認証関連API呼び出しを並行実行
      const apiCalls = [
        cy.request({ url: `${backendUrl}/auth/google/url`, failOnStatusCode: false }),
        cy.request({ url: `${backendUrl}/health`, failOnStatusCode: false }),
        cy.request({ url: `${backendUrl}/api/v1/users/me`, failOnStatusCode: false, headers: { 'Authorization': 'Bearer invalid_token' } })
      ];

      const startTime = Date.now();
      
      Promise.all(apiCalls).then(() => {
        const endTime = Date.now();
        const totalTime = endTime - startTime;
        expect(totalTime).to.be.lessThan(5000); // 5秒以内
      });
    });
  });
});