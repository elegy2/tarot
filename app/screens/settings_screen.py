"""设置页:DeepSeek API 相关配置。"""
from __future__ import annotations

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
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

from app.services.config_manager import ConfigManager
from app.services.deepseek_client import (
    DeepSeekClient, DeepSeekConfig, DeepSeekError,
)
from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="settings", **kwargs)
        self._build()

    # ---------- 布局 ----------
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
            text="[b]API 设置[/b]", markup=True,
            font_size=R.header_font_size(Window.width),
            color=list(T.COLOR_GOLD),
        )
        header.add_widget(back)
        header.add_widget(title)
        root.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        form = BoxLayout(orientation="vertical", spacing=dp(10),
                         size_hint_y=None,
                         padding=[dp(2), dp(4), dp(2), dp(8)])
        form.bind(minimum_height=form.setter("height"))

        self._status_label = Label(
            text="", markup=True, color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(22),
            halign="left", valign="middle",
        )
        self._status_label.bind(size=lambda *_: setattr(
            self._status_label, "text_size", self._status_label.size))
        form.add_widget(self._status_label)

        self._key_input = self._add_field(form, "DeepSeek API Key",
                                          password=True,
                                          hint="例如 sk-xxxxxxxxxxxxxxxx")
        self._base_input = self._add_field(form, "Base URL",
                                           hint="默认 https://api.deepseek.com")
        self._model_input = self._add_field(form, "模型名",
                                            hint="默认 deepseek-chat,可改 deepseek-reasoner")
        self._temp_input = self._add_field(form, "Temperature (0.0 - 1.5)",
                                           hint="默认 0.8")
        self._max_input = self._add_field(form, "最大输出长度 max_tokens",
                                          hint="默认 1500")

        switch_row = BoxLayout(orientation="horizontal",
                               size_hint=(1, None), height=dp(40))
        switch_label = Label(text="保存占卜历史到本地",
                             color=list(T.COLOR_TEXT),
                             font_size=R.body_font_size(Window.width),
                             halign="left", valign="middle",
                             size_hint=(1, 1))
        switch_label.bind(size=lambda *_: setattr(
            switch_label, "text_size", switch_label.size))
        self._history_switch = Switch(active=True,
                                      size_hint=(None, 1), width=dp(72))
        switch_row.add_widget(switch_label)
        switch_row.add_widget(self._history_switch)
        form.add_widget(switch_row)

        privacy = Label(
            text=("你的 API Key 仅保存在本机 user_data_dir/config.json,"
                  "不会上传到任何第三方服务器。\n"
                  "日志中只会显示脱敏后的 Key(如 sk-****abcd)。"),
            color=list(T.COLOR_TEXT_HINT),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), halign="left", valign="top",
        )
        privacy.bind(
            width=lambda *_: setattr(privacy, "text_size",
                                     (privacy.width, None)),
            texture_size=lambda *_: setattr(
                privacy, "height", privacy.texture_size[1] + dp(8)),
        )
        form.add_widget(privacy)

        scroll.add_widget(form)
        root.add_widget(scroll)

        actions = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint=(1, None),
                            height=R.button_height(Window.width))
        self._save_btn = MysticButton(text="保存配置",
                                      variant="primary",
                                      size_hint=(1, 1))
        self._save_btn.bind(on_release=lambda *_: self._save())
        self._test_btn = MysticButton(text="测试连接",
                                      variant="secondary",
                                      size_hint=(1, 1))
        self._test_btn.loading_text = "测试中……"
        self._test_btn.bind(on_release=lambda *_: self._test())
        self._clear_btn = MysticButton(text="清空 Key",
                                       variant="danger",
                                       size_hint=(1, 1))
        self._clear_btn.bind(on_release=lambda *_: self._clear_key())
        actions.add_widget(self._save_btn)
        actions.add_widget(self._test_btn)
        actions.add_widget(self._clear_btn)
        root.add_widget(actions)

        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def _add_field(self, parent, label_text: str, password: bool = False,
                   hint: str = "") -> TextInput:
        wrap = BoxLayout(orientation="vertical", size_hint=(1, None),
                         spacing=dp(3))
        wrap.height = dp(70)
        label = Label(
            text=label_text, color=list(T.COLOR_TEXT_SUB),
            font_size=R.small_font_size(Window.width),
            size_hint=(1, None), height=dp(20),
            halign="left", valign="middle",
        )
        label.bind(size=lambda *_: setattr(label, "text_size", label.size))
        ti = TextInput(
            multiline=False, password=password,
            hint_text=hint,
            size_hint=(1, None), height=dp(44),
            background_color=(0.11, 0.08, 0.20, 1),
            foreground_color=list(T.COLOR_TEXT),
            cursor_color=list(T.COLOR_GOLD),
            font_size=R.body_font_size(Window.width),
            padding=[dp(10), dp(10), dp(10), dp(10)],
        )
        wrap.add_widget(label)
        wrap.add_widget(ti)
        parent.add_widget(wrap)
        return ti

    # ---------- 生命周期 ----------
    def on_pre_enter(self, *_a):
        app = App.get_running_app()
        cfg = app.config_manager.as_dict()
        masked = ConfigManager.mask_api_key(app.config_manager.get_api_key())
        self._status_label.text = f"当前 API Key:[color=d4af37]{masked}[/color]"
        self._status_label.markup = True

        self._key_input.text = ""
        self._base_input.text = cfg.get("deepseek_base_url",
                                        "https://api.deepseek.com")
        self._model_input.text = cfg.get("deepseek_model", "deepseek-chat")
        self._temp_input.text = str(cfg.get("temperature", 0.8))
        self._max_input.text = str(cfg.get("max_tokens", 1500))
        self._history_switch.active = bool(cfg.get("save_history", True))

    # ---------- 操作 ----------
    def _save(self):
        app = App.get_running_app()
        cm = app.config_manager

        key = (self._key_input.text or "").strip()
        if key:
            cm.set_api_key(key)
        cm.set("deepseek_base_url",
               (self._base_input.text or "https://api.deepseek.com").strip())
        cm.set("deepseek_model",
               (self._model_input.text or "deepseek-chat").strip())
        try:
            cm.set("temperature",
                   max(0.0, min(1.5, float(self._temp_input.text or 0.8))))
        except ValueError:
            cm.set("temperature", 0.8)
        try:
            cm.set("max_tokens",
                   max(64, min(8000, int(self._max_input.text or 1500))))
        except ValueError:
            cm.set("max_tokens", 1500)
        cm.set("save_history", bool(self._history_switch.active))

        self._key_input.text = ""
        masked = ConfigManager.mask_api_key(cm.get_api_key())
        self._status_label.markup = True
        self._status_label.color = list(T.COLOR_SUCCESS)
        self._status_label.text = (
            f"已保存。当前 API Key:[color=d4af37]{masked}[/color]"
        )

    def _clear_key(self):
        App.get_running_app().config_manager.clear_api_key()
        self._key_input.text = ""
        self._status_label.markup = True
        self._status_label.color = list(T.COLOR_LIGHT_PURPLE)
        self._status_label.text = "API Key 已清空。"

    def _test(self):
        app = App.get_running_app()
        key = (self._key_input.text or "").strip() or app.config_manager.get_api_key()
        if not key:
            self._status_label.markup = False
            self._status_label.color = list(T.COLOR_ERROR)
            self._status_label.text = "请先填入 API Key 再测试。"
            return
        cfg = DeepSeekConfig(
            api_key=key,
            base_url=(self._base_input.text or "https://api.deepseek.com").strip(),
            model=(self._model_input.text or "deepseek-chat").strip(),
            temperature=0.5, max_tokens=32, timeout=30.0,
        )
        self._status_label.markup = False
        self._status_label.color = list(T.COLOR_TEXT_SUB)
        self._status_label.text = "测试中……请稍候。"
        self._test_btn.set_loading(True)

        def _worker():
            try:
                reply = DeepSeekClient(cfg).test_connection()
                Clock.schedule_once(lambda dt_: self._on_test_done(True, reply))
            except DeepSeekError as e:
                Clock.schedule_once(lambda dt_: self._on_test_done(False, str(e)))
            except Exception as e:  # noqa: BLE001
                Clock.schedule_once(lambda dt_: self._on_test_done(False,
                                                                   f"未知错误:{e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_test_done(self, ok: bool, msg: str):
        self._test_btn.set_loading(False, text="测试连接")
        self._status_label.markup = False
        if ok:
            self._status_label.color = list(T.COLOR_SUCCESS)
            self._status_label.text = (
                f"连接成功 ✓  模型回复:{(msg or '').strip()[:40]}"
            )
        else:
            self._status_label.color = list(T.COLOR_ERROR)
            self._status_label.text = f"连接失败:{msg}"
