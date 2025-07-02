import { Link } from 'react-router';

export default function SiteTitle() {
  return (
    <Link to="/" className="text-xl font-bold mb-2 md:mb-0 hover:underline">
      サンプルサイト
    </Link>
  );
}
