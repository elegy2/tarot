"""牌阵选择页:窄屏单列,宽屏双列。

每个牌阵卡片:
- 左侧:专属符号徽章(月/星/心/钱币/凯尔特十字)
- 右侧:牌阵名 + 张数 chip;描述;tags chip 行
- 整卡可点击;同时保留右上角「选择」按钮作为强提示
"""
from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from app.data.spreads import SPREADS
from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.auto_wrap_label import AutoWrapLabel
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton
from app.widgets.symbol_badge import SymbolBadge, symbol_for_spread


class _Chip(Label):
    """金色描边的小 chip 标签。"""

    def __init__(self, text: str, accent=None, **kwargs):
        accent = accent or T.COLOR_GOLD
        kwargs.setdefault("color",
                          [accent[0], accent[1], accent[2], 1.0])
        kwargs.setdefault("font_size", T.FS_TINY())
        kwargs.setdefault("size_hint", (None, None))
        super().__init__(text=text, **kwargs)
        self._accent = accent
        self.bind(texture_size=self._on_tex)
        self._on_tex()
        self.bind(size=self._redraw, pos=self._redraw)

    def _on_tex(self, *_a):
        self.size = (self.texture_size[0] + dp(16),
                     self.texture_size[1] + dp(8))
        self._redraw()

    def _redraw(self, *_a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self._accent[0], self._accent[1], self._accent[2], 0.10)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.height / 2])
            Color(self._accent[0], self._accent[1], self._accent[2], 0.55)
            Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, self.height / 2,
            ), width=1.0)


class _SpreadCard(ButtonBehavior, BoxLayout):
    """整张可点击的牌阵卡片。"""

    hovered = BooleanProperty(False)

    def __init__(self, spread, on_choose, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(12),
                         padding=[dp(12), dp(12), dp(14), dp(12)],
                         size_hint=(1, None), **kwargs)
        self._spread = spread
        self._on_choose = on_choose
        self.height = dp(140)

        # 左侧符号徽章
        badge_box = BoxLayout(orientation="vertical", size_hint=(None, 1),
                              width=dp(70))
        badge_box.add_widget(Widget())
        self._badge = SymbolBadge(
            symbol=symbol_for_spread(spread["key"]),
            size_hint=(None, None), size=(dp(56), dp(56)),
        )
        badge_holder = BoxLayout(orientation="horizontal",
                                 size_hint=(1, None), height=dp(56))
        badge_holder.add_widget(Widget())
        badge_holder.add_widget(self._badge)
        badge_holder.add_widget(Widget())
        badge_box.add_widget(badge_holder)
        badge_box.add_widget(Widget())
        self.add_widget(badge_box)

        # 右侧内容
        right = BoxLayout(orientation="vertical", spacing=dp(4),
                          size_hint=(1, 1))

        # 顶部:名称 + 张数 chip
        top = BoxLayout(orientation="horizontal", spacing=dp(8),
                        size_hint=(1, None), height=dp(28))
        name = Label(
            text=f"[b]{spread['name']}[/b]",
            markup=True, color=list(T.COLOR_TEXT),
            font_size=R.body_font_size(Window.width) + 2,
            halign="left", valign="middle",
            size_hint=(1, 1),
        )
        name.bind(size=lambda *_: setattr(name, "text_size", name.size))
        top.add_widget(name)
        chip = _Chip(text=f"{len(spread['positions'])} 张",
                     accent=T.COLOR_LIGHT_PURPLE)
        chip_wrap = BoxLayout(orientation="horizontal",
                              size_hint=(None, 1), width=dp(60))
        chip_wrap.add_widget(Widget())
        chip_wrap.add_widget(chip)
        top.add_widget(chip_wrap)
        right.add_widget(top)

        # 中部:介绍
        intro = AutoWrapLabel(
            text=spread["intro"],
            color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None),
        )
        right.add_widget(intro)

        # 底部:tags chip 行
        if spread.get("tags"):
            tags_row = BoxLayout(orientation="horizontal", spacing=dp(6),
                                 size_hint=(1, None), height=dp(26))
            for t in spread["tags"]:
                tags_row.add_widget(_Chip(text=t, accent=T.COLOR_GOLD_SOFT))
            tags_row.add_widget(Widget())
            right.add_widget(tags_row)

        self.add_widget(right)

        self.bind(size=self._redraw, pos=self._redraw,
                  hovered=self._redraw)
        self._redraw()

    def on_release(self):
        self._on_choose(self._spread)

    def _redraw(self, *_a):
        self.canvas.before.clear()
        with self.canvas.before:
            # 背景
            Color(*T.COLOR_PANEL)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            # 内层渐隐高光
            Color(1, 1, 1, 0.025)
            RoundedRectangle(
                pos=(self.x + dp(1), self.y + self.height * 0.55),
                size=(self.width - dp(2), self.height * 0.45 - dp(1)),
                radius=[dp(15)],
            )
            # 描边
            Color(*T.COLOR_GOLD_SOFT)
            Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, dp(16),
            ), width=1.2)
            # 左侧 accent 条
            Color(*T.COLOR_GOLD)
            RoundedRectangle(
                pos=(self.x + dp(4), self.y + dp(10)),
                size=(dp(2), self.height - dp(20)),
                radius=[dp(1)],
            )


class SpreadSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="spread_select", **kwargs)
        self._grid = None
        self._build()
        Window.bind(size=self._on_resize)

    def _build(self):
        wrapper = RelativeLayout()
        wrapper.add_widget(MysticBackground())

        root = BoxLayout(orientation="vertical",
                         padding=R.page_padding(Window.width),
                         spacing=dp(10))

        header = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(46), spacing=dp(8))
        back = MysticButton(text="< 返回", variant="ghost",
                            size_hint=(None, 1), width=dp(82))
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        title = Label(text="[b]选择牌阵[/b]", markup=True,
                      font_size=R.header_font_size(Window.width),
                      color=list(T.COLOR_GOLD))
        header.add_widget(back)
        header.add_widget(title)
        root.add_widget(header)

        hint = Label(
            text="每个牌阵对应不同的问题类型与视角,点击卡片即可选择。",
            font_size=R.small_font_size(Window.width),
            color=list(T.COLOR_TEXT_SUB),
            size_hint=(1, None), height=dp(20),
            halign="left", valign="middle",
        )
        hint.bind(size=lambda *_: setattr(hint, "text_size", hint.size))
        root.add_widget(hint)

        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        cols = 2 if Window.width >= dp(720) else 1
        self._grid = GridLayout(cols=cols, spacing=dp(12),
                                size_hint_y=None,
                                padding=[0, dp(4), 0, dp(20)])
        self._grid.bind(minimum_height=self._grid.setter("height"))
        for spread in SPREADS:
            self._grid.add_widget(_SpreadCard(spread, self._choose))
        scroll.add_widget(self._grid)
        root.add_widget(scroll)

        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def _on_resize(self, *_a):
        if not self._grid:
            return
        cols = 2 if Window.width >= dp(720) else 1
        if self._grid.cols != cols:
            self._grid.cols = cols

    def _choose(self, spread):
        app = App.get_running_app()
        app.session["spread_key"] = spread["key"]
        self.manager.current = "question"
