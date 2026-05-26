# 灵境塔罗 · Mystic Tarot

一款基于 **Python + Kivy** 的安卓塔罗占卜应用。
不依赖任何数据库,所有数据以 JSON 保存在手机本地;AI 解牌通过你自己配置的 **DeepSeek API** 完成。

## 特性

- 22 张大阿卡那完整牌义,正逆位独立
- 逆位通过把牌面图片旋转 180° 实现,**不需要单独的逆位图片**
- 5 种牌阵:单牌、三牌阵、爱情、事业、凯尔特十字
- 神秘翻牌动画:缩窄 → 切换牌面 → 回弹展开 + 金色光晕 + 翻开后柔光环
- 翻牌前只显示牌背,绝不泄露真实牌面 / 牌名 / 正逆位 / 关键词
- 响应式布局,宽屏横排、小屏自动纵排,全部使用 `dp/sp`
- DeepSeek API 解牌,system prompt 明确**禁止 Markdown**,前端再用 `sanitize_ai_text` 二次清理
- AI 解读长文本走 `ScrollView + AutoWrapLabel(按段拆分)`,长内容稳定撑高、可滚动、不溢出
- 未配置 API Key 时使用本地牌义兜底,不会崩溃
- 本地 JSON 历史记录,可单条删除 / 一键清空
- API Key 仅保存在本机,默认脱敏显示 `sk-****xxxx`

## 目录结构

```
tarot/
├── main.py
├── requirements.txt
├── buildozer.spec
├── README.md
├── app/
│   ├── theme.py                      # 旧 import 兼容,转发到 utils/theme
│   ├── data/                         # 塔罗牌 + 牌阵
│   ├── services/                     # ConfigManager / DeepSeekClient / TarotEngine
│   ├── widgets/
│   │   ├── mystic_background.py      # 神秘星空背景
│   │   ├── mystic_button.py          # 圆角金边按钮 + loading 状态
│   │   ├── mystic_panel.py           # 暗紫圆角面板
│   │   ├── auto_wrap_label.py        # 自动撑高的 Label,长文本必备
│   │   ├── tarot_card_widget.py      # 塔罗卡片 + 翻牌动画
│   │   └── starry_background.py      # 兼容旧 import
│   ├── screens/                      # 首页/牌阵/问题/抽牌/结果/设置/历史/关于
│   └── utils/
│       ├── theme.py                  # 颜色 / 字号 / 间距常量
│       ├── responsive.py             # 屏幕断点 + 自适应工具
│       ├── text_formatter.py         # AI 文本清理 sanitize_ai_text
│       └── asset_loader.py           # 跨平台资源路径
└── assets/
    ├── fonts/                        # 可放 zh.ttf 保证中文显示
    └── images/
        ├── cards/                    # 22 张大阿卡那 + card_back.jpg
        ├── backgrounds/              # 可选:应用背景图
        └── icons/                    # 可选:应用图标
```

## 本地运行

```bash
pip install -r requirements.txt
python main.py
```

首次启动会在系统 `user_data_dir` 下生成 `config.json`:

- Windows: `%APPDATA%\mystictarot`
- macOS:   `~/Library/Application Support/mystictarot`
- Android: `/data/data/org.mystictarot.mystictarot/files`

## 配置 DeepSeek API Key

两种方式任选其一:

1. 环境变量(桌面调试推荐,不会落盘):

   ```powershell
   # Windows PowerShell
   $env:DEEPSEEK_API_KEY = "sk-你的key"
   ```

   ```bash
   # bash / zsh
   export DEEPSEEK_API_KEY=sk-你的key
   ```

2. 应用内「API 设置」页面填入并保存。

应用代码中绝不硬编码任何 Key。日志中只会显示脱敏后的 Key。

---

## 前端自适应说明

- 所有尺寸都来自 `dp()` / `sp()`,不写死像素。
- `app/utils/responsive.py` 集中管理屏幕断点:

  | 类别       | 宽度阈值        |
  | -------- | ----------- |
  | compact  | < 380dp     |
  | phone    | 380 ~ 720dp |
  | wide     | ≥ 720dp     |

- 标题字号、正文字号、按钮高度、卡牌大小、内容最大宽度都按断点动态调整。
- 三牌阵/凯尔特十字等多牌阵在窗口宽度 < 540dp 时自动改为**纵向滚动**;
  ≥ 540dp 时**横向并排**,可水平滚动。
- `Window.bind(size=...)` 监听窗口尺寸变化,首页、抽牌页都会重新布局。
- 内容最大宽度限制在 `min(width * 0.94, 720dp)`,避免桌面宽屏文字一行铺满难以阅读。

## AI 长文本前端处理

DeepSeek 回复经常很长(900~1400 字)。前端策略:

1. 整页结果区使用 `ScrollView + BoxLayout(size_hint_y=None) + minimum_height`。
2. AI 解读再放进一个 `MysticPanel`,内部按空行**拆段**,每段一个 `AutoWrapLabel`。
3. `AutoWrapLabel` 绑定 `width -> text_size`、`texture_size -> height`,
   长文本自动换行并撑高,绝不溢出。
4. 段与段之间留 `dp(8)` 间距,阅读体验更好。
5. 底部按钮区使用独立 BoxLayout,不会被长文本挤出屏幕。

## DeepSeek 输出 Markdown 怎么办?

本应用采取「双保险」策略:

1. **system prompt 明确禁止 Markdown**(见 `app/services/deepseek_client.py` 的 `SYSTEM_PROMPT`)。
2. 不论模型是否听话,前端都会再用 `app/utils/text_formatter.py` 的 `sanitize_ai_text()` 清理:
   - 三反引号代码块 / 行内反引号
   - 行首 `#` 标题
   - 加粗 `**` / `__`、斜体 `*` / `_`
   - 项目符号(行首 `-`、`*`、`•`)
   - Markdown 表格分隔线 / 单元格竖线
   - HTML 标签
   - 多余空行
3. 清理只动"展示层",不改变中文语义。
4. 历史记录中的旧文本在再次查看时也会经过 `sanitize_ai_text` 二次清理。

---

## 前端资源与图片规范

图片优先 + 无图兜底:

- 你提供了图片 → 显示真实牌面 / 牌背。
- 你没提供 → 自动退化为 Canvas 自绘版本,功能仍然可用。

### 目录

```
assets/images/cards/           # 塔罗牌正面 + 统一牌背
assets/images/backgrounds/     # (可选)应用背景图、开屏图
assets/images/icons/           # (可选)应用图标
assets/fonts/                  # (可选)中文字体 zh.ttf
```

### 必须提供

| 名称 | 路径 | 说明 |
| --- | --- | --- |
| 牌背 | `assets/images/cards/card_back.jpg` | 所有未翻开的牌都用这张 |

### 22 张大阿卡那正面(第一版只需提供这些)

```
assets/images/cards/major_00_fool.jpg
assets/images/cards/major_01_magician.jpg
assets/images/cards/major_02_high_priestess.jpg
assets/images/cards/major_03_empress.jpg
assets/images/cards/major_04_emperor.jpg
assets/images/cards/major_05_hierophant.jpg
assets/images/cards/major_06_lovers.jpg
assets/images/cards/major_07_chariot.jpg
assets/images/cards/major_08_strength.jpg
assets/images/cards/major_09_hermit.jpg
assets/images/cards/major_10_wheel_of_fortune.jpg
assets/images/cards/major_11_justice.jpg
assets/images/cards/major_12_hanged_man.jpg
assets/images/cards/major_13_death.jpg
assets/images/cards/major_14_temperance.jpg
assets/images/cards/major_15_devil.jpg
assets/images/cards/major_16_tower.jpg
assets/images/cards/major_17_star.jpg
assets/images/cards/major_18_moon.jpg
assets/images/cards/major_19_sun.jpg
assets/images/cards/major_20_judgement.jpg
assets/images/cards/major_21_world.jpg
```

逆位无需单独图片;代码会在展示时把牌面图像旋转 180°,牌名 / 关键词不旋转。

### 推荐图片规格

| 资源类型 | 推荐尺寸 | 最低尺寸 | 高清尺寸 | 比例 | 格式 | 单文件大小 |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| 大阿卡那牌面 | 768 × 1344 | 512 × 896 | 1024 × 1792 | 4 : 7 | `.jpg` / `.png` | 300 KB ~ 1.5 MB |
| 牌背 | 768 × 1344 | 512 × 896 | 1024 × 1792 | 4 : 7 | `.jpg` / `.png` | 同上 |
| 手机背景图 | 1080 × 1920 | 720 × 1280 | 1440 × 2560 | 9 : 16 | `.jpg` | ≤ 2 MB |
| 应用图标 | 512 × 512 | 192 × 192 | — | 1 : 1 | `.png` | ≤ 300 KB |

### 风格建议

```
色调:深紫 / 黑蓝 / 暗金 / 黑色
装饰:星星、月亮、星尘、魔法阵、细金线
构图:竖版 4:7,主体居中
边框:内嵌金色细线或神秘符号
氛围:神秘、优雅、安静、有仪式感
```

避开:

- 横版图片
- 过亮、过花、高饱和度
- 写实风 + 卡通风混搭
- 文件名包含中文 / 空格 / 特殊符号
- 单图超过 2 MB
- 牌面塞太多小字(小屏看不清)

---

## 打包 Android APK

> 依赖 Linux / macOS / WSL + Java 17 + Android SDK/NDK。Windows 原生不被 Buildozer 支持,请使用 WSL。

```bash
pip install buildozer cython
buildozer -v android debug
```

`buildozer.spec` 已配置好以下关键项:

```text
source.include_exts = py,png,jpg,jpeg,kv,json,ttf,otf,ttc
android.permissions = INTERNET
orientation = portrait
fullscreen = 0
```

所以只要把图片放进 `assets/images/**/`,执行 `buildozer android debug` 就会自动打包进 APK。

编译产物在 `bin/mystictarot-0.1.0-arm64-v8a-debug.apk`,用 USB 安装:

```bash
adb install -r bin/mystictarot-0.1.0-arm64-v8a-debug.apk
```

## 常见问题

| 问题 | 答案 |
| --- | --- |
| AI 解读太长显示不完整怎么办? | 结果页使用 `ScrollView + AutoWrapLabel(分段)`,长文本自动换行并撑高,可上下滑动查看完整内容。 |
| DeepSeek 输出了 Markdown 怎么办? | system prompt 已明确要求纯文本;前端会再用 `sanitize_ai_text` 清理,不会显示 `**`、`#`、`-` 等符号。 |
| 小屏手机卡牌太挤怎么办? | 项目根据窗口宽度自动切换横向 / 纵向布局,卡牌大小、字体、间距都会跟着变。 |
| 中文显示成方块 | 把任意中文 `.ttf` 放到 `assets/fonts/zh.ttf`,`main.py` 会自动注册。 |
| 翻牌后看不见牌面 | 检查 `assets/images/cards/` 下文件名是否与表格一致(大小写和下划线)。 |
| 点击 AI 解牌没反应 | 设置页点「测试连接」可以诊断 API Key、网络、模型名是否正确。 |
| 打包时 `openai` 相关包报错 | 先去掉 `buildozer.spec` 的 openai 依赖,再 `buildozer android clean` 重新打包。 |
| API Key 想清掉 | 设置页「清空 Key」,或直接删除 `user_data_dir/config.json`。 |

## 隐私声明

- API Key 仅写入本机 `user_data_dir/config.json`。
- 所有问题、抽牌结果、AI 解读默认只保存在本机的 `history.json`。
- 可在设置页关闭「保存占卜历史到本地」。
- 塔罗解读仅供反思;医疗、法律、投资、严重心理问题请咨询专业人士。
