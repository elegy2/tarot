"""可自动撑高的 Label。

Kivy 默认 Label 不会随文字撑高,长 AI 解读文本一旦放进 ScrollView 就会被截断。
本组件解决这个问题:把 size_hint_y 锁为 None,绑定 width -> text_size,
绑定 texture_size -> height,自动按文本实际高度伸展。
"""
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.label import Label


class AutoWrapLabel(Label):
    def __init__(self, padding_y: float = 0, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("markup", False)
        super().__init__(**kwargs)
        self._padding_y = padding_y
        self.size_hint_y = None
        self.bind(width=self._update_text_size,
                  texture_size=self._update_height)
        # 初始触发一次,防止首屏不撑开
        self._update_text_size()

    def _update_text_size(self, *_a):
        self.text_size = (self.width, None)

    def _update_height(self, *_a):
        # +padding_y 留一点行间富余,避免最后一行紧贴底
        self.height = self.texture_size[1] + self._padding_y
