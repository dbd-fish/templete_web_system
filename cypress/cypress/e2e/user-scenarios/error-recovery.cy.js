/**
 * エラー対応・復旧シナリオE2Eテスト
 * 
 * 顧客がエラーに遭遇した際の対応と復旧操作をテスト
 * - ネットワークエラー時の対応
 * - フォームエラーからの復旧
 * - セッション切れ時の対応
 * - 入力ミス時の修正フロー
 */
describe('エラー対応・復旧シナリオ', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.visit('/', { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('ログインエラーからの復旧', () => {
    it('複数回のログイン失敗 → 正しい認証情報で最終的に成功', () => {
      cy.visit('/login');
      
      // 試行1: 完全に間違った情報
      cy.get('[data-cy="email-input"]').type('wrong@example.com');
      cy.get('[data-cy="password-input"]').type('wrongpassword');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // 試行2: 正しいメール、間違ったパスワード
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').clear().type('stillwrong');
      cy.get('[data-cy="login-submit-button"]').click();
      
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // 試行3: 正しい認証情報で成功
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // 最終的にログイン成功
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
    });

    it('大文字小文字間違い → エラー → 正しい入力で修正', () => {
      cy.visit('/login');
      
      // 大文字小文字を間違えた入力
      cy.get('[data-cy="email-input"]').type('TARGETUSER@EXAMPLE.COM');
      cy.get('[data-cy="password-input"]').type('password123456+-'); // 大文字Pが小文字
      cy.get('[data-cy="login-submit-button"]').click();
      
      // エラー確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // 正しい大文字小文字で修正
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('フォームバリデーションエラーからの復旧', () => {
    it('必須フィールド未入力 → バリデーション → 正しい入力で修正', () => {
      cy.visit('/login');
      
      // 空のフォームで送信
      cy.get('[data-cy="login-submit-button"]').click();
      
      // HTML5バリデーションエラー確認
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // メールアドレスのみ入力して再送信
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // パスワード未入力エラー
      cy.get('[data-cy="password-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // パスワードも入力して成功
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });

    it('不正なメールフォーマット → バリデーション → 正しいフォーマットで修正', () => {
      cy.visit('/login');
      
      // 不正なメールフォーマット入力
      cy.get('[data-cy="email-input"]').type('invalid-email-format');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // メールフォーマットエラー
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.contain('有効な');
      });
      
      // 正しいメールフォーマットで修正
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('サインアップフォームエラーからの復旧', () => {
    it('パスワード確認不一致 → エラー → 一致させて修正', () => {
      cy.visit('/signup');
      
      const timestamp = Date.now();
      const testEmail = `testuser${timestamp}@example.com`;
      
      // パスワード確認が一致しない状態で送信
      cy.get('[data-cy="email-input"]').type(testEmail);
      cy.get('[data-cy="password-input"]').type('Password123+-');
      cy.get('[data-cy="password-confirm-input"]').type('DifferentPassword123+-');
      cy.get('[data-cy="terms-checkbox"]').check();
      cy.get('[data-cy="signup-submit-button"]').click();
      
      // パスワード不一致エラー（フロントエンドバリデーション）
      cy.contains('パスワードが一致しません').should('be.visible');
      
      // パスワード確認を正しく修正
      cy.get('[data-cy="password-confirm-input"]').clear().type('Password123+-');
      cy.get('[data-cy="signup-submit-button"]').click();
      
      // サインアップ成功またはログインページへ
      cy.url().should('match', /(signup-success|login|mypage)/);
    });

    it('利用規約未同意 → エラー → 同意して修正', () => {
      cy.visit('/signup');
      
      const timestamp = Date.now();
      const testEmail = `testuser${timestamp}@example.com`;
      
      // 利用規約にチェックを入れずに送信
      cy.get('[data-cy="email-input"]').type(testEmail);
      cy.get('[data-cy="password-input"]').type('Password123+-');
      cy.get('[data-cy="password-confirm-input"]').type('Password123+-');
      cy.get('[data-cy="signup-submit-button"]').click();
      
      // 利用規約未同意エラー
      cy.get('[data-cy="terms-checkbox"]').then($checkbox => {
        expect($checkbox[0].validationMessage).to.not.be.empty;
      });
      
      // 利用規約に同意
      cy.get('[data-cy="terms-checkbox"]').check();
      cy.get('[data-cy="signup-submit-button"]').click();
      
      // サインアップ成功
      cy.url().should('match', /(signup-success|login|mypage)/);
    });
  });

  describe('セッション切れ時の復旧', () => {
    it('ログイン後に手動でCookieを削除 → セッション切れ → 再ログイン', () => {
      // まずログイン
      cy.visit('/login');
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功確認
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
      
      // Cookieを手動で削除（セッション切れをシミュレート）
      cy.clearCookies();
      
      // ページをリロード
      cy.reload();
      
      // ログインページにリダイレクトされる
      cy.url().should('include', '/login');
      
      // 再ログイン
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // 再度マイページにアクセス可能
      cy.url().should('include', '/mypage');
      cy.get('[data-cy="user-menu"]').should('be.visible');
    });
  });

  describe('ネットワーク関連エラーの対応', () => {
    it('ページ読み込みエラー → リロード → 正常表示', () => {
      // 初回アクセスが失敗した場合を想定
      cy.visit('/login', { failOnStatusCode: false });
      
      // ページが正常に読み込まれるまでリロード
      cy.get('body').then($body => {
        if (!$body.find('[data-cy="login-form"]').length) {
          cy.reload();
        }
      });
      
      // 最終的にログインフォームが表示される
      cy.get('[data-cy="login-form"]', { timeout: 15000 }).should('be.visible');
      cy.get('[data-cy="email-input"]').should('be.visible');
      cy.get('[data-cy="password-input"]').should('be.visible');
    });
  });

  describe('入力ミス時の修正フロー', () => {
    it('タイポ修正 → 段階的な入力修正 → 最終的に成功', () => {
      cy.visit('/login');
      
      // タイポを含む入力
      cy.get('[data-cy="email-input"]').type('targetuse@example.com'); // rが抜けている
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // エラー確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // 段階的修正: 最後に文字を追加
      cy.get('[data-cy="email-input"]').focus().type('{end}').type('{backspace}r@example.com');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // まだエラー（まだタイポがある）
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // 完全に正しく修正
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });

    it('コピー&ペースト時の不要文字混入 → クリア → 手動入力で修正', () => {
      cy.visit('/login');
      
      // 不要な文字が混入した状態を想定
      cy.get('[data-cy="email-input"]').type(' targetuser@example.com '); // 前後にスペース
      cy.get('[data-cy="password-input"]').type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // エラー確認
      cy.contains('メールアドレスまたはパスワードが正しくありません').should('be.visible');
      
      // フィールドをクリアして手動で正しく入力
      cy.get('[data-cy="email-input"]').clear().type('targetuser@example.com');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('ブラウザ操作エラーからの復旧', () => {
    it('戻るボタン使用 → フォーム状態リセット → 再入力', () => {
      cy.visit('/login');
      
      // フォームに入力
      cy.get('[data-cy="email-input"]').type('targetuser@example.com');
      cy.get('[data-cy="password-input"]').type('partial');
      
      // 別のページに移動
      cy.get('[data-cy="signup-link"]').click();
      cy.url().should('include', '/signup');
      
      // ブラウザの戻るボタンでログインページに戻る
      cy.go('back');
      cy.url().should('include', '/login');
      
      // フォーム状態確認・完了
      cy.get('[data-cy="email-input"]').should('have.value', 'targetuser@example.com');
      cy.get('[data-cy="password-input"]').clear().type('Password123456+-');
      cy.get('[data-cy="login-submit-button"]').click();
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });

  describe('アクセシビリティエラーからの復旧', () => {
    it('キーボードナビゲーションでのエラー対応', () => {
      cy.visit('/login');
      
      // キーボードのみでナビゲーション
      cy.get('body').tab();
      cy.focused().type('targetuser'); // 不完全なメール
      
      cy.focused().tab();
      cy.focused().type('Password123456+-');
      
      cy.focused().tab();
      cy.focused().type('{enter}'); // エンターキーで送信
      
      // バリデーションエラー確認
      cy.get('[data-cy="email-input"]').then($input => {
        expect($input[0].validationMessage).to.not.be.empty;
      });
      
      // Tabで戻ってメールアドレスを修正
      cy.get('[data-cy="email-input"]').focus().clear().type('targetuser@example.com');
      cy.get('[data-cy="login-submit-button"]').focus().type('{enter}');
      
      // ログイン成功
      cy.url().should('include', '/mypage');
    });
  });
});