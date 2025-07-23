/**
 * マイページ機能のE2Eテスト
 * 
 * 操作パターン:
 * - ユーザー情報表示の確認
 * - プロフィール編集機能の検証
 * - パスワード変更フローの確認
 */
describe('マイページ機能テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('マイページアクセス', () => {
    it('認証されたユーザーはマイページにアクセスできる', () => {
      cy.loginAsUser();
      cy.visit('/mypage');
      
      cy.get('[data-cy="mypage-title"]').should('be.visible').and('contain', 'マイページ');
      cy.url().should('include', '/mypage');
    });

    it('未認証ユーザーはマイページにアクセスできない', () => {
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });

    it('マイページに必要な要素が表示される', () => {
      cy.loginAsUser();
      cy.visit('/mypage');
      
      // 基本要素の確認
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      cy.contains('アカウント情報の管理とセキュリティ設定').should('be.visible');
      cy.contains('アカウント管理').should('be.visible');
      cy.get('[data-cy="logout-form-button"]').should('be.visible');
      cy.get('[data-cy="delete-account-button"]').should('be.visible');
    });
  });

  describe('プロフィール表示・編集', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('現在のユーザー情報が表示される', () => {
      // ユーザー情報の表示確認
      cy.contains('アカウント情報').should('be.visible');
      cy.contains('アカウントタイプ').should('be.visible');
      cy.contains('アカウント状態').should('be.visible');
      cy.contains('最終ログイン').should('be.visible');
    });

    it('プロフィール情報が正しく表示される', () => {
      // 基本情報の確認
      cy.contains('登録日').should('be.visible');
      cy.contains('認証方法').should('be.visible');
      
      // ユーザーロールの表示確認
      cy.contains('一般会員').should('be.visible').or(cy.contains('無料会員'));
      cy.contains('アクティブ').should('be.visible');
    });

    it('プロフィール編集が可能である', () => {
      // プロフィール更新APIをモック
      cy.intercept('POST', '**/mypage', {
        statusCode: 200,
        body: {
          success: 'プロフィールを更新しました。',
          type: 'updateProfile'
        }
      }).as('updateProfile');

      // プロフィール編集フォームがある場合のテスト
      // （実際の編集フォーム要素があれば以下を実行）
      if (cy.get('[data-cy="profile-edit-form"]').should('exist')) {
        cy.get('[data-cy="username-input"]').clear().type('Updated Username');
        cy.get('[data-cy="profile-save-button"]').click();
        cy.wait('@updateProfile');
        
        // 成功メッセージの確認
        cy.contains('プロフィールを更新しました').should('be.visible');
      }
    });
  });

  describe('セキュリティ設定', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('セキュリティ設定セクションが表示される', () => {
      cy.contains('セキュリティ設定').should('be.visible');
      cy.contains('パスワード').should('be.visible');
      cy.contains('ログインデバイス').should('be.visible');
    });

    it('パスワード変更リンクが動作する', () => {
      cy.contains('a', '変更する').should('have.attr', 'href').and('include', 'reset-password');
    });

    it('現在のデバイス情報が表示される', () => {
      cy.contains('現在のデバイス').should('be.visible');
      cy.contains('アクティブ').should('be.visible');
    });
  });

  describe('利用状況・統計情報', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('利用状況が表示される', () => {
      cy.contains('利用状況').should('be.visible');
      cy.contains('今月のログイン回数').should('be.visible');
      cy.contains('利用開始日からの日数').should('be.visible');
      cy.contains('アカウントレベル').should('be.visible');
    });

    it('統計情報が数値で表示される', () => {
      // 数値の表示確認（具体的な値は変動する可能性があるため、存在確認のみ）
      cy.get('.text-2xl.font-bold').should('have.length.greaterThan', 0);
    });
  });

  describe('アカウント管理機能', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('ログアウト機能が正常に動作する', () => {
      // ログアウトAPIをモック
      cy.intercept('POST', '**/mypage', {
        statusCode: 302,
        headers: {
          'Location': '/login'
        }
      }).as('logout');

      cy.get('[data-cy="logout-form-button"]').click();
      
      // ログアウト処理の確認
      cy.url().should('include', '/login', { timeout: 10000 });
    });

    it('アカウント削除の確認ダイアログが表示される', () => {
      // 確認ダイアログをスタブ
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(false).as('confirmDialog');
      });

      cy.get('[data-cy="delete-account-button"]').click();
      
      // 確認ダイアログが呼ばれる
      cy.get('@confirmDialog').should('have.been.calledWith', 
        '本当にアカウントを削除しますか？この操作は取り消せません。'
      );
    });

    it('アカウント削除をキャンセルできる', () => {
      // 確認ダイアログでキャンセル
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(false);
      });

      cy.get('[data-cy="delete-account-button"]').click();
      
      // マイページに残る
      cy.url().should('include', '/mypage');
    });

    it('アカウント削除を実行できる', () => {
      // 削除APIをモック
      cy.intercept('POST', '**/mypage', {
        statusCode: 302,
        headers: {
          'Location': '/login'
        }
      }).as('deleteAccount');

      // 確認ダイアログでOK
      cy.window().then((win) => {
        cy.stub(win, 'confirm').returns(true);
      });

      cy.get('[data-cy="delete-account-button"]').click();
      
      // 削除後ログインページにリダイレクト
      cy.url().should('include', '/login', { timeout: 10000 });
    });
  });

  describe('プレミアム機能案内（一般ユーザー）', () => {
    it('無料会員にはアップグレード案内が表示される', () => {
      cy.login('free@example.com', 'FreePass123!');
      cy.visit('/mypage');
      
      // プレミアム機能案内の確認
      cy.contains('プレミアム機能').should('be.visible');
      cy.contains('さらに高度な機能をご利用いただけます').should('be.visible');
      cy.get('[data-cy="upgrade-button"]').should('be.visible');
      
      // 機能一覧の確認
      cy.contains('高度な分析機能').should('be.visible');
      cy.contains('優先サポート').should('be.visible');
      cy.contains('容量無制限').should('be.visible');
    });

    it('管理者にはアップグレード案内が表示されない', () => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
      
      // プレミアム機能案内が非表示
      cy.get('[data-cy="upgrade-button"]').should('not.exist');
      cy.contains('プレミアム機能').should('not.exist');
    });

    it('アップグレードボタンが正常に動作する', () => {
      cy.login('free@example.com', 'FreePass123!');
      cy.visit('/mypage');
      
      cy.get('[data-cy="upgrade-button"]').should('be.enabled');
      cy.get('[data-cy="upgrade-button"]').click();
      
      // アップグレード処理の確認（具体的な動作は実装に依存）
    });
  });

  describe('マイページの応答性とアクセシビリティ', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('レスポンシブデザインが正常に動作する', () => {
      // デスクトップサイズ
      cy.viewport(1920, 1080);
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      
      // タブレットサイズ
      cy.viewport(768, 1024);
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      
      // モバイルサイズ
      cy.viewport(375, 667);
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });

    it('キーボードナビゲーションが可能', () => {
      // ログアウトボタンにフォーカス
      cy.get('[data-cy="logout-form-button"]').focus().should('be.focused');
      
      // Tab キーで次の要素に移動
      cy.get('[data-cy="logout-form-button"]').tab();
      cy.get('[data-cy="delete-account-button"]').should('be.focused');
    });

    it('適切なaria属性とセマンティックHTML', () => {
      // セクション見出しの確認
      cy.get('h1').should('exist');
      cy.get('h3').should('exist');
      
      // ボタン要素の確認
      cy.get('button').should('have.length.greaterThan', 0);
    });
  });

  describe('エラーハンドリング', () => {
    beforeEach(() => {
      cy.loginAsUser();
      cy.visit('/mypage');
    });

    it('APIエラー時のエラーメッセージ表示', () => {
      // エラーレスポンスをモック
      cy.intercept('POST', '**/mypage', {
        statusCode: 400,
        body: {
          error: 'サーバーエラーが発生しました',
          type: 'general'
        }
      }).as('serverError');

      // 何らかのアクション実行（プロフィール更新など）
      if (cy.get('[data-cy="profile-save-button"]').should('exist')) {
        cy.get('[data-cy="profile-save-button"]').click();
        cy.wait('@serverError');
        
        // エラーメッセージが表示される
        cy.contains('サーバーエラーが発生しました').should('be.visible');
      }
    });

    it('ネットワークエラー時の処理', () => {
      // ネットワークエラーをシミュレート
      cy.intercept('POST', '**/mypage', { forceNetworkError: true }).as('networkError');

      if (cy.get('[data-cy="logout-form-button"]').should('exist')) {
        cy.get('[data-cy="logout-form-button"]').click();
        
        // エラーハンドリングの確認（具体的な表示は実装に依存）
        cy.wait('@networkError');
      }
    });
  });
});