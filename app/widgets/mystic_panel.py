"""神秘暗色面板:用于包裹 AI 解读结果、卡牌列表等内容。

variant:
    plain         默认平面
    elevated      带柔和阴影,视觉抬高
    highlighted   左侧金色 accent 条,用于重点信息

外观:
- 深紫半透明圆角填充
- 金色细描边,且在内层再画一道极浅的高光
- 顶部一道隐约金色横线,模拟"翻页折角"
"""
from __future__ import annotations

from kivy.graphics import Color, Line, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty, ListProperty, NumericProperty, StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from app.utils import theme as T


class MysticPanel(BoxLayout):
    bg_color = ListProperty(list(T.COLOR_PANEL))
    border_color = ListProperty(list(T.COLOR_GOLD_SOFT))
    accent_color = ListProperty(list(T.COLOR_GOLD))
    radius = NumericProperty(dp(16))
    border_width = NumericProperty(1.2)
    variant = StringProperty("plain")  # plain / elevated / highlighted
    show_top_divider = BooleanProperty(True)

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", [dp(14), dp(12), dp(14), dp(14)])
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        self.bind(
            size=self._redraw, pos=self._redraw,
            bg_color=self._redraw, border_color=self._redraw,
            accent_color=self._redraw, radius=self._redraw,
            variant=self._redraw, show_top_divider=self._redraw,
        )
        self._redraw()

    def _redraw(self, *_a):
        self.canvas.before.clear()
        with self.canvas.before:
            # 阴影层(elevated):放在最下层,稍微外扩,做柔和阴影
            if self.variant == "elevated":
                Color(0, 0, 0, 0.22)
                ext = dp(3)
                RoundedRectangle(
                    pos=(self.x - ext, self.y - ext - dp(2)),
                    size=(self.width + 2 * ext,
                          self.height + 2 * ext),
                    radius=[self.radius + ext],
                )

            # 主背景
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius])

            # 内层渐隐高光层(模拟玻璃质感)
            Color(1, 1, 1, 0.025)
            RoundedRectangle(
                pos=(self.x + dp(1), self.y + self.height * 0.55),
                size=(self.width - dp(2), self.height * 0.45 - dp(1)),
                radius=[self.radius - dp(1)],
            )

            # 描边
            Color(*self.border_color)
            Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, self.radius,
            ), width=self.border_width)

            # 内层金色细线
            r2 = max(self.radius - dp(2), dp(2))
            Color(self.border_color[0], self.border_color[1],
                  self.border_color[2], self.border_color[3] * 0.5)
            Line(rounded_rectangle=(
                self.x + dp(2), self.y + dp(2),
                self.width - dp(4), self.height - dp(4), r2,
            ), width=1.0)

            # 顶部隐约金色横线
            if self.show_top_divider and self.height > dp(40):
                Color(self.accent_color[0], self.accent_color[1],
                      self.accent_color[2], 0.18)
                pad_x = self.radius + dp(4)
                y = self.y + self.height - dp(8)
                Line(points=[self.x + pad_x, y,
                             self.x + self.width - pad_x, y],
                     width=1.0)

            # 高亮 variant 左侧 accent 条
            if self.variant == "highlighted":
                Color(*self.accent_color)
                bar_x = self.x + dp(6)
                bar_y = self.y + dp(10)
                bar_h = max(self.height - dp(20), dp(10))
                Rectangle(pos=(bar_x, bar_y), size=(dp(3), bar_h))
