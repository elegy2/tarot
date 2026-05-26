"""神秘风格按钮:深紫圆角底 + 金色描边 + 多 variant + 按下缩放反馈。

variant:
    primary    填充紫色,主入口按钮
    secondary  默认深底金描边
    ghost      透明底 + 金色描边,弱化按钮
    danger     红色描边,用于删除/清空

leading_symbol: 可选,左侧的 SymbolBadge 符号名(参考 widgets.symbol_badge)。
"""
from __future__ import annotations

from kivy.animation import Animation
from kivy.graphics import (
    Color, Line, PopMatrix, PushMatrix, RoundedRectangle, Scale,
)
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty, ListProperty, NumericProperty, StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label

from app.utils import theme as T


_VARIANT_PRESETS = {
    "primary": {
        "bg_color": list(T.COLOR_PRIMARY),
        "border_color": list(T.COLOR_GOLD),
        "color": list(T.COLOR_TEXT),
    },
    "secondary": {
        "bg_color": list(T.COLOR_BG_INDIGO),
        "border_color": list(T.COLOR_GOLD),
        "color": list(T.COLOR_TEXT),
    },
    "ghost": {
        "bg_color": [0, 0, 0, 0],
        "border_color": [T.COLOR_GOLD[0], T.COLOR_GOLD[1],
                         T.COLOR_GOLD[2], 0.55],
        "color": list(T.COLOR_TEXT),
    },
    "danger": {
        "bg_color": list(T.COLOR_BG_INDIGO),
        "border_color": list(T.COLOR_ERROR),
        "color": [T.COLOR_ERROR[0], T.COLOR_ERROR[1],
                  T.COLOR_ERROR[2], 1.0],
    },
}


class MysticButton(ButtonBehavior, Label):
    bg_color = ListProperty(list(T.COLOR_BG_INDIGO))
    border_color = ListProperty(list(T.COLOR_GOLD))
    radius = NumericProperty(dp(14))
    pressed_flag = BooleanProperty(False)
    loading = BooleanProperty(False)
    loading_text = StringProperty("正在解读……")
    variant = StringProperty("secondary")
    press_scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        # 先确定 variant,再让显式 kwargs 覆盖默认值
        variant = kwargs.pop("variant", "secondary")
        preset = _VARIANT_PRESETS.get(variant, _VARIANT_PRESETS["secondary"])
        kwargs.setdefault("color", preset["color"])
        kwargs.setdefault("font_size", T.FS_BUTTON())
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("markup", True)
        kwargs.setdefault("bg_color", preset["bg_color"])
        kwargs.setdefault("border_color", preset["border_color"])
        super().__init__(**kwargs)
        self.variant = variant
        self._original_text = self.text
        self.bind(
            size=self._on_size_change, pos=self._redraw,
            bg_color=self._redraw, border_color=self._redraw,
            pressed_flag=self._redraw, disabled=self._redraw,
            loading=self._on_loading_change,
            text=self._on_text_change,
            press_scale=self._redraw,
            variant=self._on_variant_change,
        )
        self._redraw()
        self.text_size = self.size

    # ---------- 行为 ----------
    def on_press(self):
        if self.disabled or self.loading:
            return
        self.pressed_flag = True
        Animation.cancel_all(self, "press_scale", "opacity")
        Animation(press_scale=0.96, opacity=0.92,
                  duration=0.07, t="out_quad").start(self)

    def on_release(self):
        self.pressed_flag = False
        Animation.cancel_all(self, "press_scale", "opacity")
        Animation(press_scale=1.0, opacity=1.0,
                  duration=0.16, t="out_back").start(self)

    def set_loading(self, on: bool, text: str = None):
        if on:
            if not self.loading:
                self._original_text = self.text
            self.loading = True
            self.text = self.loading_text
            self.disabled = True
        else:
            self.loading = False
            if text is not None:
                self.text = text
                self._original_text = text
            else:
                self.text = self._original_text
            self.disabled = False

    # ---------- 内部 ----------
    def _on_text_change(self, *_a):
        if not self.loading:
            self._original_text = self.text

    def _on_loading_change(self, *_a):
        self._redraw()

    def _on_size_change(self, *_a):
        self.text_size = self.size
        self._redraw()

    def _on_variant_change(self, *_a):
        preset = _VARIANT_PRESETS.get(
            self.variant, _VARIANT_PRESETS["secondary"])
        self.bg_color = list(preset["bg_color"])
        self.border_color = list(preset["border_color"])
        self.color = list(preset["color"])

    def _redraw(self, *_args):
        self.canvas.before.clear()
        self.canvas.after.clear()

        # 计算按下时的微缩中心
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        s = self.press_scale

        with self.canvas.before:
            PushMatrix()
            Scale(origin=(cx, cy), x=s, y=s, z=1)

            r, g, b, a = self.bg_color
            if self.disabled:
                r = r * 0.5 + 0.05
                g = g * 0.5 + 0.05
                b = b * 0.5 + 0.05
                a = max(0.25, a * 0.6)
            elif self.pressed_flag:
                r = min(1.0, r + 0.10)
                g = min(1.0, g + 0.07)
                b = min(1.0, b + 0.12)
            Color(r, g, b, a)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius])

            # 内层渐变高光(顶部稍亮)
            if not self.disabled and a > 0.05:
                Color(1, 1, 1, 0.05)
                RoundedRectangle(
                    pos=(self.x + dp(1),
                         self.y + self.height * 0.55),
                    size=(self.width - dp(2),
                          self.height * 0.45 - dp(1)),
                    radius=[max(self.radius - dp(1), dp(2))],
                )

            # 边框
            br, bg_, bb, ba = self.border_color
            if self.disabled:
                ba = max(0.20, ba * 0.5)
            Color(br, bg_, bb, ba)
            Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, self.radius,
            ), width=1.4)

            # 内层柔和高光(仅启用态)
            if not self.disabled:
                Color(1, 1, 1, 0.05)
                Line(rounded_rectangle=(
                    self.x + dp(2), self.y + dp(2),
                    self.width - dp(4), self.height - dp(4),
                    max(self.radius - dp(2), dp(2)),
                ), width=1.0)

        with self.canvas.after:
            PopMatrix()
