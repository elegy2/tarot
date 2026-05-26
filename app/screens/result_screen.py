"""解读结果页:展示问题、牌、AI 解读结果。

重点:
1. 整页用 ScrollView + BoxLayout(size_hint_y=None) 包裹,长 AI 文本可滚动。
2. AI 文本展示在 MysticPanel 内的多个 AutoWrapLabel(按段拆分),稳定撑高,不溢出。
3. AI 文本输出前用 sanitize_ai_text 清理 Markdown / 表格 / 代码块。
4. AI 按钮按抽牌完成度、loading 状态切换文案与可点击性。
5. 错误信息显示在结果面板内,而不是控制台。
"""
from __future__ import annotations

import datetime as dt
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from app.data.spreads import get_spread
from app.services.deepseek_client import (
    DeepSeekClient, DeepSeekConfig, DeepSeekError,
)
from app.services.tarot_engine import TarotEngine
from app.utils import responsive as R
from app.utils import theme as T
from app.utils.text_formatter import sanitize_ai_text, split_paragraphs
from app.widgets.auto_wrap_label import AutoWrapLabel
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton
from app.widgets.mystic_panel import MysticPanel


LOADING_MESSAGES = [
    "正在连接星象能量……",
    "正在解读牌阵中的关系……",
    "DeepSeek 正在生成解读……",
]


class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="result", **kwargs)
        self._ai_thread = None
        self._current_reading = ""        # 清理后的纯文本,用于保存历史
        self._loading_index = 0
        self._loading_event = None
        self._has_interpreted = False
        self._build()

    # ---------- 布局 ----------
    def _build(self):
        wrapper = RelativeLayout()
        wrapper.add_widget(MysticBackground())

        root = BoxLayout(orientation="vertical",
                         padding=R.page_padding(Window.width),
                         spacing=dp(8))

        # 顶栏
        header = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(46), spacing=dp(8))
        back = MysticButton(text="< 返回", size_hint=(None, 1), width=dp(82))
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        self._title = Label(
            text="[b]解读结果[/b]", markup=True,
            font_size=R.header_font_size(Window.width),
            color=list(T.COLOR_GOLD),
        )
        header.add_widget(back)
        header.add_widget(self._title)
        root.add_widget(header)

        # 主体可滚动区
        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        self._content = BoxLayout(orientation="vertical", spacing=dp(10),
                                  size_hint_y=None,
                                  padding=[0, dp(4), 0, dp(20)])
        self._content.bind(minimum_height=self._content.setter("height"))

        # —— 问题 / 牌阵 / 抽到的牌 —— 三个面板
        self._question_panel = MysticPanel(size_hint_y=None,
                                           variant="elevated")
        self._question_panel.bind(
            minimum_height=self._question_panel.setter("height"))
        self._question_label = self._make_panel_title("你的问题")
        self._question_text = AutoWrapLabel(
            text="", color=list(T.COLOR_TEXT),
            font_size=R.body_font_size(Window.width),
        )
        self._question_panel.add_widget(self._question_label)
        self._question_panel.add_widget(self._question_text)

        self._cards_panel = MysticPanel(size_hint_y=None,
                                        variant="elevated")
        self._cards_panel.bind(
            minimum_height=self._cards_panel.setter("height"))
        self._cards_title = self._make_panel_title("抽到的牌")
        self._cards_panel.add_widget(self._cards_title)
        self._cards_lines_box = BoxLayout(
            orientation="vertical", spacing=dp(6), size_hint_y=None)
        self._cards_lines_box.bind(
            minimum_height=self._cards_lines_box.setter("height"))
        self._cards_panel.add_widget(self._cards_lines_box)

        self._ai_panel = MysticPanel(size_hint_y=None,
                                     variant="highlighted")
        self._ai_panel.bind(minimum_height=self._ai_panel.setter("height"))
        self._ai_title = self._make_panel_title("AI 解读")
        self._ai_panel.add_widget(self._ai_title)
        # AI 段落容器:每段一个 AutoWrapLabel,长文本自动撑高
        self._ai_paragraphs_box = BoxLayout(
            orientation="vertical", spacing=dp(8), size_hint_y=None)
        self._ai_paragraphs_box.bind(
            minimum_height=self._ai_paragraphs_box.setter("height"))
        self._ai_panel.add_widget(self._ai_paragraphs_box)
        # 初始提示
        self._ai_status_label = AutoWrapLabel(
            text="翻开所有塔罗牌后,点击下方按钮开始解读。",
            color=list(T.COLOR_TEXT_SUB),
            font_size=R.body_font_size(Window.width),
        )
        self._ai_paragraphs_box.add_widget(self._ai_status_label)

        self._content.add_widget(self._question_panel)
        self._content.add_widget(self._cards_panel)
        self._content.add_widget(self._ai_panel)

        scroll.add_widget(self._content)
        root.add_widget(scroll)

        # 底部按钮
        actions = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint=(1, None),
                            height=R.button_height(Window.width))
        self._ai_btn = MysticButton(
            text="开始 AI 解牌", variant="primary",
            size_hint=(1.4, 1),
        )
        self._ai_btn.loading_text = "正在解读……"
        self._ai_btn.bind(on_release=lambda *_: self._request_ai())
        self._save_btn = MysticButton(text="保存到历史",
                                      variant="ghost",
                                      size_hint=(1, 1))
        self._save_btn.bind(on_release=lambda *_: self._save_to_history())
        self._save_btn.disabled = True
        redraw_btn = MysticButton(text="重新占卜",
                                  variant="ghost",
                                  size_hint=(1, 1))
        redraw_btn.bind(on_release=lambda *_: setattr(
            self.manager, "current", "spread_select"))
        actions.add_widget(self._ai_btn)
        actions.add_widget(self._save_btn)
        actions.add_widget(redraw_btn)
        root.add_widget(actions)

        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def _make_panel_title(self, text: str) -> Label:
        lbl = Label(
            text=f"[b]{text}[/b]", markup=True,
            color=list(T.COLOR_GOLD),
            font_size=R.body_font_size(Window.width) + 1,
            size_hint=(1, None), height=dp(24),
            halign="left", valign="middle",
        )
        lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
        return lbl

    # ---------- 生命周期 ----------
    def on_pre_enter(self, *_a):
        app = App.get_running_app()
        question = (app.session.get("question") or "").strip()
        spread_key = app.session.get("spread_key", "three")
        cards = app.session.get("cards", [])
        spread = get_spread(spread_key)

        self._title.text = f"[b]{spread['name']} · 解读[/b]"

        q_display = question if question else "今日指引(未输入具体问题)"
        self._question_text.text = q_display

        # 抽到的牌 - 每张一行,使用 AutoWrapLabel
        self._cards_lines_box.clear_widgets()
        if cards:
            for c in cards:
                kw = "、".join(c["keywords"][:3])
                orient = c.get("orientation", "")
                # 正位用金色,逆位用淡紫色
                if orient == "正位":
                    orient_text = "[color=d4af37]正位[/color]"
                else:
                    orient_text = "[color=c9a4ff]逆位[/color]"
                line = AutoWrapLabel(
                    text=(f"[color=d4af37][b]·[/b][/color] "
                          f"[color=b79ced][b]{c['position']}[/b][/color]   "
                          f"[color=f5f1e8]{c['card_name_cn']}[/color]   "
                          f"{orient_text}\n"
                          f"      [size=11sp][color=c8c0d8]{kw}[/color][/size]"),
                    markup=True,
                    color=list(T.COLOR_TEXT),
                    font_size=R.body_font_size(Window.width),
                )
                self._cards_lines_box.add_widget(line)
        else:
            empty = AutoWrapLabel(
                text="(暂无抽牌结果)",
                color=list(T.COLOR_TEXT_SUB),
                font_size=R.body_font_size(Window.width),
            )
            self._cards_lines_box.add_widget(empty)

        # 重置 AI 区域为初始状态
        self._reset_ai_panel("翻开所有塔罗牌后,点击下方按钮开始解读。",
                             color=T.COLOR_TEXT_SUB)
        self._current_reading = ""
        self._has_interpreted = False
        self._save_btn.disabled = True
        self._save_btn.text = "保存到历史"
        self._update_ai_button_state()

    def on_leave(self, *_a):
        self._stop_loading_ticker()

    def _update_ai_button_state(self):
        cards = App.get_running_app().session.get("cards", [])
        if not cards:
            self._ai_btn.set_loading(False, text="请先翻开所有塔罗牌")
            self._ai_btn.disabled = True
            return
        self._ai_btn.set_loading(
            False,
            text="重新解读" if self._has_interpreted else "开始 AI 解牌",
        )

    # ---------- AI 区域 ----------
    def _reset_ai_panel(self, message: str, color=None):
        self._ai_paragraphs_box.clear_widgets()
        lbl = AutoWrapLabel(
            text=message,
            color=list(color or T.COLOR_TEXT_SUB),
            font_size=R.body_font_size(Window.width),
        )
        self._ai_paragraphs_box.add_widget(lbl)
        self._ai_status_label = lbl

    def _render_ai_paragraphs(self, text: str, color=None):
        self._ai_paragraphs_box.clear_widgets()
        paragraphs = split_paragraphs(text)
        if not paragraphs:
            self._reset_ai_panel("(空内容)", T.COLOR_TEXT_SUB)
            return
        col = list(color or T.COLOR_TEXT)
        for p in paragraphs:
            lbl = AutoWrapLabel(
                text=p, color=col,
                font_size=R.body_font_size(Window.width),
            )
            self._ai_paragraphs_box.add_widget(lbl)

    # ---------- AI 解牌 ----------
    def _request_ai(self):
        app = App.get_running_app()
        cards = app.session.get("cards", [])
        spread_key = app.session.get("spread_key", "three")
        question = app.session.get("question", "")
        spread = get_spread(spread_key)

        if not cards:
            return

        # 没有 API Key:用本地兜底解读,不报错
        if not app.config_manager.has_api_key():
            local = TarotEngine.render_local_summary(cards)
            text = sanitize_ai_text(
                "尚未配置 DeepSeek API Key。\n"
                "下方是基于本地牌义的简版解读,配置后可获得完整 AI 解牌。\n\n"
                + local
            )
            self._render_ai_paragraphs(text, color=T.COLOR_LIGHT_PURPLE)
            self._current_reading = text
            self._save_btn.disabled = False
            self._has_interpreted = True
            self._update_ai_button_state()
            return

        cfg_dict = app.config_manager.as_dict()
        cfg = DeepSeekConfig(
            api_key=app.config_manager.get_api_key(),
            base_url=cfg_dict.get("deepseek_base_url",
                                  "https://api.deepseek.com"),
            model=cfg_dict.get("deepseek_model", "deepseek-chat"),
            temperature=float(cfg_dict.get("temperature", 0.8)),
            max_tokens=int(cfg_dict.get("max_tokens", 1500)),
        )

        self._ai_btn.set_loading(True)
        self._start_loading_ticker()

        def _worker():
            try:
                client = DeepSeekClient(cfg)
                raw = client.interpret_tarot(question, spread, cards)
                Clock.schedule_once(lambda dt_: self._on_ai_success(raw))
            except DeepSeekError as e:
                Clock.schedule_once(lambda dt_: self._on_ai_error(str(e)))
            except Exception as e:  # noqa: BLE001
                Clock.schedule_once(lambda dt_: self._on_ai_error(f"未知错误:{e}"))

        self._ai_thread = threading.Thread(target=_worker, daemon=True)
        self._ai_thread.start()

    # ---------- loading ticker ----------
    def _start_loading_ticker(self):
        self._loading_index = 0
        self._reset_ai_panel(LOADING_MESSAGES[0], T.COLOR_TEXT_SUB)
        if self._loading_event:
            self._loading_event.cancel()
        self._loading_event = Clock.schedule_interval(
            self._tick_loading, 1.6)

    def _tick_loading(self, *_a):
        self._loading_index = (self._loading_index + 1) % len(LOADING_MESSAGES)
        # 直接更新已存在的 status label
        if self._ai_status_label:
            self._ai_status_label.text = LOADING_MESSAGES[self._loading_index]

    def _stop_loading_ticker(self):
        if self._loading_event:
            self._loading_event.cancel()
            self._loading_event = None

    # ---------- 回调 ----------
    def _on_ai_success(self, raw_text: str):
        self._stop_loading_ticker()
        cleaned = sanitize_ai_text(raw_text or "")
        if not cleaned:
            self._on_ai_error("API 返回空内容。请稍后重试。")
            return
        self._render_ai_paragraphs(cleaned, color=T.COLOR_TEXT)
        self._current_reading = cleaned
        self._save_btn.disabled = False
        self._has_interpreted = True
        self._update_ai_button_state()

    def _on_ai_error(self, msg: str):
        self._stop_loading_ticker()
        body = (
            "解读失败\n\n"
            f"{msg}\n\n"
            "可能原因:网络异常、API Key 无效或 DeepSeek 服务暂时不可用。\n"
            "请检查设置后重试。"
        )
        self._render_ai_paragraphs(body, color=T.COLOR_ERROR)
        self._update_ai_button_state()

    # ---------- 历史 ----------
    def _save_to_history(self):
        app = App.get_running_app()
        record = {
            "time": dt.datetime.now().isoformat(timespec="seconds"),
            "question": app.session.get("question", ""),
            "spread_key": app.session.get("spread_key", "three"),
            "spread_name": get_spread(
                app.session.get("spread_key", "three"))["name"],
            "cards": app.session.get("cards", []),
            "reading": self._current_reading,
        }
        app.config_manager.append_history(record)
        self._save_btn.disabled = True
        self._save_btn.text = "已保存"
