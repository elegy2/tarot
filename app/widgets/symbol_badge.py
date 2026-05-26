"""塔罗主题的纯矢量符号徽章。

用 Canvas 直接绘制简单符号,免除外部 SVG/字体依赖,适合做小尺寸装饰。
支持的符号(symbol):
    moon       上弦月
    sun        太阳带光芒
    star       五角星
    star8      八角星
    diamond    菱形
    cross      凯尔特十字
    heart      简化心形(三段直线轮廓)
    suit_cup   圣杯
    suit_sword 剑
    suit_wand  权杖
    suit_pent  五角钱币

颜色由 stroke / fill 控制,默认金色。
"""
from __future__ import annotations

import math

from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import (
    ListProperty, NumericProperty, StringProperty,
)
from kivy.uix.widget import Widget

from app.utils import theme as T


class SymbolBadge(Widget):
    """绘制一个塔罗主题符号。"""

    symbol = StringProperty("star")
    stroke = ListProperty(list(T.COLOR_GOLD))
    fill = ListProperty([0, 0, 0, 0])
    line_width = NumericProperty(1.4)
    inset = NumericProperty(0.18)  # 内边距比例,符号不会贴边

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            size=self._redraw, pos=self._redraw,
            symbol=self._redraw, stroke=self._redraw,
            fill=self._redraw, line_width=self._redraw,
            inset=self._redraw,
        )

    # ---------- 公共 ----------
    def _redraw(self, *_a):
        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return
        with self.canvas:
            handler = getattr(self, f"_draw_{self.symbol}", None)
            if handler is None:
                self._draw_star()
            else:
                handler()

    # ---------- 几何辅助 ----------
    def _box(self):
        pad = min(self.width, self.height) * self.inset
        x0 = self.x + pad
        y0 = self.y + pad
        w = self.width - 2 * pad
        h = self.height - 2 * pad
        return x0, y0, w, h

    def _set_stroke(self, alpha_mul: float = 1.0):
        r, g, b, a = self.stroke
        Color(r, g, b, a * alpha_mul)

    def _set_fill(self, alpha_mul: float = 1.0):
        r, g, b, a = self.fill
        Color(r, g, b, a * alpha_mul)

    # ---------- 符号实现 ----------
    def _draw_moon(self):
        x, y, w, h = self._box()
        size = min(w, h)
        cx = x + w / 2
        cy = y + h / 2
        r = size / 2
        # 主圆(描边)
        self._set_fill()
        if self.fill[3] > 0:
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
        self._set_stroke()
        Line(circle=(cx, cy, r), width=self.line_width)
        # 阴影圆,做出月相
        self._set_stroke(0.35)
        Line(circle=(cx + r * 0.30, cy + r * 0.05, r * 0.92),
             width=self.line_width)

    def _draw_sun(self):
        x, y, w, h = self._box()
        size = min(w, h)
        cx = x + w / 2
        cy = y + h / 2
        r = size * 0.32
        self._set_stroke()
        Line(circle=(cx, cy, r), width=self.line_width)
        # 8 道光芒
        for i in range(8):
            ang = i * math.pi / 4
            x1 = cx + r * 1.18 * math.cos(ang)
            y1 = cy + r * 1.18 * math.sin(ang)
            x2 = cx + r * 1.7 * math.cos(ang)
            y2 = cy + r * 1.7 * math.sin(ang)
            Line(points=[x1, y1, x2, y2], width=self.line_width)

    def _polygon_points(self, cx, cy, r, points: int, rotation: float = 0):
        pts = []
        for i in range(points + 1):
            ang = rotation + i * 2 * math.pi / points
            pts.append(cx + r * math.cos(ang))
            pts.append(cy + r * math.sin(ang))
        return pts

    def _star_points(self, cx, cy, r_outer, r_inner, points: int = 5,
                     rotation: float = -math.pi / 2):
        pts = []
        n = points * 2
        for i in range(n + 1):
            r = r_outer if i % 2 == 0 else r_inner
            ang = rotation + i * math.pi / points
            pts.append(cx + r * math.cos(ang))
            pts.append(cy + r * math.sin(ang))
        return pts

    def _draw_star(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 2
        self._set_stroke()
        Line(points=self._star_points(cx, cy, r, r * 0.45, points=5),
             width=self.line_width)

    def _draw_star8(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 2
        self._set_stroke()
        Line(points=self._star_points(cx, cy, r, r * 0.55, points=8),
             width=self.line_width)

    def _draw_diamond(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 2
        self._set_stroke()
        Line(points=[
            cx, cy + r,
            cx + r, cy,
            cx, cy - r,
            cx - r, cy,
            cx, cy + r,
        ], width=self.line_width)

    def _draw_cross(self):
        # 凯尔特十字:十字 + 围圆
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 2
        self._set_stroke()
        Line(circle=(cx, cy, r * 0.78), width=self.line_width)
        Line(points=[cx - r, cy, cx + r, cy], width=self.line_width)
        Line(points=[cx, cy - r, cx, cy + r], width=self.line_width)

    def _draw_heart(self):
        # 简化轮廓:两段弧 + V 字
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) * 0.30
        self._set_stroke()
        # 左弧
        pts_l = []
        for i in range(0, 18):
            ang = math.pi - i * math.pi / 18
            pts_l.append(cx - r + r * math.cos(ang))
            pts_l.append(cy + r * 0.4 + r * math.sin(ang))
        Line(points=pts_l, width=self.line_width)
        # 右弧
        pts_r = []
        for i in range(0, 18):
            ang = math.pi - i * math.pi / 18
            pts_r.append(cx + r + r * math.cos(ang))
            pts_r.append(cy + r * 0.4 + r * math.sin(ang))
        Line(points=pts_r, width=self.line_width)
        # 下半 V
        Line(points=[cx - 2 * r, cy + r * 0.4,
                     cx, cy - r * 1.05,
                     cx + 2 * r, cy + r * 0.4], width=self.line_width)

    def _draw_suit_cup(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        size = min(w, h)
        self._set_stroke()
        # U 形杯身
        Line(points=[
            cx - size * 0.35, cy + size * 0.32,
            cx - size * 0.35, cy - size * 0.05,
        ], width=self.line_width)
        Line(points=[
            cx + size * 0.35, cy + size * 0.32,
            cx + size * 0.35, cy - size * 0.05,
        ], width=self.line_width)
        # 杯底圆弧
        pts = []
        for i in range(19):
            ang = math.pi + i * math.pi / 18
            pts.append(cx + size * 0.35 * math.cos(ang))
            pts.append(cy - size * 0.05 + size * 0.20 * math.sin(ang))
        Line(points=pts, width=self.line_width)
        # 杯托
        Line(points=[cx - size * 0.18, cy - size * 0.36,
                     cx + size * 0.18, cy - size * 0.36],
             width=self.line_width)
        Line(points=[cx, cy - size * 0.25, cx, cy - size * 0.36],
             width=self.line_width)

    def _draw_suit_sword(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        size = min(w, h)
        self._set_stroke()
        # 剑刃
        Line(points=[cx, cy + size * 0.45, cx, cy - size * 0.20],
             width=self.line_width + 0.4)
        # 护手
        Line(points=[cx - size * 0.25, cy - size * 0.20,
                     cx + size * 0.25, cy - size * 0.20],
             width=self.line_width)
        # 剑柄
        Line(points=[cx, cy - size * 0.20, cx, cy - size * 0.42],
             width=self.line_width)
        # 圆头
        Line(circle=(cx, cy - size * 0.45, size * 0.04),
             width=self.line_width)

    def _draw_suit_wand(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        size = min(w, h)
        self._set_stroke()
        # 主权杖斜线
        Line(points=[cx - size * 0.32, cy - size * 0.40,
                     cx + size * 0.32, cy + size * 0.40],
             width=self.line_width + 0.4)
        # 三个枝节
        for f in (-0.18, 0.0, 0.18):
            x1 = cx + f * size * 0.6 - size * 0.10
            y1 = cy + f * size * 0.6 + size * 0.06
            x2 = cx + f * size * 0.6 + size * 0.06
            y2 = cy + f * size * 0.6 - size * 0.10
            Line(points=[x1, y1, x2, y2], width=self.line_width)

    def _draw_suit_pent(self):
        x, y, w, h = self._box()
        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 2
        self._set_stroke()
        Line(circle=(cx, cy, r), width=self.line_width)
        Line(points=self._star_points(cx, cy, r * 0.78, r * 0.30,
                                      points=5),
             width=self.line_width)


# 牌阵 key -> 推荐符号
SPREAD_SYMBOL = {
    "single": "moon",
    "three": "star",
    "love": "heart",
    "career": "suit_pent",
    "celtic": "cross",
}


def symbol_for_spread(key: str) -> str:
    return SPREAD_SYMBOL.get(key, "star8")
