"""历史记录页:列表 + 详情弹窗。"""
from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from app.utils import format_record_time
from app.utils import responsive as R
from app.utils import theme as T
from app.utils.text_formatter import sanitize_ai_text, split_paragraphs
from app.widgets.auto_wrap_label import AutoWrapLabel
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton
from app.widgets.mystic_panel import MysticPanel


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="history", **kwargs)
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
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        title = Label(
            text="[b]历史记录[/b]", markup=True,
            font_size=R.header_font_size(Window.width),
            color=list(T.COLOR_GOLD),
        )
        clear = MysticButton(text="清空", variant="danger",
                             size_hint=(None, 1), width=dp(72))
        clear.bind(on_release=lambda *_: self._clear_all())
        header.add_widget(back)
        header.add_widget(title)
        header.add_widget(clear)
        root.add_widget(header)

        self._scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        self._list_layout = BoxLayout(orientation="vertical", spacing=dp(10),
                                      size_hint_y=None,
                                      padding=[0, dp(4), 0, dp(20)])
        self._list_layout.bind(
            minimum_height=self._list_layout.setter("height"))
        self._scroll.add_widget(self._list_layout)
        root.add_widget(self._scroll)

        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *_a):
        self._refresh()

    def _refresh(self):
        self._list_layout.clear_widgets()
        app = App.get_running_app()
        history = app.config_manager.load_history()
        if not history:
            empty = Label(
                text="[i]还没有历史记录。[/i]\n\n完成一次占卜并在结果页点击「保存到历史」就能在这里看到。",
                markup=True, color=list(T.COLOR_TEXT_SUB),
                halign="center", valign="middle",
                font_size=R.body_font_size(Window.width),
                size_hint=(1, None), height=dp(200),
            )
            empty.bind(size=lambda *_: setattr(empty, "text_size", empty.size))
            self._list_layout.add_widget(empty)
            return
        for idx, record in enumerate(history):
            self._list_layout.add_widget(self._build_item(idx, record))

    def _build_item(self, idx: int, record) -> MysticPanel:
        item = MysticPanel(size_hint=(1, None),
                           variant="elevated",
                           padding=[dp(14), dp(10), dp(14), dp(12)],
                           spacing=dp(6))
        item.height = dp(132)

        time_str = format_record_time(record.get("time", ""))
        spread_name = record.get("spread_name", "")
        cards_count = len(record.get("cards", []))
        top = Label(
            text=(f"[b]{spread_name}[/b]   "
                  f"[size=11sp][color=b79ced]{cards_count} 张[/color][/size]   "
                  f"[size=11sp][color=807898]{time_str}[/color][/size]"),
            markup=True, color=list(T.COLOR_TEXT),
            font_size=R.body_font_size(Window.width),
            halign="left", valign="middle",
            size_hint=(1, None), height=dp(24),
        )
        top.bind(size=lambda *_: setattr(top, "text_size", top.size))
        item.add_widget(top)

        q = (record.get("question") or "").strip() or "今日指引(未输入具体问题)"
        # 截断长问题,保持卡片高度稳定
        if len(q) > 40:
            q = q[:38] + "…"
        q_label = Label(
            text=f"[color=b79ced]问题:[/color] [color=f5f1e8]{q}[/color]",
            markup=True, color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            halign="left", valign="top",
            size_hint=(1, None), height=dp(24),
        )
        q_label.bind(size=lambda *_: setattr(q_label, "text_size", q_label.size))
        item.add_widget(q_label)

        btns = BoxLayout(orientation="horizontal", spacing=dp(8),
                         size_hint=(1, None), height=dp(40))
        view_btn = MysticButton(text="查看", variant="primary",
                                size_hint=(1, 1))
        view_btn.bind(on_release=lambda *_a, r=record: self._show_detail(r))
        del_btn = MysticButton(text="删除", variant="danger",
                               size_hint=(1, 1))
        del_btn.bind(on_release=lambda *_a, i=idx: self._delete(i))
        btns.add_widget(view_btn)
        btns.add_widget(del_btn)
        item.add_widget(btns)

        return item

    def _show_detail(self, record):
        modal = ModalView(size_hint=(0.94, 0.86),
                          background_color=(0, 0, 0, 0.4))

        box = MysticPanel(orientation="vertical", spacing=dp(8),
                          padding=[dp(14), dp(14), dp(14), dp(14)])

        header = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(36))
        header.add_widget(Label(
            text=f"[b]{record.get('spread_name', '')}[/b]  "
                 f"[size=11sp][color=b0a8c8]"
                 f"{format_record_time(record.get('time', ''))}[/color][/size]",
            markup=True, color=list(T.COLOR_GOLD),
            font_size=R.body_font_size(Window.width) + 1,
            halign="left", valign="middle",
        ))
        close_btn = MysticButton(text="关闭", size_hint=(None, 1), width=dp(64))
        close_btn.bind(on_release=lambda *_: modal.dismiss())
        header.add_widget(close_btn)
        box.add_widget(header)

        scroll = ScrollView(bar_width=dp(4))
        content = BoxLayout(orientation="vertical", spacing=dp(8),
                            size_hint_y=None,
                            padding=[dp(2), dp(4), dp(2), dp(8)])
        content.bind(minimum_height=content.setter("height"))

        def add_label(text, color=T.COLOR_TEXT, markup=False):
            lbl = AutoWrapLabel(
                text=text, markup=markup, color=list(color),
                font_size=R.body_font_size(Window.width),
            )
            content.add_widget(lbl)
            return lbl

        q = (record.get("question") or "").strip() or "今日指引"
        add_label(f"[b]你的问题[/b]\n{q}", markup=True)
        lines = []
        for c in record.get("cards", []):
            kw = "、".join(c.get("keywords", [])[:3])
            lines.append(
                f"· 位置「{c['position']}」: {c['card_name_cn']} · {c['orientation']}  "
                f"[color=b0a8c8]{kw}[/color]"
            )
        add_label("[b]抽到的牌[/b]\n" + "\n".join(lines), markup=True)

        # 解读分段渲染,保证长文本可滚动
        reading = sanitize_ai_text(record.get("reading") or "")
        add_label("[b]解读[/b]", markup=True, color=T.COLOR_GOLD)
        paragraphs = split_paragraphs(reading) or ["(未保存解读内容)"]
        for p in paragraphs:
            add_label(p)

        scroll.add_widget(content)
        box.add_widget(scroll)
        modal.add_widget(box)
        modal.open()

    def _delete(self, idx: int):
        App.get_running_app().config_manager.delete_history_at(idx)
        self._refresh()

    def _clear_all(self):
        App.get_running_app().config_manager.clear_history()
        self._refresh()
