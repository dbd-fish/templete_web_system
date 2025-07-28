/**
 * 認証フロー顧客シナリオE2Eテスト
 * 
 * 認証に関する顧客の実際の操作パターンをテスト
 * - サインアップからログインまでの完全フロー
 * - ログアウト後の再ログイン
 * - 認証エラー時の顧客対応
 */
describe('認証フロー顧客シナリオ', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.visit('/', { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('新規顧客のアカウント作成フロー', () => {
    it('初回訪問 → アカウント作成 → 即座にログイン利用開始', () => {
      const timestamp = Date.now();
      const newUserEmail = `testuser${timestamp}@example.com`;
      const newUserPassword = 'NewPassword123+-';
      
      // ステップ1: トップページからサインアップへ
      cy.get('[data-cy="login-link"]').should('be.visible').click();
      cy.get('[data-cy="signup-link"]').should('be.visible').click();
      
      // ステップ2: 新規アカウント情報入力
      cy.url().should('include', '/signup');
      cy.get('[data-cy="email-input"]').should('be.visible').type(newUserEmail);
      cy.get('[data-cy="password-input"]').should('be.visible').type(newUserPassword);
      cy.get('[data-cy="password-confirm-input"]').should('be.visible').type(newUserPassword);
      
      // ステップ3: 利用規約確認と同意
      cy.get('[data-cy="terms-checkbox"]').should('be.visible').check();
      
      // ステップ4: アカウント作成実行
      cy.get('[data-cy="signup-submit-button"]').should('be.visible').click();
      
      // ステップ5: 作成完了後の処理
      cy.url().should('match', /(login|signup-success|mypage)/);
      
      // アカウント作成と同時にログインする場合
      cy.url().then((url) => {
        if (url.includes('/mypage')) {
          // 自動ログインされた場合
          cy.get('[data-cy="user-menu"]').should('be.visible');
          cy.contains(newUserEmail).should('be.visible');
        } else {
          // ログインページにリダイレクトされた場合
          if (url.includes('signup-success')) {
            cy.get('[data-cy="go-to-login-link"]').click();
          }
          
          // 作成したアカウントでログイン
          cy.visit('/login');
          cy.get('[data-cy="email-input"]').type(newUserEmail);
          cy.get('[data-cy="password-input"]').type(newUserPassword);
          cy.get('[data-cy="login-submit-button"]').click();
          
          // ログイン成功確認
          cy.url().should('include', '/mypage');
          cy.get('[data-cy="user-menu"]').should('be.visible');
        }
      });
    });
  });

  describe('既存顧客のログイン・ログアウトフロー', () => {
    it('日常的なログイン → サービス利用 → ログアウト', () => {
      // ステップ1: ログインページに直接アクセス
      cy.visit('/login');
      
      // ステップ2: 認証情報入力
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ3: ログイン成功後のマイページ利用
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-info"]').should('be.visible');
      cy.contains('targetuser@example.com').should('be.visible');
      
      // ステップ4: ユーザーメニューの確認
      cy.get('[data-cy="user-menu"]').should('be.visible').click();
      
      // ステップ5: プロフィール情報の確認
      cy.get('[data-cy="profile-link"]').should('be.visible');
      cy.get('[data-cy="settings-link"]').should('be.visible');
      
      // ステップ6: ログアウト実行
      cy.get('[data-cy="logout-button"]').should('be.visible').click();
      
      // ステップ7: ログアウト完了確認
      cy.url().should('include', '/login');
      cy.get('[data-cy="login-title"]').should('be.visible');
    });
  });

  describe('認証エラー時の顧客対応フロー', () => {
    it('パスワード間違い → エラー確認 → 正しいパスワードで再試行', () => {
      cy.visit('/login');
      
      // ステップ1: 間違ったパスワードでログイン試行
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword123');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: エラーメッセージの確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      cy.url().should('include', '/login'); // ログインページに留まる
      
      // ステップ3: パスワードフィールドをクリアして正しいパスワード入力
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ4: ログイン成功
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
    });

    it('存在しないアカウントでログイン試行 → エラー → アカウント作成案内', () => {
      cy.visit('/login');
      
      // ステップ1: 存在しないメールアドレスでログイン試行
      cy.get('[data-cy="email-input"]').type('nonexistent@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: エラーメッセージ確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // ステップ3: 新規アカウント作成リンクをクリック
      cy.get('[data-cy="signup-link"]').should('be.visible').click();
      
      // ステップ4: サインアップページに移動
      cy.url().should('include', '/signup');
    });
  });

  describe('パスワードリセットフロー', () => {
    it('パスワード忘れ → メールアドレス入力 → リセットメール送信', () => {
      cy.visit('/login');
      
      // ステップ1: パスワードを忘れた場合のリンクをクリック
      cy.get('[data-cy="forgot-password-link"]').should('be.visible').click();
      
      // ステップ2: パスワードリセットページに移動
      cy.url().should('include', '/send-reset-password-email');
      cy.get('h1').should('contain', 'パスワードリセット');
      
      // ステップ3: メールアドレス入力
      cy.get('[data-cy="email-input"]').should('be.visible').type('targetuser@example.com');
      
      // ステップ4: リセットメール送信
      cy.get('[data-cy="send-email-button"]').should('be.visible').click();
      
      // ステップ5: 送信完了メッセージ確認
      cy.contains('パスワードリセットメールを送信しました').should('be.visible');
      
      // ステップ6: ログインページに戻るリンク
      cy.get('[data-cy="back-to-login-link"]').should('be.visible').click();
      cy.url().should('include', '/login');
    });
  });

  describe('セッション継続と自動ログアウト', () => {
    it('ログイン → ページ間移動 → セッション継続確認', () => {
      // ステップ1: ログイン
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: マイページでログイン状態確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      
      // ステップ3: ホームページに移動
      cy.visit('/');
      cy.get('[data-cy="user-menu"]').should('be.visible'); // ログイン状態維持
      
      // ステップ4: マイページに戻る
      cy.get('[data-cy="user-menu"]').click();
      cy.get('[data-cy="mypage-link"]').click();
      
      // ステップ5: マイページに正常にアクセスできる
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-info"]').should('be.visible');
    });

    it('ブラウザリロード後のセッション復元', () => {
      // ステップ1: ログイン
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ2: マイページでログイン確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      
      // ステップ3: ページリロード
      cy.reload();
      
      // ステップ4: ログイン状態が復元される
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      cy.contains('targetuser@example.com').should('be.visible');
    });
  });

  describe('アクセス制御と認証ガード', () => {
    it('認証が必要なページへの直接アクセス → ログイン誘導 → 目的ページへリダイレクト', () => {
      // ステップ1: ログインせずに保護されたページにアクセス
      cy.visit('/mypage');
      
      // ステップ2: ログインページにリダイレクト
      cy.url().should('include', '/login');
      
      // ステップ3: リダイレクト理由の表示確認
      cy.contains('ログインが必要です').should('be.visible');
      
      // ステップ4: ログイン実行
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ステップ5: 元の目的ページ（マイページ）にリダイレクト
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-info"]').should('be.visible');
    });
  });

  describe('フォーム操作とユーザビリティ', () => {
    it('フォーム入力時のリアルタイムバリデーション', () => {
      cy.visit('/login');
      
      // ステップ1: 空の状態で送信
      cy.get('[data-cy="login-submit-button"]').click();
      
      // HTML5バリデーションが働く
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // ステップ2: 不正なメールフォーマット入力
      cy.get('[data-cy="email-input"]').type('invalid-email');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // メールフォーマットエラー
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // ステップ3: 正しい入力で修正
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });

    it('キーボードナビゲーションでのログイン操作', () => {
      cy.visit('/login');
      
      // Tabキーとエンターキーでログイン
      cy.get('body').tab(); // 最初のフォーカス可能要素へ
      cy.focused().should('have.attr', 'data-cy', 'email-input');
      
      cy.focused().type('targetuser@example.com').tab();
      cy.focused().should('have.attr', 'data-cy', 'password-input');
      
      cy.focused().type('Password123456+-').tab();
      cy.focused().should('have.attr', 'data-cy', 'login-submit-button');
      
      cy.focused().type('{enter}');
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });
});