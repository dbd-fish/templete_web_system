// NOTE: Loader関数やAction関数でロガーが機能しないため、ログ出力をコメントアウトしている
// import pino from 'pino';
// import build from 'pino-abstract-transport';
// import fs from 'fs';
// import path from 'path';
// import { format } from 'date-fns';
// import * as dateFnsTz from 'date-fns-tz'; // 修正：正しいインポート形式
// import { fileURLToPath } from 'url';

// // 現在のファイルのディレクトリを取得し、その1つ上のディレクトリを指定
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);
// const parentDir = path.join(__dirname, '..'); // 1つ上のディレクトリ

// // ログディレクトリの設定
// const logDir = path.join(parentDir, 'logs');
// if (!fs.existsSync(logDir)) {
//   fs.mkdirSync(logDir);
// }

// // 日付に基づくログファイル名の生成
// const getLogFileName = (): string => {
//   const date = new Date();
//   return path.join(logDir, `app-${format(date, 'yyyy-MM-dd')}.log`);
// };

// // 書き込みストリームの初期化
// let currentLogFile = getLogFileName();
// let logStream = fs.createWriteStream(currentLogFile, { flags: 'a' });

// // 日付のチェックとストリームの更新
// const checkDateAndRotate = (): void => {
//   const newLogFile = getLogFileName();
//   if (newLogFile !== currentLogFile) {
//     logStream.end();
//     currentLogFile = newLogFile;
//     logStream = fs.createWriteStream(currentLogFile, { flags: 'a' });
//   }
// };

// // タイムゾーン設定（日本時間 JST）
// const timeZone = 'Asia/Tokyo';

// // Pinoロガーの定義
// const transport = build(async function (source) {
//   for await (const obj of source) {
//     checkDateAndRotate();

//     // 現在の日時を日本時間（JST）に変換して取得
//     const now = new Date();
//     const zonedDate = dateFnsTz.toZonedTime(now, timeZone); // 修正：正しいインポート形式に対応
//     const timestamp = format(zonedDate, 'yyyy-MM-dd HH:mm:ss.SSS'); // 日本時間でフォーマット
//     obj.time = timestamp; // `time` フィールドをカスタマイズ

//     // 動的カスタムフィールドを正確に含めるよう変更
//     const logMessage = JSON.stringify({
//       time: obj.time,
//       level: obj.level,
//       pid: obj.pid,
//       hostname: obj.hostname,
//       ...obj, // 追加されたすべてのカスタムフィールドを含む
//     });

//     logStream.write(logMessage + '\n');
//   }
// });

// // Pinoロガーの作成
// const logger = pino(transport);

// export default logger;
