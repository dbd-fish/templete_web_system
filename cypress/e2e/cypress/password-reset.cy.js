/**
 * パスワードリセット機能のE2Eテスト
 * 
 * 操作パターン:
 * - パスワードリセット申請フローの確認
 * - メール認証を使ったリセット処理の検証
 * - 新パスワード設定後のログイン確認
 */
describe('パスワードリセット機能テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('パスワードリセット要求', () => {
    it('パスワードリセット要求ページが正常に表示される', () => {
      cy.visit('/send-reset-password-email');
      
      // ページの基本要素確認
      cy.contains('パスワードリセット').should('be.visible');
      cy.get('input[type="email"]').should('be.visible');
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('ログインページからパスワードリセットリンクでアクセスできる', () => {
      cy.visit('/login');
      cy.get('[data-cy="forgot-password-link"]').click();
      
      cy.url().should('include', '/send-reset-password-email');
      cy.contains('パスワードリセット').should('be.visible');
    });

    it('有効なメールアドレスでリセット要求を送信できる', () => {
      // パスワードリセット要求APIをモック
      cy.intercept('POST', '**/send-reset-password-email', {
        statusCode: 200,
        body: {
          success: true,
          message: 'パスワードリセット用のメールを送信しました'
        }
      }).as('resetPasswordRequest');

      cy.visit('/send-reset-password-email');
      
      cy.get('input[type="email"]').type('test@example.com');
      cy.get('button[type="submit"]').click();
      
      cy.wait('@resetPasswordRequest');
      
      // 成功ページまたはメッセージの表示
      cy.url().should('include', 'send-reset-password-email-complete').or(cy.contains('メールを送信しました'));
    });

    it('無効なメールアドレスでエラーが表示される', () => {
      // 無効なメールアドレスに対するエラーレスポンス
      cy.intercept('POST', '**/send-reset-password-email', {
        statusCode: 400,
        body: {
          error: '該当するメールアドレスが見つかりません'
        }
      }).as('resetPasswordError');

      cy.visit('/send-reset-password-email');
      
      cy.get('input[type="email"]').type('nonexistent@example.com');
      cy.get('button[type="submit"]').click();
      
      cy.wait('@resetPasswordError');
      
      // エラーメッセージの表示確認
      cy.contains('該当するメールアドレスが見つかりません').should('be.visible');
    });

    it('メール形式のバリデーションが働く', () => {
      cy.visit('/send-reset-password-email');
      
      // 無効なメール形式を入力
      cy.get('input[type="email"]').type('invalid-email');
      cy.get('button[type="submit"]').click();
      
      // HTML5バリデーションメッセージの確認
      cy.get('input[type="email"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
    });
  });

  describe('パスワードリセット完了（トークンベース）', () => {
    it('有効なトークンでリセットページにアクセスできる', () => {
      const validToken = 'valid-reset-token-123';
      
      // トークン検証APIをモック
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 200,
        body: {
          valid: true,
          email: 'test@example.com'
        }
      }).as('tokenValidation');

      cy.visit(`/reset-password?token=${validToken}`);
      
      cy.wait('@tokenValidation');
      
      // パスワードリセットフォームが表示される
      cy.get('input[type="password"]').should('have.length', 2); // パスワードと確認パスワード
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('無効なトークンでエラーページが表示される', () => {
      const invalidToken = 'invalid-token';
      
      // 無効なトークンのレスポンス
      cy.intercept('GET', `**/reset-password?token=${invalidToken}`, {
        statusCode: 400,
        body: {
          error: 'トークンが無効または期限切れです'
        }
      }).as('invalidToken');

      cy.visit(`/reset-password?token=${invalidToken}`);
      
      cy.wait('@invalidToken');
      
      // エラーメッセージの表示
      cy.contains('トークンが無効または期限切れです').should('be.visible');
    });

    it('パスワードリセットが正常に完了する', () => {
      const validToken = 'valid-reset-token-123';
      
      // トークン検証とパスワード更新APIをモック
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 200,
        body: { valid: true, email: 'test@example.com' }
      }).as('tokenValidation');
      
      cy.intercept('POST', '**/reset-password', {
        statusCode: 200,
        body: {
          success: true,
          message: 'パスワードが正常に更新されました'
        }
      }).as('passwordReset');

      cy.visit(`/reset-password?token=${validToken}`);
      cy.wait('@tokenValidation');
      
      // 新しいパスワードを入力
      const newPassword = 'NewPassword123!';
      cy.get('input[name="password"]').type(newPassword);
      cy.get('input[name="confirmPassword"]').type(newPassword);
      cy.get('button[type="submit"]').click();
      
      cy.wait('@passwordReset');
      
      // 成功ページにリダイレクト
      cy.url().should('include', 'reset-password-complete').or(cy.contains('パスワードが正常に更新されました'));
    });

    it('パスワード確認が一致しない場合エラーが表示される', () => {
      const validToken = 'valid-reset-token-123';
      
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 200,
        body: { valid: true, email: 'test@example.com' }
      });

      cy.visit(`/reset-password?token=${validToken}`);
      
      // 異なるパスワードを入力
      cy.get('input[name="password"]').type('NewPassword123!');
      cy.get('input[name="confirmPassword"]').type('DifferentPassword123!');
      
      // バリデーションエラーの表示
      cy.contains('パスワードが一致しません').should('be.visible');
    });

    it('弱いパスワードに対するバリデーション', () => {
      const validToken = 'valid-reset-token-123';
      
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 200,
        body: { valid: true, email: 'test@example.com' }
      });

      cy.visit(`/reset-password?token=${validToken}`);
      
      // 弱いパスワードを入力
      cy.get('input[name="password"]').type('weak');
      cy.get('input[name="confirmPassword"]').click();
      
      // パスワード強度のバリデーションエラー
      cy.contains('パスワードが条件を満たしていません').should('be.visible');
    });
  });

  describe('パスワードリセット完了ページ', () => {
    it('リセット完了ページが正常に表示される', () => {
      cy.visit('/reset-password-complete');
      
      // 完了メッセージの表示確認
      cy.contains('パスワードが正常に更新されました').should('be.visible').or(cy.contains('パスワードリセット完了'));
      
      // ログインページへのリンクがある
      cy.contains('ログインページ').should('be.visible').or(cy.get('a[href="/login"]'));
    });

    it('リセット完了後にログインページに遷移できる', () => {
      cy.visit('/reset-password-complete');
      
      // ログインリンクをクリック
      cy.contains('a', 'ログイン').click().or(cy.get('a[href="/login"]').click());
      
      cy.url().should('include', '/login');
    });
  });

  describe('パスワードリセット後の認証テスト', () => {
    it('新しいパスワードでログインできる', () => {
      // パスワードリセット完了をシミュレート
      cy.visit('/login');
      
      // 新しいパスワードでログイン試行
      cy.get('[data-cy="email-input"]').type('test@example.com');
      cy.get('[data-cy="password-input"]').type('NewPassword123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功（モックデータに依存）
      cy.url().should('not.include', '/login');
    });

    it('古いパスワードではログインできない', () => {
      cy.visit('/login');
      
      // 古いパスワードでログイン試行
      cy.get('[data-cy="email-input"]').type('test@example.com');
      cy.get('[data-cy="password-input"]').type('OldPassword123!');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン失敗
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
    });
  });

  describe('セキュリティテスト', () => {
    it('期限切れトークンの処理', () => {
      const expiredToken = 'expired-token';
      
      // 期限切れトークンのレスポンス
      cy.intercept('GET', `**/reset-password?token=${expiredToken}`, {
        statusCode: 400,
        body: {
          error: 'リセットトークンの有効期限が切れています'
        }
      });

      cy.visit(`/reset-password?token=${expiredToken}`);
      
      // エラーメッセージの表示
      cy.contains('リセットトークンの有効期限が切れています').should('be.visible');
    });

    it('使用済みトークンの処理', () => {
      const usedToken = 'used-token';
      
      // 使用済みトークンのレスポンス
      cy.intercept('GET', `**/reset-password?token=${usedToken}`, {
        statusCode: 400,
        body: {
          error: 'このリセットトークンは既に使用されています'
        }
      });

      cy.visit(`/reset-password?token=${usedToken}`);
      
      // エラーメッセージの表示
      cy.contains('このリセットトークンは既に使用されています').should('be.visible');
    });

    it('トークンなしでのリセットページアクセス', () => {
      cy.visit('/reset-password');
      
      // トークンが必要である旨のメッセージまたはエラーページ
      cy.contains('無効なリクエストです').should('be.visible').or(cy.url().should('include', '/login'));
    });

    it('同一トークンの複数回使用防止', () => {
      const validToken = 'valid-token-once';
      
      // 1回目の使用
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 200,
        body: { valid: true, email: 'test@example.com' }
      });
      
      cy.intercept('POST', '**/reset-password', {
        statusCode: 200,
        body: { success: true, message: 'パスワードが更新されました' }
      });

      cy.visit(`/reset-password?token=${validToken}`);
      cy.get('input[name="password"]').type('NewPassword123!');
      cy.get('input[name="confirmPassword"]').type('NewPassword123!');
      cy.get('button[type="submit"]').click();
      
      // 2回目の使用試行
      cy.intercept('GET', `**/reset-password?token=${validToken}`, {
        statusCode: 400,
        body: { error: 'このトークンは既に使用されています' }
      });

      cy.visit(`/reset-password?token=${validToken}`);
      cy.contains('このトークンは既に使用されています').should('be.visible');
    });
  });

  describe('ユーザビリティテスト', () => {
    it('リセット要求の送信完了ページで適切な案内が表示される', () => {
      cy.visit('/send-reset-password-email-complete');
      
      // 適切な案内メッセージ
      cy.contains('メールを送信しました').should('be.visible');
      cy.contains('メールボックスを確認してください').should('be.visible');
    });

    it('パスワード強度の案内が表示される', () => {
      cy.visit('/reset-password?token=valid-token');
      
      // パスワード要件の案内
      cy.contains('8文字以上').should('be.visible').or(cy.contains('パスワードの条件'));
      cy.contains('大文字・小文字').should('be.visible').or(cy.contains('英数字'));
    });

    it('フォームの必須項目バリデーション', () => {
      cy.visit('/send-reset-password-email');
      
      // 空のまま送信
      cy.get('button[type="submit"]').click();
      
      // 必須項目のバリデーション
      cy.get('input[type="email"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
    });
  });

  describe('レスポンシブデザイン', () => {
    const pages = [
      '/send-reset-password-email',
      '/reset-password?token=valid-token',
      '/reset-password-complete'
    ];

    pages.forEach(page => {
      it(`${page} がモバイルで正常に表示される`, () => {
        cy.viewport(375, 667);
        cy.visit(page);
        
        // 基本的な表示確認
        cy.get('body').should('be.visible');
      });
    });
  });
});