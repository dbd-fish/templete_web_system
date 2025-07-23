"""
Redisテスト用フィクスチャ
"""

import pytest_asyncio

from api.common.redis_client import redis_client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_redis():
    """テスト用Redisクライアントのセットアップ"""
    print("Redisクライアントの接続を開始")

    try:
        # Redis接続
        await redis_client.connect()
        print("Redisクライアントの接続完了")

        # テスト環境でRedisが正常に動作することを確認
        await redis_client.client.ping()
        print("Redis ping成功")

    except Exception as e:
        print(f"Redis接続エラー: {e}")
        raise

    yield redis_client

    # テスト終了時のクリーンアップ
    print("Redisクライアントの切断を開始")
    try:
        # テストデータをクリア
        await redis_client.client.flushdb()
        print("Redisテストデータをクリア")

        # 接続を切断
        await redis_client.disconnect()
        print("Redisクライアントの切断完了")
    except Exception as e:
        print(f"Redis切断エラー: {e}")
