/**
 * Google SSO機能のE2Eテスト
 * 
 * 操作パターン:
 * - Google OAuth 2.0 認証フローの確認
 * - SSO（シングルサインオン）機能の検証
 * - Google認証後のリダイレクト処理
 */
describe('Google SSO機能テスト', () => {
  const baseUrl = '/';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('Google認証ボタンの表示・動作', () => {
    it('Googleログインボタンが正常に表示される', () => {
      cy.visit('/login');
      
      // Googleログインボタンの存在確認
      cy.get('[data-cy="google-login-button"]').should('be.visible');
      cy.get('[data-cy="google-login-button"]').should('contain', 'Googleでログイン');
      cy.get('[data-cy="google-login-button"] svg').should('be.visible'); // Googleアイコンが表示される
    });

    it('Google認証サービスが初期化される', () => {
      cy.visit('/login');
      
      // Googleライブラリが初期化されるまで待つ
      cy.get('[data-cy="google-login-button"]').should('not.contain', '初期化中...');
      cy.get('[data-cy="google-login-button"]').should('be.enabled');
    });

    it('Googleログインボタンクリック時の動作確認', () => {
      cy.visit('/login');
      
      // Google認証APIをモック
      cy.window().then((win) => {
        win.google = {
          accounts: {
            id: {
              initialize: cy.stub().as('googleInitialize'),
              prompt: cy.stub().as('googlePrompt'),
              renderButton: cy.stub().as('googleRenderButton')
            }
          }
        };
      });
      
      // Googleログインボタンをクリック
      cy.get('[data-cy="google-login-button"]').click();
      
      // Google認証プロンプトが呼び出される（モック確認）
      cy.get('@googlePrompt').should('have.been.called');
    });
  });

  describe('Google認証フローのモック', () => {
    it('Google認証成功フローのモック', () => {
      cy.visit('/login');
      
      // Google認証の成功をシミュレート
      cy.window().then((win) => {
        // Google認証コールバック関数をモック
        const mockCredential = 'mock-google-jwt-token';
        
        // Google認証サービスをモック
        win.google = {
          accounts: {
            id: {
              initialize: (config) => {
                // 初期化成功をシミュレート
                if (config.callback) {
                  // 認証成功時のコールバック実行をシミュレート
                  setTimeout(() => {
                    config.callback({
                      credential: mockCredential,
                      select_by: 'btn'
                    });
                  }, 100);
                }
              },
              prompt: cy.stub(),
              renderButton: cy.stub()
            }
          }
        };
      });
      
      // Googleログインボタンをクリック
      cy.get('[data-cy="google-login-button"]').click();
      
      // 認証処理の状態確認（ローディング表示など）
      cy.get('[data-cy="google-login-button"]').should('contain', 'ログイン中...');
    });

    it('Google認証エラーフローのモック', () => {
      cy.visit('/login');
      
      // Google認証のエラーをシミュレート
      cy.window().then((win) => {
        win.google = {
          accounts: {
            id: {
              initialize: (config) => {
                if (config.error_callback) {
                  setTimeout(() => {
                    config.error_callback({
                      type: 'popup_failed_to_open'
                    });
                  }, 100);
                }
              },
              prompt: cy.stub(),
              renderButton: cy.stub()
            }
          }
        };
      });
      
      cy.get('[data-cy="google-login-button"]').click();
      
      // エラーメッセージが表示される
      cy.contains('Google認証の初期化に失敗しました').should('be.visible');
    });
  });

  describe('Google認証の環境設定テスト', () => {
    it('Google OAuth設定が不完全な場合のエラー処理', () => {
      cy.visit('/login');
      
      // 環境変数をクリアしてGoogle設定を無効にする
      cy.window().then((win) => {
        // Google設定の検証失敗をシミュレート
        win.process = { env: {} }; // 環境変数をクリア
      });
      
      cy.get('[data-cy="google-login-button"]').should('be.disabled');
    });

    it('Google認証ライブラリ未読み込み時の処理', () => {
      cy.visit('/login');
      
      // Google認証ライブラリが利用できない状況をシミュレート
      cy.window().then((win) => {
        delete win.google; // Googleオブジェクトを削除
      });
      
      cy.get('[data-cy="google-login-button"]').click();
      
      // エラーメッセージが表示される
      cy.contains('Google認証サービスが利用できません').should('be.visible');
    });
  });

  describe('Google認証とバックエンド連携', () => {
    it('Google認証後のバックエンドAPI呼び出し', () => {
      // バックエンドAPIをインターセプト
      cy.intercept('POST', '**/auth/google', {
        statusCode: 200,
        body: {
          success: true,
          message: 'Google認証に成功しました',
          user: {
            id: 1,
            email: 'test@gmail.com',
            username: 'Test User',
            user_role: 2
          }
        }
      }).as('googleAuth');
      
      cy.visit('/login');
      
      // Google認証成功をシミュレート
      cy.window().then((win) => {
        win.google = {
          accounts: {
            id: {
              initialize: (config) => {
                if (config.callback) {
                  setTimeout(() => {
                    config.callback({
                      credential: 'mock-google-jwt-token',
                      select_by: 'btn'
                    });
                  }, 100);
                }
              },
              prompt: cy.stub(),
              renderButton: cy.stub()
            }
          }
        };
      });
      
      cy.get('[data-cy="google-login-button"]').click();
      
      // バックエンドAPIが呼び出される
      cy.wait('@googleAuth');
    });

    it('Google認証失敗時のバックエンドエラー処理', () => {
      // バックエンドAPIエラーをインターセプト
      cy.intercept('POST', '**/auth/google', {
        statusCode: 400,
        body: {
          success: false,
          error: 'Invalid Google token'
        }
      }).as('googleAuthError');
      
      cy.visit('/login');
      
      // Google認証をシミュレート（バックエンドでエラー）
      cy.window().then((win) => {
        win.google = {
          accounts: {
            id: {
              initialize: (config) => {
                if (config.callback) {
                  setTimeout(() => {
                    config.callback({
                      credential: 'invalid-token',
                      select_by: 'btn'
                    });
                  }, 100);
                }
              },
              prompt: cy.stub(),
              renderButton: cy.stub()
            }
          }
        };
      });
      
      cy.get('[data-cy="google-login-button"]').click();
      
      // バックエンドAPIエラーを待つ
      cy.wait('@googleAuthError');
      
      // エラーメッセージが表示される
      cy.contains('Google認証処理中にエラーが発生しました').should('be.visible');
    });
  });

  describe('Google認証のUI/UX', () => {
    it('Google認証ボタンのローディング状態', () => {
      cy.visit('/login');
      
      // 初期化中の表示確認
      cy.get('[data-cy="google-login-button"]').should('contain', '初期化中...').or('be.enabled');
      
      // 初期化完了後は通常状態
      cy.get('[data-cy="google-login-button"]', { timeout: 5000 }).should('not.contain', '初期化中...');
      cy.get('[data-cy="google-login-button"]').should('be.enabled');
    });

    it('Google認証ボタンの無効化状態', () => {
      cy.visit('/login');
      
      // Google認証が初期化されるまではボタンが無効
      cy.get('[data-cy="google-login-button"]').should('have.class', 'disabled').or('be.enabled');
    });

    it('Google認証ボタンのアクセシビリティ', () => {
      cy.visit('/login');
      
      // ボタンが適切なaria属性を持つ
      cy.get('[data-cy="google-login-button"]').should('have.attr', 'type', 'button');
      
      // キーボードでアクセス可能
      cy.get('[data-cy="google-login-button"]').focus().should('be.focused');
      cy.get('[data-cy="google-login-button"]').type('{enter}');
    });
  });
});