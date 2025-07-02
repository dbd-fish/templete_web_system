# app/common/common.py
from datetime import datetime
from zoneinfo import ZoneInfo


def datetime_now()-> datetime:
    """日本時間（Asia/Tokyo）の現在時刻を取得する。
    delete_atカラムに挿入するデータを作成する。
    """
    return datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None, microsecond=0)
