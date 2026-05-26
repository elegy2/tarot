"""关于页。"""
from __future__ import annotations

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from app.utils import responsive as R
from app.utils import theme as T
from app.widgets.auto_wrap_label import AutoWrapLabel
from app.widgets.mystic_background import MysticBackground
from app.widgets.mystic_button import MysticButton
from app.widgets.mystic_panel import MysticPanel


ABOUT_TEXT = (
    "灵境塔罗 · Mystic Tarot\n\n"
    "这是一款基于 Python + Kivy 的本地塔罗占卜应用。\n"
    "它不使用任何数据库,所有设置与历史记录都保存在你手机上的私有目录。\n\n"
    "AI 解牌\n"
    "应用通过你自行配置的 DeepSeek API 生成解牌,未配置时仍可使用本地基础牌义。\n"
    "AI 输出会经过纯文本清理,不再带 Markdown 标记,适合手机阅读。\n\n"
    "塔罗的态度\n"
    "塔罗不是命运的裁决,而是一面镜子。\n"
    "它帮你看见情绪、看见模式、看见尚未被注意的选项。\n"
    "重要决定,仍然请你用自己的理性与直觉来做。\n\n"
    "隐私\n"
    "API Key 仅保存在本机 user_data_dir。\n"
    "不会上传你的问题或历史到任何第三方。\n"
    "日志中只显示脱敏 Key。\n\n"
    "医疗 / 法律 / 投资提醒\n"
    "若问题涉及以上领域或严重的心理困扰,请优先咨询相关专业人士。"
)


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="about", **kwargs)
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
            text="[b]关于应用[/b]", markup=True,
            font_size=R.header_font_size(Window.width),
            color=list(T.COLOR_GOLD),
        )
        header.add_widget(back)
        header.add_widget(title)
        root.add_widget(header)

        scroll = ScrollView(bar_width=dp(4))
        content = BoxLayout(orientation="vertical",
                            padding=[dp(2), dp(4), dp(2), dp(12)],
                            size_hint_y=None, spacing=dp(8))
        content.bind(minimum_height=content.setter("height"))

        panel = MysticPanel(size_hint_y=None)
        panel.bind(minimum_height=panel.setter("height"))
        # 按段拆分
        parts = [p.strip() for p in ABOUT_TEXT.split("\n\n") if p.strip()]
        for p in parts:
            lbl = AutoWrapLabel(
                text=p,
                color=list(T.COLOR_TEXT),
                font_size=R.body_font_size(Window.width),
            )
            panel.add_widget(lbl)
        content.add_widget(panel)
        scroll.add_widget(content)
        root.add_widget(scroll)

        wrapper.add_widget(root)
        self.add_widget(wrapper)
