// mainタグの基本レイアウト
import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export default function Main({ children, className = '' }: MainLayoutProps) {
  return (
    <main
      className={`min-h-screen flex-grow flex items-center justify-center mt-8 ${className}`}
    >
      {children}
    </main>
  );
}
