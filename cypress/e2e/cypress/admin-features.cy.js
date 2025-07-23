/**
 * 管理者権限機能のE2Eテスト
 * 
 * 操作パターン:
 * - 管理者アカウントでのログイン確認
 * - 管理者専用ページへのアクセス検証
 * - 一般ユーザーでのアクセス制限確認
 */
describe('管理者権限機能テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('管理者ログインと権限確認', () => {
    it('管理者としてログインできる', () => {
      cy.loginAsAdmin();
      cy.url().should('include', '/mypage');
    });

    it('管理者マイページが正常に表示される', () => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
      
      // 管理者専用の要素が表示される
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible').and('contain', '管理者マイページ');
      cy.contains('システム管理者として全機能にアクセス可能です').should('be.visible');
      cy.get('[data-cy="user-management-toggle"]').should('be.visible');
    });

    it('一般ユーザーには管理者機能が表示されない', () => {
      cy.loginAsUser();
      cy.visit('/mypage');
      
      // 一般ユーザー用のマイページが表示される
      cy.get('[data-cy="mypage-title"]').should('be.visible').and('contain', 'マイページ');
      cy.get('[data-cy="admin-mypage-title"]').should('not.exist');
      cy.get('[data-cy="user-management-toggle"]').should('not.exist');
    });
  });

  describe('ユーザー管理機能', () => {
    beforeEach(() => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
    });

    it('ユーザー管理パネルが表示される', () => {
      // ユーザー管理トグルボタンをクリック
      cy.get('[data-cy="user-management-toggle"]').click();
      
      // ユーザー管理機能が展開される
      cy.contains('ユーザー管理').should('be.visible');
    });

    it('管理者はユーザー一覧を確認できる', () => {
      // バックエンドAPIをモック
      cy.intercept('GET', '**/admin/users*', {
        statusCode: 200,
        body: {
          data: {
            users: [
              {
                user_id: '1',
                email: 'user1@example.com',
                username: 'User 1',
                user_role: 2,
                user_status: 1,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z'
              },
              {
                user_id: '2',
                email: 'user2@example.com',
                username: 'User 2',
                user_role: 3,
                user_status: 1,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z'
              }
            ]
          }
        }
      }).as('getUserList');
      
      cy.get('[data-cy="user-management-toggle"]').click();
      
      // APIコールが実行される
      cy.wait('@getUserList');
      
      // ユーザー一覧が表示される
      cy.contains('user1@example.com').should('be.visible');
      cy.contains('user2@example.com').should('be.visible');
    });
  });

  describe('管理者専用アクション', () => {
    beforeEach(() => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
    });

    it('管理者はユーザー情報を更新できる', () => {
      // ユーザー更新APIをモック
      cy.intercept('PATCH', '**/admin/users/*', {
        statusCode: 200,
        body: {
          success: true,
          message: 'ユーザー情報を更新しました'
        }
      }).as('updateUser');

      // ユーザー管理機能を展開
      cy.get('[data-cy="user-management-toggle"]').click();
      
      // ユーザー更新フォーム操作をシミュレート
      // 実際のフォーム要素がある場合の操作
      if (cy.get('[data-cy="user-edit-form"]').should('exist')) {
        cy.get('[data-cy="user-username-input"]').clear().type('Updated User');
        cy.get('[data-cy="update-user-button"]').click();
        cy.wait('@updateUser');
      }
    });

    it('管理者はユーザーを削除できる', () => {
      // ユーザー削除APIをモック
      cy.intercept('DELETE', '**/admin/users/*', {
        statusCode: 200,
        body: {
          success: true,
          message: 'ユーザーを削除しました'
        }
      }).as('deleteUser');

      cy.get('[data-cy="user-management-toggle"]').click();
      
      // 削除操作をシミュレート（実際のボタンがある場合）
      if (cy.get('[data-cy="delete-user-button"]').should('exist')) {
        cy.get('[data-cy="delete-user-button"]').first().click();
        
        // 確認ダイアログの処理
        cy.on('window:confirm', () => true);
        
        cy.wait('@deleteUser');
      }
    });

    it('管理者はユーザーを復活させることができる', () => {
      // ユーザー復活APIをモック
      cy.intercept('POST', '**/admin/users/*/restore', {
        statusCode: 200,
        body: {
          success: true,
          message: 'ユーザーを復活させました'
        }
      }).as('restoreUser');

      cy.get('[data-cy="user-management-toggle"]').click();
      
      // 復活操作をシミュレート（実際のボタンがある場合）
      if (cy.get('[data-cy="restore-user-button"]').should('exist')) {
        cy.get('[data-cy="restore-user-button"]').first().click();
        cy.wait('@restoreUser');
      }
    });
  });

  describe('権限レベルのテスト', () => {
    it('レベル4（管理者）権限でアクセス可能', () => {
      // 管理者権限（レベル4）でログイン
      cy.login('admin@example.com', 'AdminPass123!');
      cy.visit('/mypage');
      
      // 管理者機能にアクセス可能
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      cy.get('[data-cy="user-management-toggle"]').should('be.visible');
    });

    it('レベル3（一般会員）権限では管理者機能にアクセスできない', () => {
      // 一般会員権限（レベル3）でログイン
      cy.login('member@example.com', 'MemberPass123!');
      cy.visit('/mypage');
      
      // 一般ユーザー向けページが表示される
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      cy.get('[data-cy="admin-mypage-title"]').should('not.exist');
      cy.get('[data-cy="user-management-toggle"]').should('not.exist');
    });

    it('レベル2（無料会員）権限では管理者機能にアクセスできない', () => {
      // 無料会員権限（レベル2）でログイン
      cy.login('free@example.com', 'FreePass123!');
      cy.visit('/mypage');
      
      // 一般ユーザー向けページが表示される
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      cy.get('[data-cy="upgrade-button"]').should('be.visible');
    });
  });

  describe('管理者機能のセキュリティテスト', () => {
    it('未認証状態では管理者ページにアクセスできない', () => {
      cy.visit('/mypage');
      cy.url().should('include', '/login');
    });

    it('一般ユーザーが管理者APIに直接アクセスしようとするとエラーになる', () => {
      cy.loginAsUser();
      
      // 管理者用APIへの直接アクセスを試みる
      cy.request({
        method: 'GET',
        url: 'http://backend:8000/api/v1/auth/admin/users',
        failOnStatusCode: false
      }).then((response) => {
        // 権限エラー（403）または認証エラー（401）が返される
        expect(response.status).to.be.oneOf([401, 403]);
      });
    });

    it('権限のないユーザーには管理者機能のボタンが表示されない', () => {
      cy.loginAsUser();
      cy.visit('/mypage');
      
      // 管理者専用要素が存在しない
      cy.get('body').should('not.contain', 'ユーザー管理');
      cy.get('body').should('not.contain', '管理者機能');
      cy.get('[data-cy="user-management-toggle"]').should('not.exist');
    });
  });

  describe('管理者UIの応答性テスト', () => {
    beforeEach(() => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
    });

    it('管理者機能パネルが適切に展開・収縮される', () => {
      // 初期状態ではユーザー管理パネルが非表示
      cy.get('[data-cy="user-management-toggle"]').should('be.visible');
      
      // クリックで展開
      cy.get('[data-cy="user-management-toggle"]').click();
      
      // 再度クリックで収縮
      cy.get('[data-cy="user-management-toggle"]').click();
    });

    it('管理者ページがレスポンシブに表示される', () => {
      // デスクトップサイズ
      cy.viewport(1920, 1080);
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      
      // タブレットサイズ
      cy.viewport(768, 1024);
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      
      // モバイルサイズ
      cy.viewport(375, 667);
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
    });
  });
});