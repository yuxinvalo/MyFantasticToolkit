# LittleCapturer
专业的截图工具插件，超越Windows系统自带截图功能，提供更多的截图选项和自定义功能。

## Plugin说明
Plugin应当有两种启动方式，可以通过HSBC LittleWorker的插件管理界面来启动，也可以直接通过plugin入口脚本（`LittleCapturer.py`）单独启动程序。

### little capturer config
```json
{  
   "plugin_info": {
    "name": "little_capturer",
    "display_name": "LittleCapturer",
    "version": "1.0.0",
    "author": "HSBC IT SUPPORT",
    "description": "专业的截图工具插件，超越Windows系统自带截图功能，提供更多的截图选项和自定义功能。"
   },
   "available_config": {
      "enabled": true,
      "hotkey": "Alt+Shift+A",
      "auto_hide_window": true,
      "save_path": "./screenshots",
      "image_format": ["PNG", "JPG", "BMP", "PNG"],
      "enable_ocr": true,
      "enable_pin": true,
      "enable_edit": true
   }
}
```

### Plugin启动方式
1. 通过HSBC LittleWorker的插件管理界面注册
2. 读取插件的配置，并启动全局的Key绑定，默认是`ALT+SHIFT+A`
3. 如果用户点击使用该插件，HSBC LittleWorker将会显示一个LittleCapturer插件tab窗口，窗口内容只包含使用文字说明。 
4. 截图完成后，图片后续处理的widget应当在一个新的QWidget中，和主程序解耦。

### plugin入口脚本启动
1. 直接运行`LittleCapturer.py`脚本
2. 脚本会自动读取`config.json`配置文件，包括插件的配置和全局的Key绑定
3. 脚本会自动启动全局的Key绑定，默认是`ALT+SHIFT+A`
4. 脚本会自动显示一个LittleCapturer插件tab窗口，窗口内容只包含使用文字说明。
5. 截图完成后，图片后续处理的widget应当在一个新的QWidget中，和主程序解耦。

## 功能介绍
🎯 快捷键触发（默认：ALT+SHIFT+A，可配置）截图，在截图时自动隐藏HSBC LittleWorker主窗口以及LittleCapturer插件窗口，截图完成后自动显示主窗口。
🖱️ 鼠标拖拽自定义截图区域选择
🛠️ 截图后弹出编辑工具栏，包含：  
   - 📌 图片钉在屏幕上（悬浮显示）
   - 🔍 OCR文字识别和复制功能
   - ✏️ 画笔涂改工具（支持撤销/重做）
   - 💾 图片保存和导出功能

## 🚀 开发流程

### 📁 1. 创建插件目录结构

按照HSBC Little Worker插件开发规范，创建以下目录结构：

```
plugins/
└── little_capturer/
    ├── __init__.py              # 插件主文件
    ├── config.json              # 插件配置文件
    ├── translations/             # 国际化翻译文件
    │   ├── zh_CN.json           # 中文翻译
    │   └── en_US.json           # 英文翻译
    ├── capture_window.py        # 截图窗口类
    ├── edit_toolbar.py          # 编辑工具栏类
    ├── ocr_handler.py           # OCR处理类
    └── utils/                   # 工具模块
        ├── screenshot.py        # 截图功能
        ├── hotkey_manager.py    # 全局热键管理
        └── image_processor.py   # 图片处理
```

### ⚙️ 2. 配置文件设计

**`plugins/little_capturer/config.json`**
```json
{
  "plugin_info": {
    "name": "little_capturer",
    "display_name": "LittleCapturer",
    "description": "Little screenshot tool. Capture screen with ease.",
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

