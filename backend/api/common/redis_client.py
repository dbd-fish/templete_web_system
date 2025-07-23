"""
Redis接続管理とセッションストア機能
"""

import json
import uuid
from datetime import datetime
from typing import Any, cast
from zoneinfo import ZoneInfo

import redis.asyncio as aioredis
import structlog
from redis.asyncio import Redis

from api.common.setting import setting

# ログの設定
logger = structlog.get_logger()


class RedisClient:
    """Redis接続管理クラス"""

    def __init__(self):
        self._redis: Redis | None = None
        self._pool = None

    async def connect(self) -> None:
        """Redisサーバーに接続"""
        logger.info("redis_connect - start")
        try:
            redis_url = f"redis://{setting.REDIS_HOST}:{setting.REDIS_PORT}/{setting.REDIS_DB}"
            if setting.REDIS_PASSWORD:
                redis_url = f"redis://:{setting.REDIS_PASSWORD}@{setting.REDIS_HOST}:{setting.REDIS_PORT}/{setting.REDIS_DB}"

            self._redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)

            # 接続テスト
            await self._redis.ping()
            logger.info("redis_connect - success")

        except Exception as e:
            logger.error("redis_connect - failed", error=str(e))
            raise
        finally:
            logger.info("redis_connect - end")

    async def disconnect(self) -> None:
        """Redis接続を切断"""
        logger.info("redis_disconnect - start")
        try:
            if self._redis:
                await self._redis.aclose()
                self._redis = None
            logger.info("redis_disconnect - success")
        except Exception as e:
            logger.error("redis_disconnect - failed", error=str(e))
        finally:
            logger.info("redis_disconnect - end")

    @property
    def client(self) -> Redis:
        """Redisクライアントを取得"""
        if not self._redis:
            raise RuntimeError("Redis client is not connected")
        return self._redis


# グローバルなRedisクライアントインスタンス
redis_client = RedisClient()


class SessionStore:
    """Redisベースのセッション管理クラス"""

    REFRESH_TOKEN_PREFIX = "refresh_token:"
    SESSION_PREFIX = "session:"
    USER_SESSIONS_PREFIX = "user_sessions:"

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client

    async def store_refresh_token(self, refresh_token: str, user_email: str, device_info: dict[str, str] | None = None) -> None:
        """リフレッシュトークンをRedisに保存

        Args:
            refresh_token (str): リフレッシュトークン
            user_email (str): ユーザーメールアドレス
            device_info (Dict[str, str], optional): デバイス情報
        """
        logger.info("store_refresh_token - start", user_email=user_email)
        try:
            # リフレッシュトークン情報
            token_data = {
                "user_email": user_email,
                "created_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
                "device_info": json.dumps(device_info or {}),
                "last_used": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
            }

            # リフレッシュトークンを保存
            await cast(Any, self.redis.client.hset(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}", mapping=token_data))
            await cast(Any, self.redis.client.expire(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}", setting.REDIS_SESSION_EXPIRE_SECONDS))

            # ユーザーのセッション一覧に追加
            await cast(Any, self.redis.client.sadd(f"{self.USER_SESSIONS_PREFIX}{user_email}", refresh_token))
            await cast(Any, self.redis.client.expire(f"{self.USER_SESSIONS_PREFIX}{user_email}", setting.REDIS_SESSION_EXPIRE_SECONDS))

            logger.info("store_refresh_token - success", user_email=user_email)

        except Exception as e:
            logger.error("store_refresh_token - failed", user_email=user_email, error=str(e))
            raise
        finally:
            logger.info("store_refresh_token - end")

    async def validate_refresh_token(self, refresh_token: str) -> str | None:
        """リフレッシュトークンを検証してユーザーメールを取得

        Args:
            refresh_token (str): 検証対象のリフレッシュトークン

        Returns:
            Optional[str]: ユーザーメールアドレス（無効な場合はNone）
        """
        logger.info("validate_refresh_token - start")
        try:
            token_data = await cast(Any, self.redis.client.hgetall(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}"))

            if not token_data:
                logger.info("validate_refresh_token - token not found")
                return None

            user_email = token_data.get("user_email")
            if not user_email:
                logger.error("validate_refresh_token - user_email not found in token data")
                return None

            # 最終使用時刻を更新
            await cast(Any, self.redis.client.hset(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}", "last_used", datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()))

            logger.info("validate_refresh_token - success", user_email=user_email)
            return user_email

        except Exception as e:
            logger.error("validate_refresh_token - failed", error=str(e))
            return None
        finally:
            logger.info("validate_refresh_token - end")

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        """単一のリフレッシュトークンを無効化

        Args:
            refresh_token (str): 無効化対象のリフレッシュトークン
        """
        logger.info("revoke_refresh_token - start")
        try:
            # トークン情報を取得してからユーザーセッション一覧から削除
            token_data = await cast(Any, self.redis.client.hgetall(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}"))
            if token_data and token_data.get("user_email"):
                await cast(Any, self.redis.client.srem(f"{self.USER_SESSIONS_PREFIX}{token_data['user_email']}", refresh_token))

            # リフレッシュトークンを削除
            await self.redis.client.delete(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}")

            logger.info("revoke_refresh_token - success")

        except Exception as e:
            logger.error("revoke_refresh_token - failed", error=str(e))
        finally:
            logger.info("revoke_refresh_token - end")

    async def revoke_all_refresh_tokens_for_user(self, user_email: str) -> int:
        """特定ユーザーの全リフレッシュトークンを無効化

        Args:
            user_email (str): 対象ユーザーのメールアドレス

        Returns:
            int: 無効化されたトークン数
        """
        logger.info("revoke_all_refresh_tokens_for_user - start", user_email=user_email)
        revoked_count = 0
        try:
            # ユーザーのセッション一覧を取得
            refresh_tokens = await cast(Any, self.redis.client.smembers(f"{self.USER_SESSIONS_PREFIX}{user_email}"))

            if refresh_tokens:
                # 各リフレッシュトークンを削除
                for refresh_token in refresh_tokens:
                    await self.redis.client.delete(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}")
                    revoked_count += 1

                # ユーザーセッション一覧を削除
                await self.redis.client.delete(f"{self.USER_SESSIONS_PREFIX}{user_email}")

            logger.info("revoke_all_refresh_tokens_for_user - success", user_email=user_email, revoked_count=revoked_count)
            return revoked_count

        except Exception as e:
            logger.error("revoke_all_refresh_tokens_for_user - failed", user_email=user_email, error=str(e))
            return revoked_count
        finally:
            logger.info("revoke_all_refresh_tokens_for_user - end")

    async def get_user_sessions(self, user_email: str) -> list[dict[str, str]]:
        """ユーザーのアクティブセッション一覧を取得

        Args:
            user_email (str): ユーザーメールアドレス

        Returns:
            List[Dict[str, str]]: セッション情報のリスト
        """
        logger.info("get_user_sessions - start", user_email=user_email)
        sessions = []
        try:
            # ユーザーのセッション一覧を取得
            refresh_tokens = await cast(Any, self.redis.client.smembers(f"{self.USER_SESSIONS_PREFIX}{user_email}"))

            for refresh_token in refresh_tokens:
                token_data = await cast(Any, self.redis.client.hgetall(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}"))
                if token_data:
                    session_info = {
                        "refresh_token": refresh_token,
                        "created_at": token_data.get("created_at", ""),
                        "last_used": token_data.get("last_used", ""),
                        "device_info": json.loads(token_data.get("device_info", "{}")),
                    }
                    sessions.append(session_info)

            logger.info("get_user_sessions - success", user_email=user_email, session_count=len(sessions))
            return sessions

        except Exception as e:
            logger.error("get_user_sessions - failed", user_email=user_email, error=str(e))
            return sessions
        finally:
            logger.info("get_user_sessions - end")

    async def revoke_session_by_device(self, user_email: str, device_id: str) -> bool:
        """デバイス別セッション無効化

        Args:
            user_email (str): ユーザーメールアドレス
            device_id (str): デバイスID

        Returns:
            bool: 無効化成功の可否
        """
        logger.info("revoke_session_by_device - start", user_email=user_email, device_id=device_id)
        try:
            # ユーザーのセッション一覧を取得
            refresh_tokens = await cast(Any, self.redis.client.smembers(f"{self.USER_SESSIONS_PREFIX}{user_email}"))

            for refresh_token in refresh_tokens:
                token_data = await cast(Any, self.redis.client.hgetall(f"{self.REFRESH_TOKEN_PREFIX}{refresh_token}"))
                if token_data:
                    device_info = json.loads(token_data.get("device_info", "{}"))
                    if device_info.get("device_id") == device_id:
                        await self.revoke_refresh_token(refresh_token)
                        logger.info("revoke_session_by_device - success", user_email=user_email, device_id=device_id)
                        return True

            logger.info("revoke_session_by_device - device not found", user_email=user_email, device_id=device_id)
            return False

        except Exception as e:
            logger.error("revoke_session_by_device - failed", user_email=user_email, device_id=device_id, error=str(e))
            return False
        finally:
            logger.info("revoke_session_by_device - end")


# グローバルなセッションストアインスタンス
session_store = SessionStore(redis_client)


async def get_device_info_from_request(request) -> dict[str, str]:
    """リクエストからデバイス情報を抽出

    Args:
        request: FastAPI Requestオブジェクト

    Returns:
        Dict[str, str]: デバイス情報
    """
    return {
        "device_id": str(uuid.uuid4()),  # 実際にはより永続的なデバイスIDを生成
        "user_agent": request.headers.get("user-agent", "unknown"),
        "ip_address": request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "unknown"),
        "platform": _extract_platform_from_user_agent(request.headers.get("user-agent", "")),
    }


def _extract_platform_from_user_agent(user_agent: str) -> str:
    """User-Agentからプラットフォームを抽出

    Args:
        user_agent (str): User-Agent文字列

    Returns:
        str: プラットフォーム名
    """
    user_agent_lower = user_agent.lower()

    if "mobile" in user_agent_lower or "android" in user_agent_lower:
        return "mobile"
    elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        return "ios"
    elif "windows" in user_agent_lower:
        return "windows"
    elif "macintosh" in user_agent_lower or "mac os" in user_agent_lower:
        return "macos"
    elif "linux" in user_agent_lower:
        return "linux"
    else:
        return "unknown"
