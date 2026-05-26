"""资源路径与纹理加载工具。

同时兼容桌面调试和 Android 打包:
- 桌面:相对项目根的 `assets/...` 路径
- Android:Buildozer 打包后,`kivy.resources.resource_find` 会从 apk 中查找

使用示例:
    from app.utils.asset_loader import get_asset_path, load_texture

    path = get_asset_path("assets/images/cards/card_back.jpg")
    tex = load_texture("assets/images/cards/major_00_fool.jpg")
    if tex is None:
        # 资源不存在,做兜底展示
        ...
"""
from __future__ import annotations

import os
from typing import Optional


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def project_root() -> str:
    """返回项目根目录(桌面运行时对应 `tarot/` 目录)。"""
    return _PROJECT_ROOT


def get_asset_path(relative: str) -> Optional[str]:
    """查找资源文件,返回绝对路径或 None。

    查找顺序:
    1. 原样 (可能已经是绝对路径)
    2. 项目根目录
    3. kivy.resources.resource_find (打包后 apk 内资源)
    """
    if not relative:
        return None
    if os.path.isabs(relative) and os.path.exists(relative):
        return relative

    # 项目根 (桌面运行)
    abs_path = os.path.join(_PROJECT_ROOT, relative)
    if os.path.exists(abs_path):
        return abs_path

    # 打包环境:资源随 apk 解压,资源路径由 Buildozer 决定
    try:
        from kivy.resources import resource_find
    except ImportError:
        return None
    found = resource_find(relative)
    return found or None


def load_texture(relative: str):
    """加载一张图片为 Kivy Texture。失败返回 None,调用方需兜底处理。

    该函数不抛出异常,因为用户可能尚未放入完整的 22 张大阿卡那图片,
    此时应自动退化为文字/线稿占位。
    """
    path = get_asset_path(relative)
    if not path:
        return None
    try:
        from kivy.core.image import Image as CoreImage
        return CoreImage(path).texture
    except Exception:
        return None


def card_back_path() -> str:
    """统一的牌背图片相对路径。"""
    return "assets/images/cards/card_back.jpg"
