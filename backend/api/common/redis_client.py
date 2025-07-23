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
    SESSION_METRICS_PREFIX = "session_metrics:"

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

    async def record_session_metrics(self, action: str, user_email: str | None = None, device_info: dict[str, str] | None = None) -> None:
        """セッション操作のメトリクスを記録

        Args:
            action (str): アクション名（login, refresh, logout等）
            user_email (str, optional): ユーザーメールアドレス
            device_info (Dict[str, str], optional): デバイス情報
        """
        logger.info("record_session_metrics - start", action=action)
        try:
            timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
            metric_data = {
                "action": action,
                "timestamp": timestamp,
                "user_email": user_email or "anonymous",
                "device_info": json.dumps(device_info or {}),
            }

            # 日別メトリクスキーを生成
            date_key = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")
            metric_key = f"{self.SESSION_METRICS_PREFIX}{date_key}:{action}"

            # カウンターを増加
            await cast(Any, self.redis.client.incr(metric_key))
            await cast(Any, self.redis.client.expire(metric_key, 86400 * 7))  # 7日間保持

            # 詳細ログをリストに追加（最新100件のみ保持）
            detail_key = f"{self.SESSION_METRICS_PREFIX}detail:{date_key}"
            await cast(Any, self.redis.client.lpush(detail_key, json.dumps(metric_data)))
            await cast(Any, self.redis.client.ltrim(detail_key, 0, 99))  # 最新100件のみ保持
            await cast(Any, self.redis.client.expire(detail_key, 86400 * 7))  # 7日間保持

            # 異常パターン検知
            await self._detect_anomaly_patterns(action, user_email, device_info)

            logger.info("record_session_metrics - success", action=action)

        except Exception as e:
            logger.error("record_session_metrics - failed", action=action, error=str(e))
        finally:
            logger.info("record_session_metrics - end")

    async def _detect_anomaly_patterns(self, action: str, user_email: str | None = None, device_info: dict[str, str] | None = None) -> None:
        """異常パターンの検知と記録

        Args:
            action (str): アクション名
            user_email (str, optional): ユーザーメールアドレス
            device_info (Dict[str, str], optional): デバイス情報
        """
        try:
            if not user_email:
                return

            current_time = datetime.now(ZoneInfo("Asia/Tokyo"))

            # 1時間以内の同一ユーザーのアクション数をチェック
            hour_key = current_time.strftime("%Y-%m-%d:%H")
            user_hour_key = f"user_activity:{user_email}:{hour_key}"

            # 現在の1時間のアクション数を取得・増加
            current_count = await self.redis.client.incr(user_hour_key)
            await self.redis.client.expire(user_hour_key, 3600)  # 1時間で期限切れ

            # 異常パターンの閾値
            thresholds = {
                "login": 10,  # 1時間に10回以上のログイン
                "refresh": 100,  # 1時間に100回以上のトークン更新
                "token_created": 15,  # 1時間に15回以上のトークン作成
            }

            threshold = thresholds.get(action, 50)  # デフォルト閾値

            if current_count >= threshold:
                # 異常パターンを記録
                anomaly_data = {
                    "user_email": user_email,
                    "action": action,
                    "count": current_count,
                    "threshold": threshold,
                    "timestamp": current_time.isoformat(),
                    "device_info": device_info or {},
                    "severity": "HIGH" if current_count >= threshold * 2 else "MEDIUM",
                }

                # 異常パターンログに記録
                anomaly_key = f"security_anomaly:{current_time.strftime('%Y-%m-%d')}"
                await cast(Any, self.redis.client.lpush(anomaly_key, json.dumps(anomaly_data)))
                await cast(Any, self.redis.client.ltrim(anomaly_key, 0, 999))  # 最新1000件保持
                await cast(Any, self.redis.client.expire(anomaly_key, 86400 * 30))  # 30日間保持

                logger.warning("security_anomaly_detected", user_email=user_email, action=action, count=current_count, threshold=threshold, severity=anomaly_data["severity"])

        except Exception as e:
            logger.error("_detect_anomaly_patterns - failed", error=str(e))

    async def get_security_anomalies(self, date: str | None = None, limit: int = 100) -> list[dict]:
        """セキュリティ異常パターンを取得

        Args:
            date (str, optional): 対象日付（YYYY-MM-DD形式）
            limit (int): 取得件数上限

        Returns:
            List[Dict]: 異常パターンのリスト
        """
        if not date:
            date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

        logger.info("get_security_anomalies - start", date=date, limit=limit)
        anomalies = []
        try:
            anomaly_key = f"security_anomaly:{date}"
            anomaly_logs = await cast(Any, self.redis.client.lrange(anomaly_key, 0, limit - 1))

            for log in anomaly_logs:
                try:
                    anomaly_data = json.loads(log)
                    anomalies.append(anomaly_data)
                except json.JSONDecodeError:
                    continue

            logger.info("get_security_anomalies - success", date=date, anomaly_count=len(anomalies))
            return anomalies

        except Exception as e:
            logger.error("get_security_anomalies - failed", date=date, error=str(e))
            return anomalies
        finally:
            logger.info("get_security_anomalies - end")

    async def get_session_metrics(self, date: str | None = None) -> dict[str, int]:
        """セッションメトリクスを取得

        Args:
            date (str, optional): 対象日付（YYYY-MM-DD形式、未指定時は今日）

        Returns:
            Dict[str, int]: アクション別のカウント
        """
        if not date:
            date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

        logger.info("get_session_metrics - start", date=date)
        metrics = {}
        try:
            # パターンマッチでメトリクスキーを取得
            pattern = f"{self.SESSION_METRICS_PREFIX}{date}:*"
            keys = await self.redis.client.keys(pattern)

            for key in keys:
                action = key.split(":")[-1]
                count = await self.redis.client.get(key)
                metrics[action] = int(count) if count else 0

            logger.info("get_session_metrics - success", date=date, metrics=metrics)
            return metrics

        except Exception as e:
            logger.error("get_session_metrics - failed", date=date, error=str(e))
            return metrics
        finally:
            logger.info("get_session_metrics - end")


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
