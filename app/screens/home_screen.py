"""首页: 应用名称 + 主入口按钮。

风格目标:
- 神秘、简洁、深色; 不使用 emoji 与花哨符号。
- 中央 BoxLayout 居中, 内容随窗口尺寸自适应。
- 主页面只保留导航入口, 卡牌图片由抽牌流程在 DrawScreen / ResultScreen 展示。
"""
from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton


PRIMARY = ("开始占卜", "spread_select", "primary")
SECONDARY = [
    ("每日一牌", "_daily", "ghost"),
    ("历史记录", "history", "ghost"),
    ("API 设置", "settings", "ghost"),
    ("关于应用", "about", "ghost"),
]


class _HairlineDivider(Widget):
    """中段一段细金色线 + 两侧渐隐, 用于标题下方的视觉分隔。"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(10)
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *_a):
        self.canvas.clear()
        if self.width <= 4:
            return
        cy = self.y + self.height / 2
        mid_w = max(self.width * 0.28, dp(60))
        x1 = self.x + (self.width - mid_w) / 2
        with self.canvas:
            Color(T.COLOR_GOLD[0], T.COLOR_GOLD[1], T.COLOR_GOLD[2], 0.85)
            Line(points=[x1, cy, x1 + mid_w, cy], width=1.0)
            # 两侧渐隐
            Color(T.COLOR_GOLD[0], T.COLOR_GOLD[1], T.COLOR_GOLD[2], 0.18)
            Line(points=[self.x + dp(6), cy, x1 - dp(8), cy], width=1.0)
            Line(points=[x1 + mid_w + dp(8), cy,
                         self.x + self.width - dp(6), cy], width=1.0)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="home", **kwargs)
        self._build()
        Window.bind(size=lambda *_a: self._layout())

    def _build(self):
        wrapper = RelativeLayout()
        wrapper.add_widget(MysticBackground())

        center = AnchorLayout(anchor_x="center", anchor_y="center",
                              padding=R.page_padding(Window.width))
        column = BoxLayout(orientation="vertical", spacing=dp(10),
                           size_hint=(None, None))
        self._column = column

        # ---- 标题: 字间距撑开, 提升神秘感 ----
        self._title_label = Label(
            text="[b]灵 境 塔 罗[/b]", markup=True,
            font_size=R.title_font_size(Window.width),
            color=list(T.COLOR_GOLD),
            size_hint=(1, None), height=dp(58),
            halign="center", valign="middle",
        )
        self._title_label.bind(size=lambda *_: setattr(
            self._title_label, "text_size", self._title_label.size))
        column.add_widget(self._title_label)

        # ---- 英文副标题: 全大写 + 字间距, 偏弱化 ----
        self._subtitle_label = Label(
            text="M Y S T I C   T A R O T",
            font_size=sp(11),
            color=list(T.COLOR_TEXT_HINT),
            size_hint=(1, None), height=dp(20),
            halign="center", valign="middle",
        )
        self._subtitle_label.bind(size=lambda *_: setattr(
            self._subtitle_label, "text_size", self._subtitle_label.size))
        column.add_widget(self._subtitle_label)

        # ---- 细金分割线 ----
        self._divider = _HairlineDivider(size_hint=(1, None))
        column.add_widget(self._divider)

        # ---- 中文 tagline ----
        self._tagline_label = Label(
            text="聆听牌阵深处的低语",
            font_size=R.body_font_size(Window.width),
            color=list(T.COLOR_TEXT_SUB),
            size_hint=(1, None), height=dp(24),
            halign="center", valign="middle",
        )
        self._tagline_label.bind(size=lambda *_: setattr(
            self._tagline_label, "text_size", self._tagline_label.size))
        column.add_widget(self._tagline_label)

        # 中部留白
        column.add_widget(Widget(size_hint=(1, None), height=dp(22)))

        # ---- 主操作按钮 ----
        self._primary_btn = MysticButton(
            text=PRIMARY[0], variant=PRIMARY[2],
            font_size=T.FS_BUTTON() + 1,
            size_hint=(1, None),
        )
        self._primary_btn.height = R.button_height(Window.width) + dp(4)
        self._primary_btn.bind(
            on_release=lambda *_a: self._navigate(PRIMARY[1]))
        column.add_widget(self._primary_btn)

        # ---- 次级按钮 ----
        self._secondary_box = BoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint=(1, None),
        )
        column.add_widget(self._secondary_box)

        # 间隔
        column.add_widget(Widget(size_hint=(1, None), height=dp(8)))

        # ---- 底部免责 ----
        self._footer_label = Label(
            text="本应用提供的解读仅供反思, 不构成任何专业建议。",
            font_size=R.small_font_size(Window.width),
            color=list(T.COLOR_TEXT_HINT),
            size_hint=(1, None), height=dp(20),
            halign="center", valign="middle",
        )
        self._footer_label.bind(size=lambda *_: setattr(
            self._footer_label, "text_size", self._footer_label.size))
        column.add_widget(self._footer_label)

        center.add_widget(column)
        wrapper.add_widget(center)
        self.add_widget(wrapper)
        self._layout()

    def _layout(self):
        w = Window.width
        col_w = R.content_max_width(w)
        self._column.width = col_w

        # 字号同步当前断点
        self._title_label.font_size = R.title_font_size(w)
        self._tagline_label.font_size = R.body_font_size(w)
        self._footer_label.font_size = R.small_font_size(w)

        # 主按钮高度同步
        primary_h = R.button_height(w) + dp(4)
        self._primary_btn.height = primary_h

        # 重建次级按钮: >=380dp 双列, 否则单列
        self._secondary_box.clear_widgets()
        per_row = 2 if w >= dp(380) else 1
        btn_h = max(R.button_height(w) - dp(6), dp(40))

        cur = None
        for i, (label, target, variant) in enumerate(SECONDARY):
            if i % per_row == 0:
                cur = BoxLayout(orientation="horizontal", spacing=dp(8),
                                size_hint=(1, None), height=btn_h)
                self._secondary_box.add_widget(cur)
            btn = MysticButton(text=label, variant=variant,
                               size_hint=(1, 1))
            btn.bind(on_release=lambda *_a, t=target: self._navigate(t))
            cur.add_widget(btn)

        sec_rows = (len(SECONDARY) + per_row - 1) // per_row
        secondary_h = sec_rows * btn_h + max(0, sec_rows - 1) * dp(8)
        self._secondary_box.height = secondary_h

        # 整列高度自适应
        # 标题区: 标题 58 + 英文副标题 20 + 分割线 10 + tagline 24 + 间隔 22
        title_block = dp(58) + dp(20) + dp(10) + dp(24) + dp(22)
        col_h = (title_block + primary_h + secondary_h
                 + dp(8) + dp(20))
        self._column.height = col_h

    def _navigate(self, target: str):
        app = App.get_running_app()
        if target == "_daily":
            app.session["spread_key"] = "single"
            app.session["question"] = ""
            self.manager.current = "draw"
            return
        self.manager.current = target
