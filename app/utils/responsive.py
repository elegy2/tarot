"""响应式工具:根据当前窗口宽度返回断点、字号、间距、卡牌尺寸等。

断点(以 dp 为单位):
    < 380dp     compact   极小屏(老款手机、折叠屏内屏一半)
    < 720dp     phone     普通手机竖屏
    >= 720dp    wide      平板 / 桌面调试窗口
"""
from __future__ import annotations

from kivy.metrics import dp, sp


# 卡牌默认竖版比例(高/宽)
CARD_RATIO = 7 / 4


def screen_type(width: float) -> str:
    if width < dp(380):
        return "compact"
    if width < dp(720):
        return "phone"
    return "wide"


def page_padding(width: float):
    """统一页面四周 padding,返回 [l, t, r, b]。"""
    st = screen_type(width)
    if st == "compact":
        return [dp(10), dp(12), dp(10), dp(10)]
    if st == "phone":
        return [dp(14), dp(16), dp(14), dp(14)]
    return [dp(24), dp(20), dp(24), dp(20)]


def section_spacing(width: float) -> float:
    return dp(6) if screen_type(width) == "compact" else dp(10)


def title_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(24)
    if st == "phone":
        return sp(28)
    return sp(34)


def header_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(18)
    if st == "phone":
        return sp(20)
    return sp(22)


def body_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(13)
    if st == "phone":
        return sp(14)
    return sp(15)


def small_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(11)
    return sp(12)


def button_height(width: float):
    st = screen_type(width)
    if st == "compact":
        return dp(46)
    if st == "phone":
        return dp(52)
    return dp(56)


def content_max_width(width: float):
    """限制超宽屏的内容宽度,避免文字一行铺满。"""
    return min(width * 0.94, dp(720))


def cards_orientation(width: float) -> str:
    """三牌阵/凯尔特等多牌阵的排列方向。"""
    return "vertical" if width < dp(540) else "horizontal"


def cards_spacing(width: float) -> float:
    """卡片之间的间距,随屏幕宽度轻微调整。"""
    st = screen_type(width)
    if st == "compact":
        return dp(10)
    if st == "phone":
        return dp(14)
    return dp(18)


def card_extra_h(width: float) -> float:
    """卡片下方文字区(位置名 + 牌名)预留的额外高度。"""
    st = screen_type(width)
    if st == "compact":
        return dp(70)
    if st == "phone":
        return dp(84)
    return dp(92)


def card_size(width: float, height: float, count: int = 3):
    """根据当前可用宽高,计算每张卡牌尺寸,返回 (card_w, card_h)。"""
    orientation = cards_orientation(width)
    spacing = cards_spacing(width)
    if orientation == "vertical":
        # 纵排:卡宽 = 屏宽 * 0.7,但限制上下界
        card_w = min(width - dp(40), dp(260))
        card_w = max(card_w, dp(150))
        card_h = card_w * CARD_RATIO
        # 同时不允许卡高超过屏高的 0.55
        max_h = max(height * 0.55, dp(240))
        if card_h > max_h:
            card_h = max_h
            card_w = card_h / CARD_RATIO
    else:
        total_space = spacing * (count + 1)
        each_w = (width - dp(40) - total_space) / max(count, 1)
        card_w = max(dp(120), min(each_w, dp(220)))
        card_h = card_w * CARD_RATIO
        max_h = max(height * 0.62, dp(280))
        if card_h > max_h:
            card_h = max_h
            card_w = card_h / CARD_RATIO
    return card_w, card_h
