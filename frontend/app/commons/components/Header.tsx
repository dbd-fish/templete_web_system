// NOTE: バックエンド連携するときに見直す必要あり
import LoggedInHeader from '~/commons/components/header/LoggedInHeade';
import LoggedOutHeader from '~/commons/components/header/LoggedOutHeader';
import { useLoaderData } from 'react-router';
import { LoaderDataType } from '~/commons/utils/types';

export default function Header() {
  // ローダー関数で取得したユーザー情報を取得
  // NOTE: 共通のLoader関数の戻り値の型定義を使用
  const loaderData = useLoaderData<LoaderDataType>();

  // 認証状況に応じて表示を切り替える
  if (loaderData?.user) {
    return <LoggedInHeader />;
  } else {
    return <LoggedOutHeader />;
  }
}
