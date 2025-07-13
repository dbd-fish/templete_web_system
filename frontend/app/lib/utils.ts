import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * shadcn/ui で使用される Tailwind CSS クラス名統合ユーティリティ
 *
 * @description
 * clsx と tailwind-merge を組み合わせて、条件付きクラス名と
 * Tailwind CSS の重複クラスを適切に処理します。
 *
 * @param inputs - clsx に渡すクラス値（文字列、オブジェクト、配列など）
 * @returns 統合されたクラス名文字列
 *
 * @example
 * ```typescript
 * // 基本的な使用法
 * cn("p-4", "bg-blue-500") // "p-4 bg-blue-500"
 *
 * // 条件付きクラス
 * cn("p-4", { "bg-red-500": isError, "bg-green-500": isSuccess })
 *
 * // Tailwind の重複クラス解決
 * cn("p-4 p-2") // "p-2" (後のクラスが優先)
 * cn("bg-red-500 bg-blue-500") // "bg-blue-500" (後のクラスが優先)
 * ```
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
