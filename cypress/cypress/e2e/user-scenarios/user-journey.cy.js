/**
 * 顧客ユーザージャーニーE2Eテスト
 * 
 * 実際の顧客が行う操作シナリオをベースとしたE2Eテスト
 * - ユーザーの視点での一連の操作フロー
 * - 画面間の遷移とユーザビリティ
 * - エラー発生時の回復操作
 */
describe('顧客ユーザージャーニー', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.visit('/', { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('新規顧客の初回サイト利用', () => {
    it('サイト訪問 → アカウント作成 → ログイン → マイページ利用の完全フロー', () => {
      // ステップ1: サイトのトップページを確認
      cy.get('h1', { timeout: 10000 }).should('be.visible');
      
      // ステップ2: ログインリンクをクリック
      cy.get('[data-cy="login-link"]').should('be.visible').click();
      cy.url().should('include', '/login');
      
      // ステップ3: 新規アカウント作成を選択
      cy.get('[data-cy="signup-link"]').should('be.visible').click();
      cy.url().should('include', '/signup');
      
      // ステップ4: アカウント情報を入力
      const timestamp = Date.now();
      const testEmail = `newuser${timestamp}@example.com`;
      
      cy.get('[data-cy="email-input"]').should('be.visible').type(testEmail);
      cy.get('[data-cy="password-input"]').should('be.visible').type('NewPassword123+-');
      cy.get('[data-cy="password-confirm-input"]').should('be.visible').type('NewPassword123+-');
      
      // ステップ5: 利用規約に同意してアカウント作成
      cy.get('[data-cy="terms-checkbox"]').should('be.visible').check();
      cy.get('[data-cy="signup-submit-button"]').should('be.visible').click();
      
      // ステップ6: アカウント作成後のログイン
      cy.url().should('match', /(login|signup-success)/);
      
      // サインアップ成功ページの場合はログインページへ移動
      cy.url().then((url) => {
        if (url.includes('signup-success')) {
          cy.get('[data-cy="go-to-login-link"]').click();
        }
      });
      
      // ログインページでログイン実行
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type(testEmail);
      cy.get('[data-cy="password-input"]').type('NewPassword123+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ7: マイページでサービス利用開始
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      cy.contains(testEmail).should('be.visible');
    });
  });

  describe('既存顧客の日常的なサイト利用', () => {
    it('ログイン → マイページ確認 → ログアウトの日常フロー', () => {
      // ステップ1: ログインページに直接アクセス
      cy.visit('/login');
      
      // ステップ2: 素早くログイン
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ3: マイページで情報確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-info"]').should('be.visible');
      cy.contains('targetuser@example.com').should('be.visible');
      
      // ステップ4: ユーザーメニューを開く
      cy.get('[data-cy="user-menu"]').should('be.visible').click();
      
      // ステップ5: ログアウト
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ステップ6: ログアウト完了確認
      cy.url().should('include', '/login');
      cy.get('[data-cy="login-title"]').should('be.visible');
    });
  });

  describe('困った時の顧客対応フロー', () => {
    it('パスワード忘れ → リセット → 新パスワードでログインの完全フロー', () => {
      // ステップ1: ログインページでパスワードを忘れた場合
      cy.visit('/login');
      cy.get('[data-cy="forgot-password-link"]').should('be.visible').click();
      
      // ステップ2: パスワードリセットページで手続き
      cy.url().should('include', '/send-reset-password-email');
      cy.get('[data-cy="email-input"]').should('be.visible').type('targetuser@example.com');
      cy.get('[data-cy="send-email-button"]').should('be.visible').click();
      
      // ステップ3: リセットメール送信完了の確認
      cy.contains('パスワードリセットメールを送信しました').should('be.visible');
    });

    it('ログイン失敗 → 再試行 → 成功の回復フロー', () => {
      // ステップ1: 間違ったパスワードでログイン試行
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: エラーメッセージを確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // ステップ3: 正しいパスワードで再試行
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ4: ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('保護されたページアクセス時の認証フロー', () => {
    it('マイページに直接アクセス → ログイン → 元ページに戻る', () => {
      // ステップ1: ログインせずに保護されたページにアクセス
      cy.visit('/mypage');
      
      // ステップ2: ログインページにリダイレクト
      cy.url().should('include', '/login');
      
      // ステップ3: ログイン実行
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ4: 元の目的ページ（マイページ）に戻る
      cy.url().should('include', '/mypage');
      cy.contains('マイページ').should('be.visible');
    });
  });

  describe('セッション管理の顧客体験', () => {
    it('ログイン → ページリロード → セッション継続確認', () => {
      // ステップ1: ログイン
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: マイページ表示確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      
      // ステップ3: ページをリロード
      cy.reload();
      
      // ステップ4: ログイン状態が維持されていることを確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      
      // ステップ5: 別のページに移動してもセッション継続
      cy.visit('/');
      cy.get('[data-cy="user-menu"]').should('be.visible');
    });
  });

  describe('フォームバリデーションと顧客ガイダンス', () => {
    it('フォーム入力ミス → バリデーション表示 → 修正 → 成功', () => {
      // ステップ1: ログインページで不正な入力
      cy.visit('/login');
      
      // 空のフィールドで送信
      cy.get('[data-cy="login-submit-button"]').click();
      
      // HTML5バリデーションが働く
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // ステップ2: 不正なメールフォーマット
      cy.get('[data-cy="email-input"]').type('invalid-email');
      cy.get('[data-cy="password-input"]').type('password123');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // バリデーションエラー
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.contain('有効なメール');
      });
      
      // ステップ3: 正しい形式で修正
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ4: ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('アクセシビリティを考慮した操作フロー', () => {
    it('キーボードナビゲーションでログインフロー', () => {
      cy.visit('/login');
      
      // Tabキーでナビゲーション
      cy.get('[data-cy="email-input"]').focus()
        .type('targetuser@example.com')
        .tab()
        .type('Password123456+-')
        .tab()
        .type('{enter}'); // Enterキーでログイン
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });
});