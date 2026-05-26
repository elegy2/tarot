"""问题输入页:用户输入本次占卜关注的问题。

适配要点:
- 输入框支持多行,占用页面合理比例。
- 示例区放在 ScrollView,小屏幕也不会把"开始抽牌"按钮挤出去。
- 键盘弹出时,顶部 BoxLayout 仍能保留底部按钮可见。
"""
from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.data.spreads import get_spread
from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton


EXAMPLES = [
    "我最近在感情上需要注意什么?",
    "这段关系适合继续深入吗?",
    "我是否应该接受新的工作机会?",
    "接下来三个月的事业重点是什么?",
    "让我困扰的这件事,有哪些隐藏层面?",
]


class QuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="question", **kwargs)
        self._build()

    def _build(self):
        wrapper = RelativeLayout()
        wrapper.add_widget(MysticBackground())

        root = BoxLayout(orientation="vertical",
                         padding=R.page_padding(Window.width),
                         spacing=dp(8))

        header = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(46), spacing=dp(8))
        back = MysticButton(text="< 返回", variant="ghost",
                            size_hint=(None, 1), width=dp(82))
        back.bind(on_release=lambda *_: setattr(
            self.manager, "current", "spread_select"))
        title = Label(text="[b]写下你的问题[/b]", markup=True,
                      font_size=R.header_font_size(Window.width),
                      color=list(T.COLOR_GOLD))
        header.add_widget(back)
        header.add_widget(title)
        root.add_widget(header)

        self._spread_label = Label(
            text="", color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(22),
            halign="left", valign="middle",
        )
        self._spread_label.bind(size=lambda *_: setattr(
            self._spread_label, "text_size", self._spread_label.size))
        root.add_widget(self._spread_label)

        hint = Label(
            text="用一句话描述你想咨询的问题。你也可以不输入问题,进行开放式占卜。",
            color=list(T.COLOR_TEXT_HINT),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(20),
            halign="left", valign="middle",
        )
        hint.bind(size=lambda *_: setattr(hint, "text_size", hint.size))
        root.add_widget(hint)

        self._input = TextInput(
            hint_text="例如:这段关系未来会怎样?",
            multiline=True,
            size_hint=(1, 0.32),
            background_color=(0.11, 0.08, 0.20, 1),
            foreground_color=list(T.COLOR_TEXT),
            cursor_color=list(T.COLOR_GOLD),
            font_size=R.body_font_size(Window.width) + 1,
            padding=[dp(12), dp(12), dp(12), dp(12)],
        )
        root.add_widget(self._input)

        examples_title = Label(
            text="示例问题(点击可填入)", color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(22),
            halign="left", valign="middle",
        )
        examples_title.bind(size=lambda *_: setattr(
            examples_title, "text_size", examples_title.size))
        root.add_widget(examples_title)

        ex_scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        examples_box = BoxLayout(orientation="vertical", spacing=dp(6),
                                 size_hint=(1, None))
        examples_box.bind(minimum_height=examples_box.setter("height"))
        for text in EXAMPLES:
            ex = MysticButton(text=text, variant="ghost",
                              size_hint=(1, None),
                              height=dp(40),
                              font_size=R.small_font_size(Window.width) + 1)
            ex.bind(on_release=lambda *_a, t=text: self._fill_example(t))
            examples_box.add_widget(ex)
        ex_scroll.add_widget(examples_box)
        root.add_widget(ex_scroll)

        actions = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint=(1, None),
                            height=R.button_height(Window.width))
        start = MysticButton(text="开始抽牌",
                             variant="primary",
                             size_hint=(1, 1))
        start.bind(on_release=lambda *_: self._start_draw())
        actions.add_widget(start)
        root.add_widget(actions)

        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *_a):
        app = App.get_running_app()
        key = app.session.get("spread_key", "three")
        spread = get_spread(key)
        self._spread_label.text = (
            f"当前牌阵:[b]{spread['name']}[/b]  · 共 {len(spread['positions'])} 张"
        )
        self._spread_label.markup = True

    def _fill_example(self, text: str):
        self._input.text = text

    def _start_draw(self):
        app = App.get_running_app()
        app.session["question"] = (self._input.text or "").strip()
        self.manager.current = "draw"
