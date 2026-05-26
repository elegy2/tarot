"""集中管理配色、字号、间距常量。

改自原 app/theme.py,并新增 App 风格所需的面板色、渐变色、
字号层级、间距刻度,保持视觉统一。
"""
from __future__ import annotations

from kivy.metrics import dp, sp


# ---------- 颜色 ----------
COLOR_BG_TOP = (0.05, 0.03, 0.10, 1)
COLOR_BG_BOTTOM = (0.01, 0.01, 0.04, 1)
COLOR_BG_DEEP = (0x0B / 255, 0x06 / 255, 0x14 / 255, 1)
COLOR_BG_PURPLE = (0x12 / 255, 0x0A / 255, 0x24 / 255, 1)
COLOR_BG_INDIGO = (0x1B / 255, 0x12 / 255, 0x33 / 255, 1)

COLOR_PANEL = (0.10, 0.07, 0.16, 0.88)
COLOR_PANEL_DARK = (0.06, 0.04, 0.10, 0.92)

COLOR_PRIMARY = (0x6B / 255, 0x46 / 255, 0xC1 / 255, 1)
COLOR_GOLD = (0.86, 0.68, 0.32, 1)
COLOR_GOLD_SOFT = (0.86, 0.68, 0.32, 0.35)
COLOR_SILVER = (0xC0 / 255, 0xC0 / 255, 0xD8 / 255, 1)
COLOR_LIGHT_PURPLE = (0xB7 / 255, 0x9C / 255, 0xED / 255, 1)

COLOR_TEXT = (0.94, 0.90, 0.82, 1)
COLOR_TEXT_SUB = (0.70, 0.65, 0.78, 1)
COLOR_TEXT_MUTED = (0.70, 0.65, 0.58, 1)
COLOR_TEXT_HINT = (0x80 / 255, 0x78 / 255, 0x98 / 255, 1)

COLOR_ERROR = (0.95, 0.42, 0.42, 1)
COLOR_SUCCESS = (0x6B / 255, 0xCB / 255, 0x9C / 255, 1)


# ---------- 间距 ----------
def SPACE_XS(): return dp(4)
def SPACE_SM(): return dp(8)
def SPACE_MD(): return dp(16)
def SPACE_LG(): return dp(24)
def SPACE_XL(): return dp(32)


# ---------- 字号 ----------
def FS_TITLE(): return sp(28)
def FS_HEADER(): return sp(20)
def FS_SUBTITLE(): return sp(16)
def FS_BODY(): return sp(14)
def FS_SMALL(): return sp(12)
def FS_TINY(): return sp(11)
def FS_BUTTON(): return sp(15)


# ---------- 圆角 ----------
def RADIUS_CARD(): return dp(16)
def RADIUS_BTN(): return dp(14)
def RADIUS_PANEL(): return dp(18)


def hex_to_rgba(hex_str: str, alpha: float = 1.0):
    hex_str = hex_str.lstrip("#")
    return (
        int(hex_str[0:2], 16) / 255,
        int(hex_str[2:4], 16) / 255,
        int(hex_str[4:6], 16) / 255,
        alpha,
    )
