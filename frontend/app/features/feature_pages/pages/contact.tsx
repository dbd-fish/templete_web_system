import Header from '~/components/layout/Header';
import Footer from '~/components/layout/Footer';
import { Form } from 'react-router';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';
import { Textarea } from '~/components/ui/textarea';


export default function Contact() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow bg-gray-100 py-16">
        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-xl p-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
            お問い合わせ
          </h1>
          <p className="text-lg text-gray-700 text-center mb-12 leading-relaxed">
            以下のフォームに必要事項をご記入の上、「送信」ボタンを押してください。
            <br />
            お問い合わせ内容を確認後、担当者よりご連絡させていただきます。
          </p>
          <Form method="post" className="space-y-10">
            <div>
              <label
                htmlFor="name"
                className="block text-lg font-medium text-gray-800 mb-2"
              >
                お名前 <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                id="name"
                name="name"
                required
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg p-4"
                placeholder="例: 山田 太郎"
              />
            </div>
            <div>
              <label
                htmlFor="email"
                className="block text-lg font-medium text-gray-800 mb-2"
              >
                メールアドレス <span className="text-red-500">*</span>
              </label>
              <Input
                type="email"
                id="email"
                name="email"
                required
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg p-4"
                placeholder="例: example@example.com"
              />
            </div>
            <div>
              <label
                htmlFor="message"
                className="block text-lg font-medium text-gray-800 mb-2"
              >
                メッセージ <span className="text-red-500">*</span>
              </label>
              <Textarea
                id="message"
                name="message"
                rows={6}
                required
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg p-4"
                placeholder="お問い合わせ内容をご記入ください"
              ></Textarea>
            </div>
            <div className="text-center">
              <Button
                type="submit"
                className="w-full"
              >
                送信する
              </Button>
            </div>
          </Form>
        </div>
      </main>
      <Footer />
    </div>
  );
}
