"""向后兼容:StarryBackground = MysticBackground(动画版)。

新代码请直接 import MysticBackground。
"""
from __future__ import annotations

from app.widgets.mystic_background import MysticBackground


class StarryBackground(MysticBackground):
    def __init__(self, **kwargs):
        kwargs.setdefault("animated", False)
        super().__init__(**kwargs)
