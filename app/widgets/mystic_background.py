"""神秘星空背景:深紫渐变 + 月亮 + 静态星点。

性能要点:
- 星点位置只在尺寸变化时重新生成,不每帧重建。
- 使用纹理化的竖直渐变贴图,避免每帧大量像素计算。
- 默认不开启动画(脉动),可通过 animated=True 启用,但 Android 上建议关闭以省电。
"""
from __future__ import annotations

import math
import random

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.widget import Widget

from app.utils import theme as T


def _build_gradient_texture(top, bottom, height: int = 256) -> Texture:
    tex = Texture.create(size=(1, height), colorfmt="rgb")
    pixels = bytearray()
    for y in range(height):
        t = y / max(1, height - 1)
        # 反转:y=0 在底部,y=height-1 在顶部(Kivy y 向上)
        rr = int((bottom[0] * (1 - t) + top[0] * t) * 255)
        gg = int((bottom[1] * (1 - t) + top[1] * t) * 255)
        bb = int((bottom[2] * (1 - t) + top[2] * t) * 255)
        pixels += bytes([rr, gg, bb])
    tex.blit_buffer(bytes(pixels), colorfmt="rgb", bufferfmt="ubyte")
    return tex


class MysticBackground(Widget):
    """神秘星空背景。"""

    NUM_STARS = 80
    animated = BooleanProperty(False)
    tick = NumericProperty(0.0)

    def __init__(self, animated: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._gradient = _build_gradient_texture(
            top=T.COLOR_BG_TOP[:3],
            bottom=T.COLOR_BG_BOTTOM[:3],
            height=256,
        )
        self._stars = []
        self.animated = animated
        self.bind(size=self._on_resize, pos=self._redraw,
                  tick=self._redraw)
        self._on_resize()
        if self.animated:
            Clock.schedule_interval(self._animate, 1 / 18.0)

    # ---------- 生成与刷新 ----------
    def _on_resize(self, *_a):
        self._build_stars()
        self._redraw()

    def _build_stars(self):
        rng = random.Random(20260509)  # 固定种子,布局稳定不抖动
        self._stars = []
        for _ in range(self.NUM_STARS):
            x = rng.random()
            y = rng.random()
            r = rng.uniform(0.8, 2.4)
            phase = rng.uniform(0, math.pi * 2)
            self._stars.append((x, y, r, phase))

    def _animate(self, _dt):
        self.tick += 0.06

    # ---------- 绘制 ----------
    def _redraw(self, *_a):
        self.canvas.clear()
        with self.canvas:
            # 渐变底
            Color(1, 1, 1, 1)
            Rectangle(texture=self._gradient, pos=self.pos, size=self.size)

            # 紫色光晕(中部偏上)
            Color(0.55, 0.42, 0.85, 0.06)
            r1 = self.width * 0.7
            Ellipse(pos=(self.x + self.width * 0.15,
                         self.y + self.height * 0.45),
                    size=(r1, r1))

            # 右上角月亮(简单两层圆)
            mr = max(dp(40), self.width * 0.10)
            mx = self.x + self.width * 0.78
            my = self.y + self.height * 0.84
            Color(0.92, 0.88, 0.98, 0.18)
            Ellipse(pos=(mx, my), size=(mr, mr))
            Color(*T.COLOR_BG_BOTTOM)
            Ellipse(pos=(mx + mr * 0.22, my + mr * 0.18),
                    size=(mr * 0.85, mr * 0.85))

            # 星点
            t = float(self.tick)
            for x, y, r, phase in self._stars:
                if self.animated:
                    alpha = 0.30 + 0.30 * math.sin(t + phase)
                else:
                    alpha = 0.45 + 0.20 * math.sin(phase)
                Color(0.95, 0.92, 0.85, max(0.10, alpha))
                cx = self.x + x * self.width
                cy = self.y + y * self.height
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

            # 顶部一条金色细线作为视觉锚
            Color(0.83, 0.69, 0.21, 0.18)
            Line(points=[
                self.x, self.y + self.height * 0.965,
                self.x + self.width, self.y + self.height * 0.965,
            ], width=1)
