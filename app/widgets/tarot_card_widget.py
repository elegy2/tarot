"""塔罗牌组件:翻牌动画 + 牌面图片 + 逆位旋转 + 翻开后柔光。

设计要点:
1. 翻牌前只显示牌背(优先用户提供的 card_back.jpg,缺失时自绘星形图案)。
2. 翻牌前不显示牌名、英文名、正逆位、关键词。
3. 翻牌动画:水平缩窄 + 纵向轻压 -> 切换为真实牌面 -> 回弹 + 上浮 + 扩散光环。
4. 同一张牌只能翻一次,动画期间禁止重复点击。
5. 逆位通过 Rotate 把"牌面图像"旋转 180°,文字保持正方向。
6. 翻开后:金色边框 + 持续柔和呼吸光晕反馈,并显示牌名/正逆位/关键词。
7. idle 态(未翻开)牌背做缓慢呼吸浮动,"点击翻牌"提示透明度柔和脉动。
8. 入场支持错峰动画(淡入 + 轻微上浮),由外层调度器控制 delay。
"""
from __future__ import annotations

import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import (
    Color, Line, PopMatrix, PushMatrix, Rectangle, Rotate,
    RoundedRectangle, Scale,
)
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty, DictProperty, NumericProperty, StringProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.utils import theme as T
from app.utils.asset_loader import card_back_path, get_asset_path, load_texture


CARD_RATIO = 7 / 4


class TarotCardWidget(FloatLayout):
    """单张塔罗牌。card 数据结构同 TarotEngine.draw() 的单项。"""

    flipped = BooleanProperty(False)
    animating = BooleanProperty(False)
    card = DictProperty({})
    position = StringProperty("")
    face_scale_x = NumericProperty(1.0)
    face_scale_y = NumericProperty(1.0)
    glow = NumericProperty(0.0)
    revealed_glow = NumericProperty(0.0)
    idle_offset = NumericProperty(0.0)      # 牌背呼吸浮动(相对位移)
    hint_alpha = NumericProperty(1.0)       # "点击翻牌" 脉动透明度
    lift = NumericProperty(0.0)             # 翻牌瞬间的上浮位移(dp)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = kwargs.get("size_hint", (1, 1))

        self._position_label = Label(
            text=self.position, color=list(T.COLOR_GOLD),
            font_size=sp(11), bold=True, markup=True,
            size_hint=(0.7, None), height=dp(22),
            pos_hint={"center_x": 0.5, "top": 0.99},
            halign="center", valign="middle",
        )
        self._position_label.bind(size=lambda *_: setattr(
            self._position_label, "text_size", self._position_label.size))

        self._tap_hint = Label(
            text="点击翻牌", color=list(T.COLOR_TEXT_HINT),
            font_size=sp(10), markup=True,
            size_hint=(1, None), height=dp(16),
            pos_hint={"center_x": 0.5, "y": 0.04},
        )

        self._name_label = Label(
            text="", color=list(T.COLOR_TEXT), markup=True,
            halign="center", valign="middle", font_size=sp(11),
            size_hint=(0.94, None), height=dp(58),
            pos_hint={"center_x": 0.5, "y": 0.02},
            opacity=0,
        )
        self._name_label.bind(size=lambda *_: setattr(
            self._name_label, "text_size", self._name_label.size))

        self._face_image = Image(
            source="", fit_mode="contain",
            size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=0,
        )

        self.add_widget(self._face_image)
        self.add_widget(self._name_label)
        self.add_widget(self._position_label)
        self.add_widget(self._tap_hint)

        self.bind(
            size=self._redraw, pos=self._redraw,
            flipped=self._on_flipped_changed,
            position=self._on_position_changed,
            face_scale_x=self._redraw,
            face_scale_y=self._redraw,
            glow=self._redraw,
            revealed_glow=self._redraw,
            idle_offset=self._redraw,
            hint_alpha=self._on_hint_alpha_changed,
            lift=self._redraw,
        )
        self._idle_anim = None
        self._hint_anim = None
        self._reveal_breath_anim = None
        self._redraw()
        # 延迟一帧启动 idle,等 size/pos 稳定
        Clock.schedule_once(lambda *_: self._start_idle_anims(), 0)

    # ---------- 属性 ----------
    def _on_position_changed(self, *_a):
        self._position_label.text = (
            f"[b]· {self.position} ·[/b]" if self.flipped else self.position
        )

    def _on_flipped_changed(self, *_a):
        if self.flipped:
            self._show_front_texts()
            self._stop_idle_anims()
            self._start_reveal_breath()
        else:
            self._hide_front_texts()
            self._stop_reveal_breath()
            self._start_idle_anims()
        self._redraw()

    def _on_hint_alpha_changed(self, *_a):
        self._tap_hint.opacity = self.hint_alpha if not self.flipped else 0

    # ---------- idle / reveal 呼吸 ----------
    def _start_idle_anims(self):
        if self.flipped:
            return
        self._stop_idle_anims()
        # 牌背上下轻微浮动
        float_up = Animation(idle_offset=dp(3.2), duration=2.4, t="in_out_sine")
        float_down = Animation(idle_offset=-dp(1.8), duration=2.4,
                               t="in_out_sine")
        self._idle_anim = float_up + float_down
        self._idle_anim.repeat = True
        self._idle_anim.start(self)

        # 点击提示透明度脉动
        hint_dim = Animation(hint_alpha=0.35, duration=1.1, t="in_out_sine")
        hint_bright = Animation(hint_alpha=1.0, duration=1.1, t="in_out_sine")
        self._hint_anim = hint_dim + hint_bright
        self._hint_anim.repeat = True
        self._hint_anim.start(self)

    def _stop_idle_anims(self):
        if self._idle_anim is not None:
            self._idle_anim.cancel(self)
            self._idle_anim = None
        if self._hint_anim is not None:
            self._hint_anim.cancel(self)
            self._hint_anim = None
        self.idle_offset = 0.0

    def _start_reveal_breath(self):
        self._stop_reveal_breath()
        up = Animation(revealed_glow=1.0, duration=1.8, t="in_out_sine")
        down = Animation(revealed_glow=0.45, duration=1.8, t="in_out_sine")
        self._reveal_breath_anim = up + down
        self._reveal_breath_anim.repeat = True
        self._reveal_breath_anim.start(self)

    def _stop_reveal_breath(self):
        if self._reveal_breath_anim is not None:
            self._reveal_breath_anim.cancel(self)
            self._reveal_breath_anim = None

    # ---------- 对外 ----------
    def reveal(self):
        if self.flipped or self.animating:
            return
        self.animating = True
        self._stop_idle_anims()
        self._tap_hint.opacity = 0

        # 第一阶段:水平缩窄 + 纵向轻压 + 起光 + 上浮
        shrink = (
            Animation(face_scale_x=0.02, duration=0.22, t="in_cubic")
            & Animation(face_scale_y=0.94, duration=0.22, t="in_cubic")
            & Animation(glow=1.0, duration=0.22, t="out_quad")
            & Animation(lift=dp(6), duration=0.22, t="out_quad")
        )

        def _on_shrink_done(*_a):
            self._swap_to_face_image()
            expand = (
                Animation(face_scale_x=1.06, duration=0.22, t="out_cubic")
                & Animation(face_scale_y=1.03, duration=0.22, t="out_cubic")
            )
            settle = (
                Animation(face_scale_x=1.0, duration=0.16, t="out_quad")
                & Animation(face_scale_y=1.0, duration=0.16, t="out_quad")
                & Animation(lift=0.0, duration=0.16, t="out_quad")
            )
            fade_glow = Animation(glow=0.0, duration=0.45, t="out_quad")

            def _after_expand(*_a2):
                self.flipped = True
                settle.bind(
                    on_complete=lambda *_: setattr(self, "animating", False))
                settle.start(self)

            expand.bind(on_complete=_after_expand)
            expand.start(self)
            fade_glow.start(self)

        shrink.bind(on_complete=_on_shrink_done)
        shrink.start(self)

    def reveal_immediate(self):
        """直接翻到正面,不播动画。用于 resize 重建时保持已翻开状态。"""
        if self.flipped:
            return
        self._stop_idle_anims()
        self._swap_to_face_image()
        self.face_scale_x = 1.0
        self.face_scale_y = 1.0
        self.glow = 0.0
        self.lift = 0.0
        self.flipped = True
        self.animating = False

    def play_enter(self, delay: float = 0.0):
        """入场动画:从略低位置淡入并轻微上浮。"""
        Animation.cancel_all(self, "opacity", "idle_offset")
        self.opacity = 0.0
        self.idle_offset = -dp(10)
        anim = (
            Animation(opacity=1.0, duration=0.38, t="out_quad")
            & Animation(idle_offset=0.0, duration=0.42, t="out_back")
        )

        def _after_enter(*_a):
            # 入场结束后重启 idle 呼吸
            if not self.flipped:
                self._start_idle_anims()

        anim.bind(on_complete=_after_enter)
        # 入场期间暂停 idle,避免抢占 idle_offset
        self._stop_idle_anims()
        if delay > 0:
            Clock.schedule_once(lambda *_: anim.start(self), delay)
        else:
            anim.start(self)

    def flip_to_front(self):
        self.reveal()

    def on_touch_down(self, touch):
        if (self.collide_point(*touch.pos) and not self.flipped
                and not self.animating):
            self.reveal()
            return True
        return super().on_touch_down(touch)

    # ---------- 内部 ----------
    def _swap_to_face_image(self):
        card = self.card or {}
        img_rel = card.get("image", "")
        img_abs = get_asset_path(img_rel) if img_rel else None
        if img_abs:
            self._face_image.source = img_abs
            self._face_image.reload()
            self._face_image.opacity = 1
        else:
            self._face_image.source = ""
            self._face_image.opacity = 0

    def _show_front_texts(self):
        card = self.card or {}
        if not card:
            return
        orient = card.get("orientation", "")
        # 正位金色,逆位淡紫
        orient_color = "d4af37" if orient == "正位" else "c9a4ff"
        name_cn = card.get("card_name_cn", "")
        name_en = card.get("card_name_en", "")
        kw = "、".join(card.get("keywords", [])[:3])
        self._name_label.text = (
            f"[b][color=f5f1e8]{name_cn}[/color][/b]  "
            f"[size=10sp][color=b0a8c8]{name_en}[/color][/size]\n"
            f"[color={orient_color}]{orient}[/color]  "
            f"[size=10sp][color=c8c0d8]{kw}[/color][/size]"
        )
        self._name_label.opacity = 1
        self._tap_hint.opacity = 0
        # 位置标签翻开后变得更明显
        self._position_label.text = f"[b]· {self.position} ·[/b]"

    def _hide_front_texts(self):
        self._name_label.text = ""
        self._name_label.opacity = 0
        self._face_image.opacity = 0
        self._tap_hint.opacity = self.hint_alpha
        self.revealed_glow = 0.0

    # ---------- 绘制 ----------
    def _redraw(self, *_a):
        self.canvas.before.clear()
        self.canvas.after.clear()
        # 关键: 同步清空 face_image 的 before/after, 否则每次 _redraw 追加的
        # PushMatrix + Scale 会持续累积。动画期间 scale 会经过 0.02 这种极小值,
        # 累积乘积会让图片永远渲染在近 0 尺寸下, 导致翻牌后看不到牌面。
        self._face_image.canvas.before.clear()
        self._face_image.canvas.after.clear()

        # 牌背时整体根据 idle_offset / lift 轻微偏移(只影响绘制,不挪动子 widget)
        dy = 0.0
        if not self.flipped:
            dy = self.idle_offset
        dy += self.lift

        with self.canvas.before:
            self._draw_card_base(dy)
            if self.glow > 0.01:
                self._draw_flip_glow(dy)
            if self.revealed_glow > 0.01 and self.flipped:
                self._draw_revealed_glow(dy)
            if not self.flipped:
                self._draw_back_pattern(dy)

        if self.flipped or self.face_scale_x < 0.99 or self.face_scale_y < 0.99:
            with self._face_image.canvas.before:
                PushMatrix()
                cx = self._face_image.center_x
                cy = self._face_image.center_y + dy
                Scale(origin=(cx, cy),
                      x=self.face_scale_x, y=self.face_scale_y, z=1)
                if self._is_reversed():
                    Rotate(angle=180, origin=(cx, cy))
            with self._face_image.canvas.after:
                PopMatrix()

        with self.canvas.after:
            if self.flipped:
                # 主金色边框
                Color(*T.COLOR_GOLD)
                Line(rounded_rectangle=(
                    self.x + dp(2), self.y + dp(2) + dy,
                    self.width - dp(4), self.height - dp(4), dp(12),
                ), width=1.4)
                # 翻开后:四角金色装饰角 + 位置 chip 背景
                self._draw_corner_accents(dy)
                self._draw_position_chip(dy)
                self._draw_bottom_info_strip(dy)

    def _draw_card_base(self, dy: float = 0.0):
        Color(*T.COLOR_BG_INDIGO)
        RoundedRectangle(pos=(self.x, self.y + dy),
                         size=self.size, radius=[dp(14)])
        pad = dp(6)
        Color(0.12, 0.08, 0.22, 1)
        RoundedRectangle(
            pos=(self.x + pad, self.y + pad + dy),
            size=(self.width - pad * 2, self.height - pad * 2),
            radius=[dp(10)],
        )
        # 静态外描边(总是有,但不抢光晕风头)
        if not self.flipped:
            Color(*T.COLOR_GOLD_SOFT)
            Line(rounded_rectangle=(
                self.x + dp(1), self.y + dp(1) + dy,
                self.width - dp(2), self.height - dp(2), dp(14),
            ), width=1.2)

    def _draw_back_pattern(self, dy: float = 0.0):
        back_rel = card_back_path()
        back_path = get_asset_path(back_rel)
        pad = dp(10)
        if back_path:
            try:
                tex = load_texture(back_rel)
            except Exception:
                tex = None
            if tex is not None:
                Color(1, 1, 1, 1)
                Rectangle(
                    texture=tex,
                    pos=(self.x + pad, self.y + pad + dy),
                    size=(self.width - pad * 2, self.height - pad * 2),
                )
                Color(*T.COLOR_GOLD)
                Line(rounded_rectangle=(
                    self.x + pad, self.y + pad + dy,
                    self.width - pad * 2, self.height - pad * 2, dp(10),
                ), width=1.0)
                return

        # 兜底:简洁神秘图案
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2 + dy
        size = min(self.width, self.height) * 0.32
        Color(0.83, 0.69, 0.21, 0.85)
        Line(points=[cx - size / 2, cy, cx + size / 2, cy], width=1.3)
        Line(points=[cx, cy - size / 2, cx, cy + size / 2], width=1.3)
        Line(points=[cx - size * 0.35, cy - size * 0.35,
                     cx + size * 0.35, cy + size * 0.35], width=1)
        Line(points=[cx - size * 0.35, cy + size * 0.35,
                     cx + size * 0.35, cy - size * 0.35], width=1)
        Color(0.83, 0.69, 0.21, 0.5)
        steps = 36
        pts = []
        radius = size * 0.55
        for i in range(steps + 1):
            ang = i * 2 * math.pi / steps
            pts.append(cx + radius * math.cos(ang))
            pts.append(cy + radius * math.sin(ang))
        Line(points=pts, width=1)

    def _draw_flip_glow(self, dy: float = 0.0):
        # 翻牌瞬间:多层扩散光环
        base = min(0.6, self.glow * 0.55)
        for i in range(3):
            a = base * (1.0 - i * 0.28)
            if a <= 0.01:
                continue
            Color(1.0, 0.84, 0.35, a)
            ext = dp(6) * self.glow + i * dp(3) * self.glow
            Line(rounded_rectangle=(
                self.x - ext, self.y - ext + dy,
                self.width + 2 * ext, self.height + 2 * ext,
                dp(18) + ext,
            ), width=2.4 - i * 0.6)

    def _draw_revealed_glow(self, dy: float = 0.0):
        # 翻开后柔和金色光环,呼吸式波动
        a = 0.10 * self.revealed_glow + 0.04
        for i in range(3):
            layer_a = a * (1.0 - i * 0.3)
            Color(1.0, 0.85, 0.4, max(0.02, layer_a))
            ext = dp(2) + i * dp(3) + dp(2) * self.revealed_glow
            Line(rounded_rectangle=(
                self.x - ext, self.y - ext + dy,
                self.width + 2 * ext, self.height + 2 * ext,
                dp(16) + ext,
            ), width=1.0)

    def _draw_corner_accents(self, dy: float = 0.0):
        """翻开后:四角金色 L 形装饰角。"""
        size = min(dp(14), self.width * 0.10)
        inset = dp(6)
        Color(1.0, 0.84, 0.35, 0.85)
        x_l = self.x + inset
        x_r = self.x + self.width - inset
        y_b = self.y + inset + dy
        y_t = self.y + self.height - inset + dy
        # 左上
        Line(points=[x_l, y_t, x_l + size, y_t], width=1.4)
        Line(points=[x_l, y_t, x_l, y_t - size], width=1.4)
        # 右上
        Line(points=[x_r, y_t, x_r - size, y_t], width=1.4)
        Line(points=[x_r, y_t, x_r, y_t - size], width=1.4)
        # 左下
        Line(points=[x_l, y_b, x_l + size, y_b], width=1.4)
        Line(points=[x_l, y_b, x_l, y_b + size], width=1.4)
        # 右下
        Line(points=[x_r, y_b, x_r - size, y_b], width=1.4)
        Line(points=[x_r, y_b, x_r, y_b + size], width=1.4)

    def _draw_position_chip(self, dy: float = 0.0):
        """翻开后:顶部位置 chip 的半透明深色底 + 金色细边。"""
        chip_w = self.width * 0.62
        chip_h = dp(22)
        cx = self.x + self.width / 2
        chip_x = cx - chip_w / 2
        chip_y = self.y + self.height - chip_h - dp(4) + dy
        # 底
        Color(0.06, 0.04, 0.12, 0.85)
        RoundedRectangle(
            pos=(chip_x, chip_y), size=(chip_w, chip_h),
            radius=[dp(11)],
        )
        # 描边
        Color(1.0, 0.84, 0.35, 0.7)
        Line(rounded_rectangle=(chip_x, chip_y, chip_w, chip_h, dp(11)),
             width=1.0)

    def _draw_bottom_info_strip(self, dy: float = 0.0):
        """翻开后:卡牌下半部一条半透明深色信息条,提升文字可读性。"""
        strip_h = dp(62)
        strip_x = self.x + dp(6)
        strip_y = self.y + dp(6) + dy
        strip_w = self.width - dp(12)
        Color(0.05, 0.03, 0.10, 0.55)
        RoundedRectangle(
            pos=(strip_x, strip_y), size=(strip_w, strip_h),
            radius=[dp(10)],
        )
        # 信息条上沿一道金色细线
        Color(1.0, 0.84, 0.35, 0.35)
        Line(points=[strip_x + dp(8), strip_y + strip_h,
                     strip_x + strip_w - dp(8), strip_y + strip_h],
             width=1.0)

    def _is_reversed(self) -> bool:
        return (self.card or {}).get("orientation") == "逆位"
