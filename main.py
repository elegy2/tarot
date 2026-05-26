"""灵境塔罗应用入口。

运行:
    python main.py

Android 打包:
    buildozer -v android debug
"""
from __future__ import annotations

import os

from kivy.config import Config

# 默认竖屏 + 桌面调试窗口尺寸。Android 端由 buildozer.spec 控制竖屏。
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "760")
Config.set("graphics", "minimum_width", "320")
Config.set("graphics", "minimum_height", "520")
Config.set("graphics", "resizable", "1")
# 不要在桌面也锁定方向,只在 Android 打包清单里锁
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App                # noqa: E402
from kivy.core.text import LabelBase    # noqa: E402
from kivy.uix.screenmanager import FadeTransition, ScreenManager  # noqa: E402

from app.services.config_manager import ConfigManager  # noqa: E402


def _register_chinese_font() -> None:
    """注册中文字体, 确保 CJK 字符与 [b] 加粗标记都能正确显示。

    优先级:
        1. 项目自带 assets/fonts/zh.ttf (打包推荐)
        2. Windows 微软雅黑 / 黑体
        3. macOS 苹方
        4. Android Noto / DroidSans
    同时尝试匹配同字体族的 Bold 文件 (msyhbd / PingFang Bold), 找到就一并
    注册为 fn_bold; 找不到则让 Kivy 回退到合成加粗。
    """
    base = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(base, "assets", "fonts", "zh.ttf")
    local_bold = os.path.join(base, "assets", "fonts", "zh_bold.ttf")

    # (regular_path, bold_path_or_None)
    candidates = [
        (local, local_bold if os.path.exists(local_bold) else None),
        # Windows
        (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"),
        (r"C:\Windows\Fonts\msyh.ttf", r"C:\Windows\Fonts\msyhbd.ttf"),
        (r"C:\Windows\Fonts\simhei.ttf", None),
        # macOS
        ("/System/Library/Fonts/PingFang.ttc", None),
        ("/System/Library/Fonts/STHeiti Medium.ttc", None),
        # Android
        ("/system/fonts/NotoSansCJK-Regular.ttc", "/system/fonts/NotoSansCJK-Bold.ttc"),
        ("/system/fonts/DroidSansFallback.ttf", None),
    ]

    for regular, bold in candidates:
        if not regular or not os.path.exists(regular):
            continue
        kwargs = {"name": "Roboto", "fn_regular": regular}
        if bold and os.path.exists(bold):
            kwargs["fn_bold"] = bold
        try:
            LabelBase.register(**kwargs)
        except Exception:
            # 不同 Kivy 版本签名略有差异, 回退到最简形式
            try:
                LabelBase.register(name="Roboto", fn_regular=regular)
            except Exception:
                continue
        return


def _register_resource_paths() -> None:
    """把 assets 目录加入 kivy.resources 的查找路径,便于 widget 查找资源。

    Buildozer 打包后,assets 目录会随 apk 被解压到 app 私有目录。
    这里同时加入桌面和打包后两种场景的搜索路径。
    """
    from kivy.resources import resource_add_path
    base = os.path.dirname(os.path.abspath(__file__))
    for sub in ("", "assets", os.path.join("assets", "images"),
                os.path.join("assets", "images", "cards"),
                os.path.join("assets", "images", "backgrounds"),
                os.path.join("assets", "images", "icons"),
                os.path.join("assets", "fonts")):
        path = os.path.join(base, sub) if sub else base
        if os.path.isdir(path):
            resource_add_path(path)


class TarotApp(App):
    title = "灵境塔罗"

    def build(self):
        base = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base, "assets", "images", "icons", "app_icon.png")
        # 兼容旧路径
        legacy_icon = os.path.join(base, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.icon = icon_path
        elif os.path.exists(legacy_icon):
            self.icon = legacy_icon

        # 本地配置与会话状态
        self.config_manager = ConfigManager(self.user_data_dir)
        self.session: dict = {}

        from app.screens.home_screen import HomeScreen
        from app.screens.spread_select_screen import SpreadSelectScreen
        from app.screens.question_screen import QuestionScreen
        from app.screens.draw_screen import DrawScreen
        from app.screens.result_screen import ResultScreen
        from app.screens.settings_screen import SettingsScreen
        from app.screens.history_screen import HistoryScreen
        from app.screens.about_screen import AboutScreen

        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(HomeScreen())
        sm.add_widget(SpreadSelectScreen())
        sm.add_widget(QuestionScreen())
        sm.add_widget(DrawScreen())
        sm.add_widget(ResultScreen())
        sm.add_widget(SettingsScreen())
        sm.add_widget(HistoryScreen())
        sm.add_widget(AboutScreen())
        sm.current = "home"
        return sm


if __name__ == "__main__":
    _register_chinese_font()
    _register_resource_paths()
    TarotApp().run()
