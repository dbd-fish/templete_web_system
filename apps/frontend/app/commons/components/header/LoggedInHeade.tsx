import SiteTitle from '~/commons/components/SiteTitle';
import { useState, useRef, useCallback } from 'react';
import { useLoaderData, useSubmit } from 'react-router';
import { LoaderDataType } from '~/commons/utils/types';
import useClickOutside from '~/commons/hooks/useClickOutside';

export default function Header() {
  const loaderData = useLoaderData<LoaderDataType>();
  const user = loaderData.user;

  const submit = useSubmit();
  const handleLogout = useCallback(async () => {
    const formData = new FormData();
    formData.append('_action', 'logout');
    submit(formData, { method: 'post' });
  }, [submit]);

  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotification, setShowNotification] = useState(false);

  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  useClickOutside(userMenuRef, () => setShowUserMenu(false));
  useClickOutside(notificationRef, () => setShowNotification(false));

  return (
    <header className="bg-gray-600 text-gray-100 py-3 shadow-md">
      <div className="container mx-auto px-4 flex justify-between items-center">
        {/* サイトタイトル */}
        <SiteTitle />

        {/* レスポンシブなナビゲーション */}
        <nav className="flex items-center space-x-4 sm:space-x-6">
          {/* 通知メニュー */}
          <div ref={notificationRef} className="relative">
            <button
              onClick={() => setShowNotification((prev) => !prev)}
              className="text-gray-300 hover:text-white text-sm sm:text-base"
            >
              通知
            </button>
            {showNotification && (
              <div className="absolute top-10 right-0 bg-gray-700 text-gray-100 rounded-md shadow-md w-48 p-3 sm:w-64 sm:p-4">
                <p className="text-xs sm:text-sm font-bold mb-2">新しい通知:</p>
                <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm">
                  <li>
                    <a href="/notification/1" className="hover:underline">
                      通知1
                    </a>
                  </li>
                  <li>
                    <a href="/notification/2" className="hover:underline">
                      通知2
                    </a>
                  </li>
                  <li>
                    <a href="/notification/3" className="hover:underline">
                      通知3
                    </a>
                  </li>
                </ul>
              </div>
            )}
          </div>

          {/* ユーザーメニュー */}
          <div ref={userMenuRef} className="relative">
            <button
              onClick={() => setShowUserMenu((prev) => !prev)}
              className="flex items-center space-x-2 bg-gray-700 text-white text-sm sm:text-base px-3 py-2 rounded-md hover:bg-gray-600"
            >
              <img
                src="https://via.placeholder.com/40"
                alt="User Avatar"
                className="w-6 h-6 sm:w-8 sm:h-8 rounded-full"
              />
              <span className="hidden sm:block">
                {user?.username || 'ゲスト'}
              </span>
            </button>
            {showUserMenu && (
              <div className="absolute top-10 right-0 bg-gray-700 text-gray-100 rounded-md shadow-md w-40 sm:w-48 p-3 sm:p-4">
                <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm">
                  <li>
                    <a href="/" className="hover:underline">
                      ホーム
                    </a>
                  </li>
                  <li>
                    <a href="/settings" className="hover:underline">
                      設定
                    </a>
                  </li>
                  <li>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left text-red-500 hover:underline"
                    >
                      ログアウト
                    </button>
                  </li>
                </ul>
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
