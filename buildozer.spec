[app]
title = 灵境塔罗
package.name = mystictarot
package.domain = org.mystictarot

source.dir = .
# 打包时包含的资源类型:塔罗图片/背景图/字体/UI 文件等
source.include_exts = py,png,jpg,jpeg,kv,json,ttf,otf,ttc

version = 0.1.0

# Python 依赖。openai 会自动带上 httpx / pydantic 等。
# 若在打包环境里 openai 太重,可移除 openai,DeepSeekClient 会在 ImportError 时友好提示。
requirements = python3,kivy==2.3.0,openai,httpx,anyio,sniffio,pydantic,pydantic-core,typing-extensions,certifi,charset-normalizer,idna,urllib3

# 强制竖屏 + 非全屏(保留系统栏方便返回)
orientation = portrait
fullscreen = 0

# 权限:只需要访问网络即可
android.permissions = INTERNET

# 支持的 Android API 级别
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1

# 资源图标 / 开屏图(准备好后去掉注释即可启用)
# icon.filename = assets/images/icons/app_icon.png
# presplash.filename = assets/images/backgrounds/presplash.png

# 允许 https 请求(Android 9+ 默认只允许 https,已够用)
# 如需支持明文 HTTP,启用下方一行
# android.allow_cleartext_traffic = True

[buildozer]
log_level = 2
warn_on_root = 1
