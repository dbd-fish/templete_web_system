// エラーハンドリング設定：原因不明なエラーで悩まされる場合はこのファイルでスキップするように定義する。
Cypress.on('uncaught:exception', (err) => {
  console.log('Uncaught Exception:', err.message); // エラーメッセージをログに出力
  
  // 無視するエラーパターン（安全で一般的でないエラーのみ）
  const ignoredErrors = [
    // ブラウザ既知の問題（無害）
    'ResizeObserver loop limit exceeded',
    
    // 開発環境特有の問題（Webpack Hot Reload等）
    'Loading CSS chunk', // CSS chunks loading errors (開発環境)
    'Loading chunk', // JavaScript chunks loading errors (開発環境)
    'ChunkLoadError', // Webpack chunk loading errors (開発環境)
    
    // Google OAuth開発環境特有の問題
    'GoogleAuth is not defined', // Google OAuth not loaded errors (テスト環境)
    'google is not defined', // Google API not loaded errors (テスト環境)
    
    // Cypress特有の無害なメッセージ
    'The following error originated from your application code, not from Cypress.',
    'Non-Error promise rejection captured'
  ];
  
  // エラーメッセージに無視すべき文字列が含まれているかチェック
  const shouldIgnore = ignoredErrors.some(pattern => 
    err.message.includes(pattern)
  );
  
  if (shouldIgnore) {
    console.log('Ignoring error:', err.message);
    return false; // テストの失敗を回避
  }
  
  // 重要なエラーをログ出力（見逃しを防ぐ）
  if (err.message.includes('Network request failed') || 
      err.message.includes('Failed to fetch') ||
      err.message.includes('Script error')) {
    console.error('⚠️  IMPORTANT ERROR (not ignored):', err.message);
    console.error('This error indicates a potential application issue that should be investigated.');
  }
  
  return true; // 他のエラーは通常通り失敗として扱う
});

// ネットワーク関連のエラーハンドリング
Cypress.on('fail', (err) => {
  // タイムアウトエラーの詳細ログ
  if (err.message.includes('Timed out')) {
    console.log('Timeout error occurred:', err.message);
    console.log('Consider increasing timeout or checking network connectivity');
  }
  
  // 要素が見つからないエラーの詳細ログ
  if (err.message.includes('Expected to find element')) {
    console.log('Element not found error:', err.message);
    console.log('Check if the selector is correct and the element exists');
  }
  
  throw err; // エラーを再スロー
});
