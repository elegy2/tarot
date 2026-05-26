"""通用工具。"""
from __future__ import annotations

import datetime as dt


def format_now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_record_time(iso_str: str) -> str:
    """把 ISO 时间转换成更易读的形式,失败时原样返回。"""
    try:
        d = dt.datetime.fromisoformat(iso_str)
        return d.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso_str
