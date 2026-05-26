"""兼容旧的 `from app import theme` 写法。

所有常量现在集中在 app/utils/theme.py,这里做一层平滑转发,
并保留原有的命名,避免旧代码在 import 时报错。
"""
from __future__ import annotations

from app.utils.theme import (
    COLOR_BG_DEEP as BG_DEEP,
    COLOR_BG_PURPLE as BG_PURPLE,
    COLOR_BG_INDIGO as BG_INDIGO,
    COLOR_PRIMARY as PRIMARY,
    COLOR_GOLD as ACCENT_GOLD,
    COLOR_SILVER as ACCENT_SILVER,
    COLOR_LIGHT_PURPLE as ACCENT_LIGHT_PURPLE,
    COLOR_TEXT as TEXT_MAIN,
    COLOR_TEXT_SUB as TEXT_SUB,
    COLOR_TEXT_HINT as TEXT_HINT,
    COLOR_ERROR as ERROR,
    COLOR_SUCCESS as SUCCESS,
    hex_to_rgba,
)
