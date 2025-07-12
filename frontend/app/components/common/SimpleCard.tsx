// ログイン画面など1つのカードを表示するときに使用

export default function SimpleCard({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="w-full max-w-md bg-card rounded-md shadow-md border p-6 mx-4">
      {children}
    </div>
  );
}
