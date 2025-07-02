import { LoaderFunction, redirect, ActionFunction } from 'react-router';
import { userDataLoader } from '~/features/feature_auth/loaders/userDataLoader';
import { AuthenticationError } from '~/commons/utils/errors/AuthenticationError';
import { logoutAction } from '~/features/feature_auth/actions/logoutAction';
// import logger from '~/commons/utils/logger';
import { Button } from '~/components/ui/button';
import Layout from '~/commons/components/Layout';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '~/components/ui/tabs';
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '~/components/ui/accordion';
import { Badge } from '~/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Input } from '~/components/ui/input';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '~/components/ui/select';
import { Switch } from '~/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '~/components/ui/radio-group';
import { Checkbox } from '~/components/ui/checkbox';
import { Textarea } from '~/components/ui/textarea';
import Main from '~/commons/components/Main';

/**
 * ローダー関数:
 * - サーバーサイドで実行され、ユーザー情報を取得
 * - 成功時: ユーザー情報を返す
 * - 失敗時: 401エラーをスロー
 */
export const loader: LoaderFunction = async ({ request }) => {
  // logger.info('[Home Loader] start');
  try {
    const userData = await userDataLoader(request, false);
    const responseBody = {
      user: userData,
    };
    // logger.info('[Home Loader] Successfully retrieved user data');
    // logger.debug('[Home Loader] User data', { userData });

    // 正常なレスポンスを返す
    return new Response(JSON.stringify(responseBody), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    if (error instanceof AuthenticationError) {
      // logger.warn('[Home Loader] AuthenticationError occurred');
      return redirect('/login');
    }

    // logger.error('[Home Loader] Unexpected error occurred', {
    //   error: error,
    // });

    throw new Response('ユーザーデータの取得に失敗しました。', {
      status: 400,
    });
  } finally {
    // logger.info('[Home Loader] end');
  }
};

// NOTE: ログアウトが必要な画面ではこれと似たAction関数を実装する必要あり
/**
 * アクション関数:
 * - クライアントからのアクションを処理
 * - ログアウトやその他のアクションを処理
 */
export const action: ActionFunction = async ({ request }) => {
  // logger.info('[Home Action] start');
  try {
    const formData = await request.formData();
    const actionType = formData.get('_action');

    // logger.debug('[Home Action] Received actionType', { actionType });

    if (actionType === 'logout') {
      const response = await logoutAction(request);
      // logger.info('[Home Action] Logout action processed successfully');
      return response;
    }

    // logger.warn('[Home Action] No valid actionType provided');
    throw new Response('サーバー上で不具合が発生しました', {
      status: 400,
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    // logger.error('[Home Action] Unexpected error occurred', {
    //   error: error
    // });
    throw new Response('サーバー上で予期しないエラーが発生しました', {
      status: 400,
    });
  } finally {
    // logger.info('[Home Action] end');
  }
};
export default function Home() {
  return (
    <Layout>
      <Main>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full max-w-screen-xl px-4">
          {/* 左サイドバー */}
          <aside className="hidden lg:block col-span-2 bg-gray-50 rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              サイドバー1
            </h2>
            <p className="text-gray-600 mb-4">
              ここに左サイドバーの内容を記述します。
            </p>
            <img
              src="https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400"
              alt="サンプル画像"
              className="rounded-lg shadow-md"
            />
          </aside>

          {/* メインコンテンツ */}
          <section className="col-span-12 lg:col-span-8 bg-white rounded-lg shadow p-6 space-y-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-4">
              メインコンテンツ
            </h1>
            <p className="text-gray-600">ホーム画面</p>
            <p className="text-gray-600">
              ここにフォームやUIコンポーネントの例を含めます。
            </p>

            {/* フォームエリア */}
            <form className="space-y-6">
              {/* テキスト入力 */}
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  名前
                </label>
                <Input id="name" placeholder="名前を入力" />
              </div>

              {/* セレクトボックス */}
              <div>
                <label
                  htmlFor="category"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  カテゴリ
                </label>
                <Select>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="カテゴリを選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="option1">オプション1</SelectItem>
                    <SelectItem value="option2">オプション2</SelectItem>
                    <SelectItem value="option3">オプション3</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* トグルスイッチ */}
              <div className="flex items-center space-x-4">
                <label
                  htmlFor="toggle"
                  className="block text-sm font-medium text-gray-700"
                >
                  トグルスイッチ
                </label>
                <Switch id="toggle" />
              </div>

              {/* ラジオボタン */}
              <div>
                <label
                  htmlFor="radio-group"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  ラジオボタン
                </label>
                <RadioGroup id="radio-group" defaultValue="option1">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="option1" id="option1" />
                    <label htmlFor="option1">オプション1</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="option2" id="option2" />
                    <label htmlFor="option2">オプション2</label>
                  </div>
                </RadioGroup>
              </div>

              {/* チェックボックス */}
              <label
                htmlFor="checkbox-group"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                チェックボックス
              </label>
              <div id="checkbox-group">
                <div className="flex items-center space-x-2">
                  <Checkbox id="check1" />
                  <label htmlFor="check1">チェックボックス1</label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="check2" />
                  <label htmlFor="check2">チェックボックス2</label>
                </div>
              </div>

              {/* テキストエリア */}
              <div>
                <label
                  htmlFor="message"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  メッセージ
                </label>
                <Textarea id="message" placeholder="メッセージを入力" />
              </div>

              {/* 送信ボタン */}
              <Button type="submit" className="w-full">
                送信
              </Button>
            </form>

            {/* Tabs コンポーネント */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Tabsのサンプル
              </h2>
              <Tabs defaultValue="tab1">
                <TabsList>
                  <TabsTrigger value="tab1">タブ1</TabsTrigger>
                  <TabsTrigger value="tab2">タブ2</TabsTrigger>
                  <TabsTrigger value="tab3">タブ3</TabsTrigger>
                </TabsList>
                <TabsContent value="tab1">タブ1の内容です。</TabsContent>
                <TabsContent value="tab2">タブ2の内容です。</TabsContent>
                <TabsContent value="tab3">タブ3の内容です。</TabsContent>
              </Tabs>
            </div>

            {/* Accordion コンポーネント */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                アコーディオンのサンプル
              </h2>
              <Accordion type="single" collapsible>
                <AccordionItem value="item1">
                  <AccordionTrigger>項目1</AccordionTrigger>
                  <AccordionContent>
                    項目1の内容です。詳細な情報をここに記述します。
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="item2">
                  <AccordionTrigger>項目2</AccordionTrigger>
                  <AccordionContent>
                    項目2の内容です。詳細な情報をここに記述します。
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>

            {/* Badge コンポーネント */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Badgeのサンプル
              </h2>
              <div className="space-x-2">
                <Badge>デフォルト</Badge>
                <Badge variant="secondary">セカンダリ</Badge>
                <Badge variant="outline">アウトライン</Badge>
              </div>
            </div>

            {/* Card コンポーネント */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Cardのサンプル
              </h2>
              <Card>
                <CardHeader>
                  <CardTitle>カードのタイトル</CardTitle>
                </CardHeader>
                <CardContent>
                  カードの内容をここに記述します。UIコンポーネントとして簡単な表示を行えます。
                </CardContent>
              </Card>
            </div>
          </section>

          {/* 右サイドバー */}
          <aside className="hidden lg:block col-span-2 bg-gray-50 rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              サイドバー2
            </h2>
            <p className="text-gray-600 mb-4">
              ここに右サイドバーの内容を記述します。
            </p>
            {/* フリー素材のGIF */}
            <img
              src="https://media.giphy.com/media/xUPGcxpCV81ebKh7Vu/giphy.gif"
              alt="サンプルGIF"
              className="rounded-lg shadow-md"
            />
          </aside>
        </div>
      </Main>
    </Layout>
  );
}
