# 灵境塔罗 · Mystic Tarot

一款基于 **Python + Kivy** 的跨平台塔罗占卜应用，支持 **桌面（Windows/macOS/Linux）** 和 **Android**。

不依赖任何数据库，所有数据以 JSON 保存在本地；AI 解牌通过你自己配置的 **DeepSeek API** 完成。

---

## ✨ 特性

- 🎴 **22 张大阿卡那**完整牌义，正逆位独立
- 🔄 逆位通过把牌面图片旋转 180° 实现，**不需要单独的逆位图片**
- 🎯 **5 种牌阵**：单牌、三牌阵、爱情、事业、凯尔特十字
- ✨ **神秘翻牌动画**：缩窄 → 切换牌面 → 回弹展开 + 金色光晕
- 🎨 **深色神秘主题**，响应式布局，宽屏横排、小屏自动纵排
- 🤖 **DeepSeek AI 解牌**，system prompt 明确禁止 Markdown，前端二次清理
- 📜 **本地历史记录**，可单条删除 / 一键清空
- 🔒 **API Key 安全**：仅保存在本机，默认脱敏显示 `sk-****xxxx`
- 🌐 **无网络兜底**：未配置 API Key 时使用本地牌义

---

## 📦 快速开始

### 方式一：桌面运行（Windows/macOS/Linux）

#### 1. 安装 Python

- **Windows**：前往 [python.org](https://www.python.org/downloads/) 下载 Python 3.8+ 安装包
  - 安装时勾选 **"Add Python to PATH"**
- **macOS**：使用 Homebrew 安装
  ```bash
  brew install python@3.10
  ```
- **Linux**：
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv
  ```

#### 2. 下载项目

**方式 A：使用 Git（推荐）**
```bash
git clone https://github.com/elegy2/tarot.git
cd tarot
```

**方式 B：直接下载 ZIP**
1. 点击 GitHub 页面右上角绿色 **Code** 按钮
2. 选择 **Download ZIP**
3. 解压到任意目录，在终端进入该目录

#### 3. 创建虚拟环境（推荐）

**Windows PowerShell：**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux：**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. 安装依赖

```bash
pip install -r requirements.txt
```

> **常见问题**：如果安装 Kivy 时报错，请参考 [Kivy 官方安装文档](https://kivy.org/doc/stable/gettingstarted/installation.html)

#### 5. 运行应用

```bash
python main.py
```

首次启动会在系统用户目录下生成配置文件：

- **Windows**: `%APPDATA%\mystictarot\config.json`
- **macOS**: `~/Library/Application Support/mystictarot/config.json`
- **Linux**: `~/.local/share/mystictarot/config.json`

---

### 方式二：打包 Android APK

> **前置要求**：Linux / macOS / WSL + Java 17 + Android SDK/NDK  
> Windows 原生不被 Buildozer 支持，请使用 WSL（Windows Subsystem for Linux）

#### 1. 安装 Buildozer

```bash
pip install buildozer cython
```

#### 2. 打包 APK

```bash
buildozer -v android debug
```

编译产物在 `bin/mystictarot-0.1.0-arm64-v8a-debug.apk`

#### 3. 安装到手机

```bash
adb install -r bin/mystictarot-0.1.0-arm64-v8a-debug.apk
```

---

## 🔑 配置 DeepSeek API Key

### 获取 API Key

1. 前往 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册并登录
3. 进入 **API Keys** 页面创建新 Key
4. 复制 `sk-` 开头的 Key

### 配置方式（二选一）

#### 方式 A：环境变量（桌面调试推荐，不会落盘）

**Windows PowerShell：**
```powershell
$env:DEEPSEEK_API_KEY = "sk-你的key"
python main.py
```

**macOS/Linux：**
```bash
export DEEPSEEK_API_KEY="sk-你的key"
python main.py
```

#### 方式 B：应用内设置（Android 推荐）

1. 启动应用
2. 点击主页 **"API 设置"**
3. 粘贴 API Key 并保存
4. 点击 **"测试连接"** 验证是否配置成功

> **安全提示**：API Key 仅保存在本机，代码中绝不硬编码任何 Key，日志中只会显示脱敏后的 `sk-****xxxx`

---

## 📁 目录结构

```
tarot/
├── main.py                           # 应用入口
├── requirements.txt                  # Python 依赖
├── buildozer.spec                    # Android 打包配置
├── README.md                         # 本文档
├── app/
│   ├── data/                         # 塔罗牌数据 + 牌阵定义
│   │   ├── tarot_cards.py            # 78 张塔罗牌完整数据
│   │   └── spreads.py                # 5 种牌阵配置
│   ├── services/                     # 核心服务
│   │   ├── config_manager.py         # 配置管理（API Key、历史记录）
│   │   ├── deepseek_client.py        # DeepSeek API 封装
│   │   └── tarot_engine.py           # 抽牌引擎
│   ├── widgets/                      # UI 组件
│   │   ├── mystic_background.py      # 神秘星空背景
│   │   ├── mystic_button.py          # 圆角金边按钮
│   │   ├── mystic_panel.py           # 暗紫圆角面板
│   │   ├── tarot_card_widget.py      # 塔罗卡片 + 翻牌动画
│   │   └── auto_wrap_label.py        # 自动换行标签
│   ├── screens/                      # 应用页面
│   │   ├── home_screen.py            # 首页
│   │   ├── spread_select_screen.py   # 牌阵选择
│   │   ├── question_screen.py        # 问题输入
│   │   ├── draw_screen.py            # 抽牌翻牌
│   │   ├── result_screen.py          # 解读结果
│   │   ├── settings_screen.py        # API 设置
│   │   ├── history_screen.py         # 历史记录
│   │   └── about_screen.py           # 关于应用
│   └── utils/                        # 工具函数
│       ├── theme.py                  # 颜色 / 字号常量
│       ├── responsive.py             # 响应式布局工具
│       ├── text_formatter.py         # AI 文本清理
│       └── asset_loader.py           # 跨平台资源加载
└── assets/                           # 资源文件
    ├── fonts/                        # 字体（可选）
    └── images/
        ├── cards/                    # 塔罗牌图片（22 张大阿卡那）
        ├── backgrounds/              # 背景图（可选）
        └── icons/                    # 应用图标（可选）
```

---

## 🎨 资源文件说明

### 必需文件

项目已包含 **22 张大阿卡那牌面图片**：

```
assets/images/cards/major_00_fool.jpg
assets/images/cards/major_01_magician.jpg
...
assets/images/cards/major_21_world.jpg
```

### 可选文件

| 文件 | 路径 | 说明 |
| --- | --- | --- |
| 牌背 | `assets/images/cards/card_back.jpg` | 所有未翻开的牌都用这张，缺失时自动绘制星形图案 |
| 中文字体 | `assets/fonts/zh.ttf` | 确保中文显示正常，缺失时使用系统字体 |
| 应用图标 | `assets/images/icons/app_icon.png` | 512×512 PNG，缺失时使用默认图标 |

### 图片规格建议

| 资源类型 | 推荐尺寸 | 比例 | 格式 | 单文件大小 |
| --- | ---: | ---: | --- | ---: |
| 塔罗牌面 | 768 × 1344 | 4 : 7 | `.jpg` / `.png` | 300 KB ~ 1.5 MB |
| 牌背 | 768 × 1344 | 4 : 7 | `.jpg` / `.png` | 同上 |
| 应用图标 | 512 × 512 | 1 : 1 | `.png` | ≤ 300 KB |

---

## ❓ 常见问题

### 安装相关

**Q: Windows 上运行 `python main.py` 提示找不到 python？**  
A: 安装 Python 时没有勾选 "Add Python to PATH"。重新安装 Python 并勾选该选项，或手动添加到系统环境变量。

**Q: `pip install -r requirements.txt` 报错？**  
A: 
1. 确保 Python 版本 ≥ 3.8：`python --version`
2. 升级 pip：`pip install --upgrade pip`
3. 如果是 Kivy 安装失败，参考 [Kivy 官方文档](https://kivy.org/doc/stable/gettingstarted/installation.html)

**Q: macOS 上提示 "command not found: python"？**  
A: macOS 默认使用 `python3`，将命令中的 `python` 改为 `python3`，`pip` 改为 `pip3`。

### 使用相关

**Q: 中文显示成方块？**  
A: 将任意中文 `.ttf` 字体文件放到 `assets/fonts/zh.ttf`，应用会自动注册。推荐使用微软雅黑或思源黑体。

**Q: 翻牌后看不见牌面图片？**  
A: 
1. 检查 `assets/images/cards/` 下文件名是否正确（大小写敏感）
2. 确认图片格式为 `.jpg` 或 `.png`
3. 查看控制台是否有图片加载错误提示

**Q: 点击 "开始 AI 解牌" 没反应？**  
A: 
1. 检查是否配置了 API Key
2. 设置页点 "测试连接" 诊断网络和 API Key 是否正确
3. 查看控制台错误信息

**Q: AI 解读显示不完整？**  
A: 结果页使用滚动视图，长文本可以上下滑动查看完整内容。

**Q: DeepSeek 输出了 Markdown 格式？**  
A: 应用已内置文本清理功能，会自动移除 `**`、`#`、`-` 等 Markdown 符号。

**Q: 如何清空 API Key？**  
A: 设置页点击 "清空 Key"，或直接删除配置文件（见上方配置文件路径）。

### Android 打包相关

**Q: Windows 上能打包 Android APK 吗？**  
A: 需要使用 WSL（Windows Subsystem for Linux）。纯 Windows 环境不支持 Buildozer。

**Q: 打包时提示 Java 版本不对？**  
A: Buildozer 需要 Java 17。安装方法：
```bash
# Ubuntu/Debian
sudo apt install openjdk-17-jdk

# macOS
brew install openjdk@17
```

**Q: 打包后 APK 安装失败？**  
A: 
1. 确保手机开启了 "允许安装未知来源应用"
2. 使用 `adb install -r` 强制覆盖安装
3. 检查手机 Android 版本是否 ≥ 5.0

---

## 🔒 隐私声明

- ✅ API Key 仅写入本机配置文件，不会上传到任何服务器
- ✅ 所有问题、抽牌结果、AI 解读默认只保存在本机
- ✅ 可在设置页关闭 "保存占卜历史到本地"
- ⚠️ 塔罗解读仅供反思参考，重要决定请结合现实情况理性判断
- ⚠️ 医疗、法律、投资、严重心理问题请咨询专业人士

---

## 📄 开源协议

MIT License

---

## 🙏 致谢

- [Kivy](https://kivy.org/) - 跨平台 Python UI 框架
- [DeepSeek](https://www.deepseek.com/) - AI 解读服务
- 塔罗牌图片来源：[待补充]

---

## 📮 反馈与贡献

- 🐛 发现 Bug？请提交 [Issue](https://github.com/elegy2/tarot/issues)
- 💡 有新想法？欢迎提交 [Pull Request](https://github.com/elegy2/tarot/pulls)
- 📧 联系作者：[待补充]

---

**祝你占卜愉快！✨**
