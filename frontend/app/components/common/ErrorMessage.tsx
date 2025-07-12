import React from 'react';

// プロパティの型定義
interface ErrorMessageProps {
  message: string; // 表示するエラーメッセージ
  onDismiss: () => void; // エラーメッセージを非表示にするためのコールバック関数
}

/**
 * ErrorMessage コンポーネント
 * - エラーメッセージを表示し、手動で非表示にする。
 * - 親コンポーネントから `message` と `onDismiss` 関数を受け取る。
 *
 * @param {string} message - 表示するエラーメッセージの内容
 * @param {() => void} onDismiss - エラーメッセージを非表示にするコールバック
 */
const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onDismiss }) => {
  // エラーメッセージの表示
  return (
    <div className="mb-4 text-red-500 text-center bg-red-100 p-2 rounded">
      {message}
      <button onClick={onDismiss} className="ml-4 text-blue-500 underline">
        閉じる
      </button>
    </div>
  );
};

export default ErrorMessage;
