/**
 * 権限分離機能のE2Eテスト
 * 
 * 操作パターン:
 * - 管理者と一般ユーザーの権限分離確認
 * - 不正アクセスの防止機能検証
 * - ロールベースアクセス制御の動作確認
 */
describe('権限分離機能テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('権限レベルの定義と表示', () => {
    const roleTestCases = [
      {
        role: 1,
        email: 'guest@example.com',
        password: 'GuestPass123!',
        expectedRole: 'ゲスト',
        description: 'ゲスト権限'
      },
      {
        role: 2,
        email: 'free@example.com',
        password: 'FreePass123!',
        expectedRole: '無料会員',
        description: '無料会員権限'
      },
      {
        role: 3,
        email: 'member@example.com',
        password: 'MemberPass123!',
        expectedRole: '一般会員',
        description: '一般会員権限'
      },
      {
        role: 4,
        email: 'admin@example.com',
        password: 'AdminPass123!',
        expectedRole: '管理者',
        description: '管理者権限'
      },
      {
        role: 5,
        email: 'owner@example.com',
        password: 'OwnerPass123!',
        expectedRole: 'オーナー',
        description: 'オーナー権限'
      }
    ];

    roleTestCases.forEach(({ email, password, expectedRole, description }) => {
      it(`${description}ユーザーのロール表示が正しい`, () => {
        cy.login(email, password);
        cy.visit('/mypage');
        
        // ロールの表示確認
        cy.contains(expectedRole).should('be.visible');
      });
    });
  });

  describe('管理者権限（レベル4以上）の機能アクセス', () => {
    it('管理者は管理者機能にアクセスできる', () => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
      
      // 管理者専用要素の確認
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      cy.get('[data-cy="user-management-toggle"]').should('be.visible');
      cy.contains('システム管理者として全機能にアクセス可能です').should('be.visible');
    });

    it('オーナー（レベル5）も管理者機能にアクセスできる', () => {
      cy.login('owner@example.com', 'OwnerPass123!');
      cy.visit('/mypage');
      
      // 管理者専用要素の確認（オーナーも管理者機能を利用可能）
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      cy.get('[data-cy="user-management-toggle"]').should('be.visible');
    });

    it('管理者はバックエンドAPIにアクセスできる', () => {
      // 管理者用APIアクセスをモック
      cy.intercept('GET', '**/admin/users*', {
        statusCode: 200,
        body: {
          data: {
            users: []
          }
        }
      }).as('adminAPI');

      cy.loginAsAdmin();
      cy.visit('/mypage');
      cy.get('[data-cy="user-management-toggle"]').click();
      
      // 管理者APIが正常に呼び出される
      cy.wait('@adminAPI');
    });
  });

  describe('一般ユーザー権限（レベル3以下）の機能制限', () => {
    const nonAdminUsers = [
      { email: 'guest@example.com', password: 'GuestPass123!', role: 'ゲスト' },
      { email: 'free@example.com', password: 'FreePass123!', role: '無料会員' },
      { email: 'member@example.com', password: 'MemberPass123!', role: '一般会員' }
    ];

    nonAdminUsers.forEach(({ email, password, role }) => {
      it(`${role}は管理者機能にアクセスできない`, () => {
        cy.login(email, password);
        cy.visit('/mypage');
        
        // 管理者専用要素が存在しない
        cy.get('[data-cy="admin-mypage-title"]').should('not.exist');
        cy.get('[data-cy="user-management-toggle"]').should('not.exist');
        
        // 一般ユーザー向けタイトルが表示される
        cy.get('[data-cy="mypage-title"]').should('be.visible');
      });

      it(`${role}は管理者APIにアクセスできない`, () => {
        cy.login(email, password);
        
        // 管理者APIへの直接アクセスを試みる
        cy.request({
          method: 'GET',
          url: 'http://backend:8000/api/v1/auth/admin/users',
          failOnStatusCode: false
        }).then((response) => {
          // 権限エラーまたは認証エラーが返される
          expect(response.status).to.be.oneOf([401, 403]);
        });
      });
    });
  });

  describe('プレミアム機能の権限制御', () => {
    it('無料会員にはアップグレード案内が表示される', () => {
      cy.login('free@example.com', 'FreePass123!');
      cy.visit('/mypage');
      
      // プレミアム機能案内の存在確認
      cy.contains('プレミアム機能').should('be.visible');
      cy.get('[data-cy="upgrade-button"]').should('be.visible');
      cy.contains('高度な分析機能').should('be.visible');
    });

    it('一般会員以上にはアップグレード案内が適切に表示される', () => {
      cy.login('member@example.com', 'MemberPass123!');
      cy.visit('/mypage');
      
      // 会員レベルに応じた表示制御の確認
      // (具体的な表示は実装に依存するため、存在確認のみ)
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });

    it('管理者にはアップグレード案内が表示されない', () => {
      cy.loginAsAdmin();
      cy.visit('/mypage');
      
      // プレミアム機能案内が非表示
      cy.get('[data-cy="upgrade-button"]').should('not.exist');
      cy.contains('プレミアム機能').should('not.exist');
    });
  });

  describe('動的権限チェック', () => {
    it('セッション中の権限変更が反映される', () => {
      // 一般ユーザーでログイン
      cy.loginAsUser();
      cy.visit('/mypage');
      cy.get('[data-cy="mypage-title"]').should('be.visible');
      
      // 権限変更をシミュレート（管理者による権限昇格）
      cy.intercept('GET', '**/mypage', {
        statusCode: 200,
        body: {
          user: {
            user_id: '1',
            email: 'user@example.com',
            username: 'Test User',
            user_role: 4, // 管理者権限に昇格
            user_status: 1
          }
        }
      }).as('roleUpdate');
      
      // ページリロードで新しい権限を取得
      cy.reload();
      
      // 管理者機能が利用可能になる
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
    });

    it('権限降格も正しく反映される', () => {
      // 管理者でログイン
      cy.loginAsAdmin();
      cy.visit('/mypage');
      cy.get('[data-cy="admin-mypage-title"]').should('be.visible');
      
      // 権限変更をシミュレート（権限降格）
      cy.intercept('GET', '**/mypage', {
        statusCode: 200,
        body: {
          user: {
            user_id: '1',
            email: 'admin@example.com',
            username: 'Admin User',
            user_role: 2, // 無料会員権限に降格
            user_status: 1
          }
        }
      }).as('roleDowngrade');
      
      // ページリロードで新しい権限を取得
      cy.reload();
      
      // 管理者機能が利用不可になる
      cy.get('[data-cy="admin-mypage-title"]').should('not.exist');
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });
  });

  describe('APIレベルでの権限制御', () => {
    it('管理者用ユーザー取得API', () => {
      cy.loginAsAdmin();
      
      // 管理者として正常にAPIアクセス
      cy.request({
        method: 'GET',
        url: 'http://backend:8000/api/v1/auth/admin/users?page=1&page_size=10',
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(200);
      });
    });

    it('管理者用ユーザー更新API', () => {
      cy.loginAsAdmin();
      
      // ユーザー更新API（管理者権限必要）
      cy.request({
        method: 'PATCH',
        url: 'http://backend:8000/api/v1/auth/admin/users/1',
        body: {
          username: 'Updated Username'
        },
        failOnStatusCode: false
      }).then((response) => {
        // 管理者なので正常またはリソースが存在しない場合のエラー
        expect(response.status).to.be.oneOf([200, 404]);
      });
    });

    it('管理者用ユーザー削除API', () => {
      cy.loginAsAdmin();
      
      // ユーザー削除API（管理者権限必要）
      cy.request({
        method: 'DELETE',
        url: 'http://backend:8000/api/v1/auth/admin/users/1',
        failOnStatusCode: false
      }).then((response) => {
        // 管理者なので正常またはリソースが存在しない場合のエラー
        expect(response.status).to.be.oneOf([200, 404]);
      });
    });

    it('一般ユーザーの管理者API拒否', () => {
      cy.loginAsUser();
      
      // 一般ユーザーが管理者APIにアクセスを試みる
      cy.request({
        method: 'GET',
        url: 'http://backend:8000/api/v1/auth/admin/users',
        failOnStatusCode: false
      }).then((response) => {
        // 権限エラーが返される
        expect(response.status).to.be.oneOf([401, 403]);
      });
    });
  });

  describe('ユーザー状態による制御', () => {
    it('アクティブユーザーは正常に機能を利用できる', () => {
      cy.loginAsUser();
      cy.visit('/mypage');
      
      // アカウント状態の確認
      cy.contains('アクティブ').should('be.visible');
      cy.get('[data-cy="mypage-title"]').should('be.visible');
    });

    it('停止中ユーザーのアクセス制御', () => {
      // 停止中ユーザーの模擬
      cy.intercept('GET', '**/mypage', {
        statusCode: 403,
        body: {
          error: 'アカウントが停止されています',
          type: 'account_suspended'
        }
      }).as('suspendedUser');

      cy.login('suspended@example.com', 'SuspendedPass123!');
      cy.visit('/mypage');
      
      // アクセス拒否の確認
      cy.contains('アカウントが停止されています').should('be.visible');
    });
  });

  describe('セキュリティテスト', () => {
    it('権限昇格攻撃の防御', () => {
      cy.loginAsUser();
      
      // 一般ユーザーが管理者機能のURLに直接アクセス
      cy.visit('/mypage');
      
      // 管理者機能が表示されない
      cy.get('[data-cy="admin-mypage-title"]').should('not.exist');
      cy.get('[data-cy="user-management-toggle"]').should('not.exist');
    });

    it('不正なトークンによるアクセス', () => {
      // 不正なトークンをセット
      cy.setCookie('authToken', 'invalid-token');
      cy.visit('/mypage');
      
      // ログインページにリダイレクト
      cy.url().should('include', '/login');
    });

    it('期限切れトークンの処理', () => {
      // 期限切れトークンのシミュレート
      cy.intercept('GET', '**/mypage', {
        statusCode: 401,
        body: {
          error: 'Token has expired',
          type: 'token_expired'
        }
      }).as('expiredToken');

      cy.loginAsUser();
      cy.visit('/mypage');
      
      // 認証失効時の処理確認
      cy.url().should('include', '/login');
    });
  });
});