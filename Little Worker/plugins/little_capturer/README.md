# LittleCapturer - 专业截图工具插件

## 📖 简介

LittleCapturer 是一个专业的截图工具插件，为 HSBC Little Worker 提供强大的截图功能，超越 Windows 系统自带的截图工具。

## ✨ 主要功能

- 🖱️ **自定义区域截图**: 鼠标拖拽选择任意截图区域
- 📌 **图片钉屏功能**: 将截图悬浮显示在屏幕上
- 🔍 **OCR文字识别**: 智能识别图片中的文字并支持复制
- ✏️ **图片编辑工具**: 内置画笔、标注等编辑功能，支持撤销/重做
- 💾 **多格式保存**: 支持 PNG、JPG、BMP 等多种图片格式
- ⌨️ **全局快捷键**: 默认 `Alt+Shift+A` 快速启动截图

## 🚀 启动方式

### 方式一：通过 HSBC Little Worker 启动

1. 启动 HSBC Little Worker 主程序
2. 在插件管理界面中启用 LittleCapturer 插件
3. 点击插件标签页查看使用说明
4. 使用快捷键 `Alt+Shift+A` 开始截图

### 方式二：独立启动

```bash
# 在项目根目录下运行
python plugins/little_capturer/LittleCapturer.py
```

## 📋 配置说明

插件配置文件位于 `config.json`，包含以下设置：

```json
{
  "plugin_info": {
    "name": "little_capturer",
    "display_name": "LittleCapturer",
    "description": "专业的截图工具插件",
    "version": "1.0.0",
    "author": "HSBC IT Support"
  },
  "available_config": {
    "enabled": true,
    "hotkey": "Alt+Shift+A",
    "auto_hide_window": true,
    "save_path": "./screenshots",
    "enable_ocr": true,
    "enable_pin": true,
    "enable_edit": true
  }
}
```

### 配置项说明

- `enabled`: 是否启用插件
- `hotkey`: 全局快捷键（默认：Alt+Shift+A）
- `auto_hide_window`: 截图时是否自动隐藏主窗口
- `save_path`: 截图保存路径
- `enable_ocr`: 是否启用OCR文字识别功能
- `enable_pin`: 是否启用图片钉屏功能
- `enable_edit`: 是否启用图片编辑功能

## 🎯 使用流程

1. **启动截图**: 按下快捷键 `Alt+Shift+A`
2. **选择区域**: 拖拽鼠标选择要截图的区域
3. **完成截图**: 释放鼠标完成区域选择
4. **后续操作**: 使用弹出的工具栏进行以下操作：
   - 📌 钉在屏幕上
   - 🔍 OCR文字识别
   - ✏️ 编辑图片
   - 💾 保存图片

## 🌍 国际化支持

插件支持中英文双语：

- 中文：`translations/zh_CN.json`
- 英文：`translations/en_US.json`

## 📁 目录结构

```
plugins/little_capturer/
├── __init__.py              # 插件主文件
├── config.json              # 插件配置文件
├── LittleCapturer.py        # 独立启动脚本
├── README.md                # 说明文档
├── translations/            # 国际化翻译文件
│   ├── zh_CN.json          # 中文翻译
│   └── en_US.json          # 英文翻译
└── utils/                   # 工具模块（待实现）
    ├── screenshot.py        # 截图功能
    ├── hotkey_manager.py    # 全局热键管理
    └── image_processor.py   # 图片处理
```

## 🔧 开发状态

当前版本为 UI 界面版本，主要功能模块的逻辑实现待后续开发：

- ✅ 插件基础框架
- ✅ UI 界面设计
- ✅ 配置管理
- ✅ 国际化支持
- ✅ 独立启动脚本
- ⏳ 截图功能实现
- ⏳ 全局热键管理
- ⏳ OCR文字识别
- ⏳ 图片编辑工具
- ⏳ 图片钉屏功能

## 📝 注意事项

1. 确保系统已安装 PySide6 依赖
2. 独立启动时需要在项目根目录下运行
3. 全局热键功能需要管理员权限（Windows）
4. OCR功能可能需要额外的依赖库

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件！

## 📄 许可证

本项目遵循 HSBC IT Support 内部许可协议。