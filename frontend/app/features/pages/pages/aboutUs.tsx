import Header from '~/components/layout/Header';
import Footer from '~/components/layout/Footer';

export default function aboutUs() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow bg-gray-100 flex items-center justify-center">
        <div className="w-full max-w-4xl bg-white rounded-lg shadow-md p-8">
          <div className="flex flex-col md:flex-row items-center justify-center space-y-6 md:space-y-0 md:space-x-6">
            <div className="w-full md:w-2/3 bg-gray-50 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                運営者情報
              </h2>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
