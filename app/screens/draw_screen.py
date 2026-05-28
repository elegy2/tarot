"""抽牌页:根据牌阵显示 N 张背面朝上的牌,用户点击翻牌。

响应式:
- 卡牌宽高来自 responsive.card_size(),屏幕变化时同步重建。
- 窄屏自动垂直滚动,宽屏横向并排。
- resize 重建保持已翻开状态,不打断体验。
- 横排总宽度不足时居中显示,避免全部堆在左侧。
- header / tip / status 字号随断点动态刷新。

入场动画:
- 每张牌依次淡入 + 轻微上浮,形成错峰的仪式感。
"""
from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from app.data.spreads import get_spread
from app.services.tarot_engine import TarotEngine
from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton
from app.widgets.tarot_card_widget import TarotCardWidget


class DrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="draw", **kwargs)
        self._engine = TarotEngine(use_major_only=True)
        self._cards_data = []
        self._card_widgets = []
        self._cards_layout = None
        self._scroll = None
        self._resize_event = None
        self._build()
        Window.bind(size=self._on_window_resize)

    # ---------- 布局 ----------
    def _build(self):
        wrapper = RelativeLayout()
        wrapper.add_widget(MysticBackground())

        self._root = BoxLayout(orientation="vertical",
                               padding=R.page_padding(Window.width),
                               spacing=dp(8))

        header = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(46), spacing=dp(8))
        back = MysticButton(text="< 返回", variant="ghost",
                            size_hint=(None, 1), width=dp(82))
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        self._title_label = Label(
            text="[b]抽牌[/b]", markup=True,
            font_size=R.header_font_size(Window.width),
            color=list(T.COLOR_GOLD),
        )
        header.add_widget(back)
        header.add_widget(self._title_label)
        self._root.add_widget(header)

        self._tip_label = Label(
            text="点击每一张牌背,静心感受后翻开。",
            color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(22),
            halign="center", valign="middle",
        )
        self._tip_label.bind(size=lambda *_: setattr(
            self._tip_label, "text_size", self._tip_label.size))
        self._root.add_widget(self._tip_label)

        # ScrollView 优化: 手机端触摸滚动体验
        self._scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(6),  # 手机端细滚动条
            scroll_type=["bars", "content"],  # 支持触摸滚动
            bar_color=[0.86, 0.68, 0.32, 0.6],  # 金色滚动条
            bar_inactive_color=[0.86, 0.68, 0.32, 0.3],
            effect_cls="ScrollEffect",  # 使用标准滚动效果
        )
        self._root.add_widget(self._scroll)

        self._status_label = Label(
            text="", color=list(T.COLOR_GOLD),
            font_size=R.small_font_size(Window.width) + 1,
            size_hint=(1, None), height=dp(22),
        )
        self._root.add_widget(self._status_label)

        self._actions = BoxLayout(orientation="horizontal", spacing=dp(10),
                                  size_hint=(1, None),
                                  height=R.button_height(Window.width))
        self._reshuffle_btn = MysticButton(text="重新洗牌",
                                           variant="ghost",
                                           size_hint=(1, 1))
        self._reshuffle_btn.bind(on_release=lambda *_: self._reshuffle())
        self._view_btn = MysticButton(
            text="查看解读", variant="primary",
            size_hint=(1.2, 1),
        )
        self._view_btn.bind(on_release=lambda *_: self._goto_result())
        self._actions.add_widget(self._reshuffle_btn)
        self._actions.add_widget(self._view_btn)
        self._root.add_widget(self._actions)

        wrapper.add_widget(self._root)
        self.add_widget(wrapper)

    # ---------- 生命周期 ----------
    def on_pre_enter(self, *_a):
        app = App.get_running_app()
        spread_key = app.session.get("spread_key")
        if not spread_key:
            self.manager.current = "spread_select"
            return
        self._reset(spread_key)

    def on_enter(self, *_a):
        # 进入屏幕后播放入场错峰动画(在 widget 已经完成布局后触发)
        Clock.schedule_once(lambda *_: self._play_enter_sequence(), 0.05)

    def on_leave(self, *_a):
        if self._cards_layout:
            self._cards_layout.clear_widgets()
        self._card_widgets.clear()

    def _on_window_resize(self, *_a):
        # 节流:短时间内多次 resize 只重建一次
        if self._resize_event is not None:
            self._resize_event.cancel()
        self._resize_event = Clock.schedule_once(
            lambda *_: self._apply_resize(), 0.08)

    def _apply_resize(self):
        self._resize_event = None
        w = Window.width
        # 同步字号 / padding / 按钮高度
        self._root.padding = R.page_padding(w)
        self._title_label.font_size = R.header_font_size(w)
        self._tip_label.font_size = R.small_font_size(w)
        self._status_label.font_size = R.small_font_size(w) + 1
        btn_h = R.button_height(w)
        self._actions.height = btn_h
        if self._cards_data:
            self._rebuild_cards_layout(animate_enter=False,
                                       preserve_flipped=True)

    # ---------- 核心逻辑 ----------
    def _reset(self, spread_key: str):
        spread = get_spread(spread_key)
        self._title_label.text = f"[b]{spread['name']}[/b]"
        self._tip_label.text = "点击每一张牌背,静心感受后翻开。"
        self._cards_data = self._engine.draw(spread_key)
        App.get_running_app().session["cards"] = self._cards_data
        self._update_status(0)
        self._view_btn.disabled = True
        self._rebuild_cards_layout(animate_enter=False, preserve_flipped=False)

    def _rebuild_cards_layout(self, *, animate_enter: bool,
                              preserve_flipped: bool):
        win_w = Window.width
        win_h = Window.height
        count = len(self._cards_data)
        orientation = R.cards_orientation(win_w)
        card_w, card_h = R.card_size(win_w, win_h, count=count)

        # 记录原本已翻开的牌索引,保证 resize 时翻开状态不丢
        prev_flipped = set()
        if preserve_flipped:
            for i, w in enumerate(self._card_widgets):
                if w.flipped:
                    prev_flipped.add(i)

        spacing = R.cards_spacing(win_w)
        self._scroll.clear_widgets()

        # 外层容器让 cards_layout 在可用空间内居中
        if orientation == "vertical":
            outer = BoxLayout(orientation="vertical",
                              size_hint=(1, None))
            self._cards_layout = BoxLayout(
                orientation="vertical", spacing=spacing,
                size_hint=(1, None),
                padding=[dp(6), dp(4), dp(6), dp(12)],
            )
            self._cards_layout.bind(
                minimum_height=self._cards_layout.setter("height"))
            outer.bind(minimum_height=outer.setter("height"))
            outer.add_widget(self._cards_layout)
            self._scroll.do_scroll_x = False
            self._scroll.do_scroll_y = True
            self._scroll.add_widget(outer)
        else:
            # 横排:用 AnchorLayout 让内部水平居中
            self._cards_layout = BoxLayout(
                orientation="horizontal", spacing=spacing,
                size_hint=(None, 1),
                padding=[dp(6), 0, dp(6), 0],
            )
            self._cards_layout.bind(
                minimum_width=self._cards_layout.setter("width"))
            outer = AnchorLayout(anchor_x="center", anchor_y="center",
                                 size_hint=(None, 1))
            outer.add_widget(self._cards_layout)
            # outer 宽度 = max(scroll 可用宽度, 卡片实际总宽度)
            self._scroll.do_scroll_x = True
            self._scroll.do_scroll_y = False
            self._scroll.add_widget(outer)

            def _sync_outer_width(*_a):
                total = self._cards_layout.width
                outer.width = max(total, self._scroll.width)
            self._cards_layout.bind(width=_sync_outer_width)
            self._scroll.bind(width=_sync_outer_width)

        self._card_widgets.clear()
        extra_h = R.card_extra_h(win_w)
        for idx, card in enumerate(self._cards_data):
            container = AnchorLayout(
                anchor_x="center", anchor_y="center",
                size_hint=(None, None),
                size=(card_w, card_h + extra_h),
            )
            widget = TarotCardWidget(
                size_hint=(None, None), size=(card_w, card_h),
            )
            widget.card = card
            widget.position = card["position"]
            widget.bind(flipped=self._on_flipped)
            container.add_widget(widget)
            self._cards_layout.add_widget(container)
            self._card_widgets.append(widget)

            if preserve_flipped and idx in prev_flipped:
                widget.reveal_immediate()

        if animate_enter:
            Clock.schedule_once(lambda *_: self._play_enter_sequence(), 0)

    def _play_enter_sequence(self):
        # 已经翻开的牌不再入场(resize 情况不会走到这里,但保底)
        for i, w in enumerate(self._card_widgets):
            if w.flipped:
                continue
            w.play_enter(delay=i * 0.09)

    # ---------- 交互 ----------
    def _on_flipped(self, *_a):
        flipped = sum(1 for w in self._card_widgets if w.flipped)
        self._update_status(flipped)
        if flipped == len(self._card_widgets) and self._card_widgets:
            self._view_btn.disabled = False
            self._tip_label.text = "牌已全部揭示,点击「查看解读」继续。"

    def _update_status(self, flipped: int):
        total = len(self._card_widgets) or len(self._cards_data)
        self._status_label.text = f"共 {total} 张,已翻开 {flipped} 张"

    def _reshuffle(self):
        app = App.get_running_app()
        spread_key = app.session.get("spread_key", "three")
        self._reset(spread_key)
        Clock.schedule_once(lambda *_: self._play_enter_sequence(), 0.05)

    def _goto_result(self):
        if any(not w.flipped for w in self._card_widgets):
            self._tip_label.text = "请先翻开所有塔罗牌。"
            return
        self.manager.current = "result"
