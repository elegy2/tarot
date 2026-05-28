"""响应式工具:根据当前窗口宽度返回断点、字号、间距、卡牌尺寸等。

断点(以 dp 为单位):
    < 360dp     compact   极小屏(老款手机、折叠屏内屏一半)
    < 720dp     phone     普通手机竖屏
    >= 720dp    wide      平板 / 桌面调试窗口

手机适配优化:
- 卡牌尺寸根据屏幕实际可用空间动态计算
- 考虑状态栏、导航栏、软键盘等系统 UI 占用
- 确保在 18:9、19.5:9、20:9 等长屏手机上正常显示
- 纵向布局时卡牌宽度不超过屏宽 75%
- 横向布局时自动计算合适的卡牌数量和间距
"""
from __future__ import annotations

from kivy.metrics import dp, sp


# 卡牌默认竖版比例(高/宽)
CARD_RATIO = 7 / 4


def screen_type(width: float) -> str:
    """根据屏幕宽度返回设备类型。"""
    if width < dp(360):
        return "compact"
    if width < dp(720):
        return "phone"
    return "wide"


def page_padding(width: float):
    """统一页面四周 padding,返回 [l, t, r, b]。"""
    st = screen_type(width)
    if st == "compact":
        return [dp(8), dp(10), dp(8), dp(8)]
    if st == "phone":
        return [dp(12), dp(14), dp(12), dp(12)]
    return [dp(24), dp(20), dp(24), dp(20)]


def section_spacing(width: float) -> float:
    return dp(6) if screen_type(width) == "compact" else dp(10)


def title_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(22)
    if st == "phone":
        return sp(28)
    return sp(34)


def header_font_size(width: float):
    st = screen_type(width)
    if st == "compact":
        return sp(17)
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
        return dp(44)
    if st == "phone":
        return dp(50)
    return dp(56)


def content_max_width(width: float):
    """限制超宽屏的内容宽度,避免文字一行铺满。"""
    return min(width * 0.94, dp(720))


def cards_orientation(width: float) -> str:
    """三牌阵/凯尔特等多牌阵的排列方向。

    手机竖屏(<540dp)强制纵向，平板/横屏可横向排列。
    """
    return "vertical" if width < dp(540) else "horizontal"


def cards_spacing(width: float) -> float:
    """卡片之间的间距,随屏幕宽度轻微调整。"""
    st = screen_type(width)
    if st == "compact":
        return dp(8)
    if st == "phone":
        return dp(12)
    return dp(18)


def card_extra_h(width: float) -> float:
    """卡片下方文字区(位置名 + 牌名)预留的额外高度。"""
    st = screen_type(width)
    if st == "compact":
        return dp(66)
    if st == "phone":
        return dp(80)
    return dp(92)


def card_size(width: float, height: float, count: int = 3):
    """根据当前可用宽高,计算每张卡牌尺寸,返回 (card_w, card_h)。

    优化策略:
    1. 纵向布局: 卡宽 = min(屏宽 * 0.72, 280dp), 卡高不超过屏高 * 0.50
    2. 横向布局: 根据卡片数量和间距动态计算，确保所有卡片能放下
    3. 极小屏(<360dp): 进一步缩小卡片，确保可用性
    4. 长屏手机(height/width > 2.0): 适当增加卡片高度上限
    """
    orientation = cards_orientation(width)
    spacing = cards_spacing(width)
    st = screen_type(width)

    # 计算屏幕长宽比，用于判断是否为长屏手机
    aspect_ratio = height / max(width, 1)
    is_tall_screen = aspect_ratio > 2.0  # 18:9 及以上

    if orientation == "vertical":
        # 纵向布局: 卡片居中显示，宽度占屏宽 65-70%
        if st == "compact":
            # 极小屏: 卡宽最多 230dp，占屏宽 65-70%
            card_w = min(width * 0.68, dp(230))
            card_w = max(card_w, dp(140))
        else:
            # 普通手机: 卡宽最多 260dp，占屏宽 68-72%
            card_w = min(width * 0.70, dp(260))
            card_w = max(card_w, dp(160))

        card_h = card_w * CARD_RATIO

        # 卡高限制: 不超过屏高的 48%（长屏可放宽到 50%）
        max_h_ratio = 0.50 if is_tall_screen else 0.48
        max_h = height * max_h_ratio

        # 极小屏额外限制
        if st == "compact":
            max_h = min(max_h, dp(400))

        if card_h > max_h:
            card_h = max_h
            card_w = card_h / CARD_RATIO
    else:
        # 横向布局: 根据卡片数量计算合适的宽度
        # 总可用宽度 = 屏宽 - 左右边距 - 所有间距
        available_w = width - dp(24) - spacing * (count + 1)
        each_w = available_w / max(count, 1)

        # 卡宽范围: 100dp ~ 220dp
        card_w = max(dp(100), min(each_w, dp(220)))
        card_h = card_w * CARD_RATIO

        # 卡高限制: 不超过屏高的 60%（长屏可放宽到 65%）
        max_h_ratio = 0.65 if is_tall_screen else 0.60
        max_h = height * max_h_ratio

        if card_h > max_h:
            card_h = max_h
            card_w = card_h / CARD_RATIO

    # 最终保底: 确保卡片不会太小
    card_w = max(card_w, dp(120))
    card_h = max(card_h, dp(210))

    return card_w, card_h
