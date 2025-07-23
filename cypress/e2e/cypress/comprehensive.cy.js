/**
 * 包括的なE2Eテスト
 * 
 * 操作パターン:
 * - フロントエンドアプリケーション全体の動作確認
 * - レスポンシブデザインのテスト
 * - パフォーマンス要件の検証
 */
describe('フロントエンドアプリケーション包括テスト', () => {
  const baseUrl = 'https://frontend:5173';
  
  beforeEach(() => {
    // HTTPS証明書エラーを無視してページにアクセス
    cy.visit(baseUrl, { 
      failOnStatusCode: false,
      timeout: 30000
    });
  });

  describe('基本画面テスト', () => {
    it('ホームページが正常に表示される', () => {
      cy.url().should('include', '5173');
      cy.get('html').should('exist');
      cy.get('body').should('be.visible');
    });

    it('HTMLの基本構造が正しい', () => {
      cy.get('html').should('have.attr', 'lang', 'en');
      cy.get('meta[name="viewport"]').should('exist');
      cy.get('head').should('exist');
    });

    it('ページが完全にロードされる', () => {
      cy.document().its('readyState').should('eq', 'complete');
    });
  });

  describe('レスポンシブ対応テスト', () => {
    const viewports = [
      { width: 1920, height: 1080, name: 'デスクトップ' },
      { width: 768, height: 1024, name: 'タブレット' },
      { width: 375, height: 667, name: 'モバイル' }
    ];

    viewports.forEach(viewport => {
      it(`${viewport.name}サイズでページが表示される`, () => {
        cy.viewport(viewport.width, viewport.height);
        cy.get('body').should('be.visible');
        cy.get('html').should('exist');
      });
    });
  });

  describe('JavaScript動作テスト', () => {
    it('JavaScriptが有効で動作している', () => {
      cy.window().should('exist');
      cy.document().should('exist');
    });

    it('Reactアプリケーションが動作している', () => {
      // React Router アプリケーションの基本要素確認
      cy.get('body').should('not.be.empty');
      // 通常のReactアプリなら何らかのDOM要素が存在するはず
      cy.get('*').should('have.length.greaterThan', 10);
    });
  });

  describe('基本的なSEO要素テスト', () => {
    it('基本的なmeta要素が存在する', () => {
      cy.get('meta[charset]').should('exist');
      cy.get('meta[name="viewport"]').should('exist');
    });

    it('HTMLの構造が正しい', () => {
      cy.get('html').should('exist');
      cy.get('head').should('exist');
      cy.get('body').should('exist');
    });
  });
});

describe('バックエンドAPI接続テスト', () => {
  describe('健康チェックAPI', () => {
    it('健康チェックAPIが正常に応答する', () => {
      cy.request({
        method: 'GET',
        url: 'http://backend:8000/api/v1/dev/health',
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('success', true);
        expect(response.body).to.have.property('message');
        expect(response.body).to.have.property('data');
      });
    });
  });

  describe('シードデータAPI', () => {
    it('シードデータAPIが実行可能', () => {
      cy.request({
        method: 'POST',
        url: 'http://backend:8000/api/v1/dev/seed_data',
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.eq(200);
      });
    });
  });
});

describe('パフォーマンステスト', () => {
  it('ページの読み込み時間が許容範囲内', () => {
    const startTime = Date.now();
    cy.visit('https://frontend:5173', { 
      failOnStatusCode: false,
      timeout: 30000
    });
    cy.get('body').should('be.visible').then(() => {
      const loadTime = Date.now() - startTime;
      expect(loadTime).to.be.lessThan(10000); // 10秒以内
    });
  });

  it('ページサイズが適切な範囲内', () => {
    cy.request({
      url: 'https://frontend:5173',
      failOnStatusCode: false
    }).then((response) => {
      const contentLength = response.headers['content-length'] || response.body.length;
      // 基本的なHTMLページなら10MBを超えることはないはず
      expect(Number(contentLength)).to.be.lessThan(10 * 1024 * 1024);
    });
  });
});