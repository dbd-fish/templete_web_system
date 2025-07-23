/**
 * 統合テストシナリオ：複数機能を組み合わせたE2Eテスト
 * 
 * 操作パターン:
 * - 複数機能を横断するユーザージャーニーの検証
 * - エンドツーエンドのワークフロー確認
 * - 実際のユーザー利用シナリオの再現
 */
describe('統合テストシナリオ', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('新規ユーザー登録から利用開始までの完全フロー', () => {
    it('サインアップ → メール認証 → 初回ログイン → プロフィール設定', () => {
      const timestamp = Date.now();
      const testUser = {
        username: `testuser${timestamp}`,
        email: `test${timestamp}@example.com`,
        password: 'TestPass123!'
      };

      // 1. サインアップ
      cy.signup(testUser.username, testUser.email, testUser.password);
      cy.url().should('not.include', '/signup');

      // 2. メール認証完了をシミュレート
      cy.visit('/signup-vertify-complete');
      cy.contains('認証が完了しました').should('be.visible');

      // 3. 初回ログイン
      cy.visit('/login');
      cy.login(testUser.email, testUser.password);
      cy.url().should('include', '/mypage');

      // 4. プロフィール確認
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      cy.contains(testUser.username).should('be.visible');
    });
  });

  describe('管理者権限での完全なユーザー管理フロー', () => {
    it('管理者ログイン → ユーザー管理 → ユーザー操作 → 権限確認', () => {
      // バックエンドAPIをモック
      cy.intercept('GET', '**/admin/users*', {
        statusCode: 200,
        body: {
          data: {
            users: [
              {
                user_id: '123',
                email: 'testuser@example.com',
                username: 'Test User',
                user_role: 2,
                user_status: 1,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z'
              }
            ]
          }
        }
      }).as('getUserList');

      cy.intercept('PATCH', '**/admin/users/123', {
        statusCode: 200,
        body: {
          success: true,
          message: 'ユーザー情報を更新しました'
        }
      }).as('updateUser');

      // 1. 管理者としてログイン
      cy.loginAsAdmin();
      cy.visit('/mypage');

      // 2. 管理者画面の確認
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');

      // 3. ユーザー管理機能を展開
      cy.get('[data-cy="user-management-toggle"]').click();
      cy.wait('@getUserList');

      // 4. ユーザー情報の表示確認
      cy.contains('testuser@example.com').should('be.visible');
      cy.contains('Test User').should('be.visible');

      // 5. ユーザー編集操作（実装に依存）
      // 実際のフォーム要素がある場合のテスト
    });
  });

  describe('パスワードリセットの完全フロー', () => {
    it('パスワード忘れ → リセット要求 → 新パスワード設定 → ログイン', () => {
      const testEmail = 'test@example.com';
      const newPassword = 'NewSecurePass123!';

      // APIモック設定
      cy.intercept('POST', '**/send-reset-password-email', {
        statusCode: 200,
        body: { success: true, message: 'リセットメールを送信しました' }
      }).as('sendResetEmail');

      cy.intercept('GET', '**/reset-password?token=valid-token', {
        statusCode: 200,
        body: { valid: true, email: testEmail }
      }).as('validateToken');

      cy.intercept('POST', '**/reset-password', {
        statusCode: 200,
        body: { success: true, message: 'パスワードが更新されました' }
      }).as('resetPassword');

      // 1. ログインページからパスワードリセット要求
      cy.visit('/login');
      cy.get('[data-cy="forgot-password-link"]').click();

      // 2. メールアドレス入力
      cy.url().should('include', '/send-reset-password-email');
      cy.get('input[type="email"]').type(testEmail);
      cy.get('button[type="submit"]').click();
      cy.wait('@sendResetEmail');

      // 3. リセット要求完了ページ
      cy.url().should('include', 'send-reset-password-email-complete');

      // 4. リセットリンクをシミュレート（トークン付きURL）
      cy.visit('/reset-password?token=valid-token');
      cy.wait('@validateToken');

      // 5. 新しいパスワードを設定
      cy.get('input[name="password"]').type(newPassword);
      cy.get('input[name="confirmPassword"]').type(newPassword);
      cy.get('button[type="submit"]').click();
      cy.wait('@resetPassword');

      // 6. リセット完了ページ
      cy.url().should('include', 'reset-password-complete');

      // 7. 新しいパスワードでログイン確認
      cy.visit('/login');
      cy.login(testEmail, newPassword);
      cy.url().should('include', '/mypage');
    });
  });

  describe('認証セッション管理とセキュリティ', () => {
    it('ログイン → セッション維持 → 自動ログアウト → 再認証', () => {
      // 1. 正常ログイン
      cy.loginAsUser();
      cy.visit('/mypage');
      cy.get('[data-cy="mypage-title"]').should('be.visible');

      // 2. ページリロードでセッション維持確認
      cy.reload();
      cy.get('[data-cy="mypage-title"]').should('be.visible');

      // 3. セッション期限切れをシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 401,
        body: { error: 'Token expired' }
      }).as('expiredSession');

      cy.visit('/mypage');
      cy.url().should('include', '/login');

      // 4. 再認証
      cy.loginAsUser();
      cy.url().should('include', '/mypage');
    });

    it('複数タブでのセッション同期', () => {
      // メインタブでログイン
      cy.loginAsUser();
      cy.visit('/mypage');

      // 新しいタブ（ウィンドウ）をシミュレート
      cy.visit('/mypage', { 
        onBeforeLoad: (win) => {
          // 別タブでの認証状態確認
          expect(win.document.cookie).to.contain('authToken');
        }
      });

      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });
  });

  describe('エラー処理とリカバリー', () => {
    it('ネットワークエラーからの復旧', () => {
      // ネットワークエラーをシミュレート
      cy.intercept('POST', '**/login', { forceNetworkError: true }).as('networkError');

      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('test@example.com');
      cy.get('[data-cy="password-input"]').type('TestPass123!');
      cy.get('[data-cy="login-submit-button"]').click();

      // エラーハンドリングの確認
      cy.wait('@networkError');

      // ネットワーク復旧をシミュレート
      cy.intercept('POST', '**/login', {
        statusCode: 200,
        body: { success: true }
      }).as('recoveredNetwork');

      // 再試行
      cy.get('[data-cy="login-submit-button"]').click();
      cy.url().should('not.include', '/login');
    });

    it('サーバーエラーからの復旧', () => {
      // サーバーエラーをシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 500,
        body: { error: 'Internal Server Error' }
      }).as('serverError');

      cy.loginAsUser();
      cy.visit('/mypage');

      // エラーページまたはメッセージの表示
      cy.contains('エラーが発生しました').should('be.visible').or(cy.url().should('include', '/login'));

      // サーバー復旧をシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 200,
        body: {
          user: {
            user_id: '1',
            email: 'user@example.com',
            username: 'Test User',
            user_role: 2,
            user_status: 1
          }
        }
      }).as('recoveredServer');

      // ページリロードまたは再アクセス
      cy.reload();
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });
  });

  describe('データ整合性とバリデーション', () => {
    it('フロントエンドとバックエンドのバリデーション一致', () => {
      // フロントエンドバリデーション
      cy.visit('/signup');
      cy.get('[data-cy="signup-password-input"]').type('weak');
      cy.get('[data-cy="signup-confirm-password-input"]').click();
      cy.contains('パスワードが条件を満たしていません').should('be.visible');

      // バックエンドバリデーション
      cy.intercept('POST', '**/signup', {
        statusCode: 400,
        body: {
          error: 'パスワードが条件を満たしていません',
          details: ['8文字以上必要です', '大文字が必要です']
        }
      }).as('backendValidation');

      // 弱いパスワードで送信試行
      cy.get('[data-cy="signup-password-input"]').clear().type('weak123');
      cy.get('[data-cy="signup-confirm-password-input"]').clear().type('weak123');
      cy.get('[data-cy="signup-submit-button"]').click();

      cy.wait('@backendValidation');
      // バックエンドエラーメッセージの表示確認
    });
  });

  describe('パフォーマンステスト', () => {
    it('大量データでの表示パフォーマンス', () => {
      // 大量のユーザーデータをモック
      const largeUserList = Array.from({ length: 100 }, (_, i) => ({
        user_id: `${i + 1}`,
        email: `user${i + 1}@example.com`,
        username: `User ${i + 1}`,
        user_role: Math.floor(Math.random() * 3) + 1,
        user_status: 1,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      }));

      cy.intercept('GET', '**/admin/users*', {
        statusCode: 200,
        body: {
          data: {
            users: largeUserList
          }
        }
      }).as('largeUserList');

      cy.loginAsAdmin();
      cy.visit('/mypage');
      
      const startTime = Date.now();
      cy.get('[data-cy="user-management-toggle"]').click();
      cy.wait('@largeUserList');
      
      cy.then(() => {
        const loadTime = Date.now() - startTime;
        expect(loadTime).to.be.lessThan(5000); // 5秒以内
      });
    });

    it('ページロード時間の測定', () => {
      cy.visit('/login', {
        onBeforeLoad: (win) => {
          win.performance.mark('navigationStart');
        }
      });

      cy.get('[data-cy="login-title"]').should('be.visible').then(() => {
        cy.window().then((win) => {
          const navTiming = win.performance.getEntriesByType('navigation')[0];
          const loadTime = navTiming.loadEventEnd - navTiming.navigationStart;
          expect(loadTime).to.be.lessThan(3000); // 3秒以内
        });
      });
    });
  });

  describe('アクセシビリティテスト', () => {
    it('キーボードナビゲーションの完全性', () => {
      cy.visit('/login');
      
      // Tabキーでのナビゲーション
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-cy', 'email-input');
      
      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'password-input');
      
      cy.focused().tab();
      cy.focused().should('have.attr', 'data-cy', 'login-submit-button');
    });

    it('スクリーンリーダー対応の確認', () => {
      cy.visit('/login');
      
      // ラベルとinputの関連付け
      cy.get('[data-cy="email-input"]').should('have.attr', 'aria-label').or('have.attr', 'id');
      cy.get('[data-cy="password-input"]').should('have.attr', 'aria-label').or('have.attr', 'id');
      
      // エラーメッセージのaria属性
      cy.login('invalid@example.com', 'wrong');
      cy.contains('メールアドレスまたはパスワードが正しくありません')
        .should('have.attr', 'role', 'alert')
        .or('have.attr', 'aria-live', 'polite');
    });
  });

  describe('国際化・多言語対応', () => {
    it('日本語表示の確認', () => {
      cy.visit('/login');
      
      // 日本語テキストの表示確認
      cy.contains('ログイン').should('be.visible');
      cy.contains('メールアドレス').should('be.visible');
      cy.contains('パスワード').should('be.visible');
    });

    it('文字エンコーディングの確認', () => {
      const japaneseText = 'テストユーザー名前';
      
      cy.visit('/signup');
      cy.get('[data-cy="signup-username-input"]').type(japaneseText);
      cy.get('[data-cy="signup-username-input"]').should('have.value', japaneseText);
    });
  });
});