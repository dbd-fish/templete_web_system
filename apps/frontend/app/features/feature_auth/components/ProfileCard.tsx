import { LoaderDataType } from '~/commons/utils/types';
import { useLoaderData } from 'react-router';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Button } from '~/components/ui/button';

export default function ProfileCard() {
  const loaderData = useLoaderData<LoaderDataType>();
  const user = loaderData.user;

  return (
    <Card className="w-full md:w-1/3 text-white rounded-lg shadow-lg p-6 text-center">
      <CardHeader className="flex flex-col items-center">
        <img
          src="https://via.placeholder.com/150"
          alt="Profile"
          className="w-24 h-24 rounded-full shadow-md mb-4 border-2 border-gray-500"
        />
        <CardTitle className="text-lg font-semibold">
          {user?.username}
        </CardTitle>
      </CardHeader>
      <CardContent className="text-center">
        <p className="text-sm text-gray-800">メールアドレス: {user?.email}</p>
        <Button variant="default" className="mt-4 w-full">
          プロフィール編集
        </Button>
      </CardContent>
    </Card>
  );
}
