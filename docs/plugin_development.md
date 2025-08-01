# 🔌 HSBC Little Worker 插件开发指南

## 📋 目录

- [概述](#概述)
- [插件系统架构](#插件系统架构)
- [开发环境准备](#开发环境准备)
- [创建第一个插件](#创建第一个插件)
- [插件基类详解](#插件基类详解)
- [插件生命周期](#插件生命周期)
- [UI界面开发](#ui界面开发)
- [配置管理](#配置管理)
- [国际化支持](#国际化支持)
- [日志记录](#日志记录)
- [插件注册与加载](#插件注册与加载)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [示例代码](#示例代码)

## 📖 概述

HSBC Little Worker 采用插件化架构设计，支持本地化配置和翻译的独立插件开发。

### 核心特性
- 🔄 **动态加载**：运行时加载和卸载插件
- 🎨 **UI集成**：自定义界面组件
- ⚙️ **本地化配置**：每个插件独立的配置文件
- 🌍 **本地化翻译**：插件专属翻译文件
- 📝 **日志系统**：统一的日志记录

## 🏗️ 插件目录结构

```
plugins/
└── your_plugin/
    ├── __init__.py              # 插件主文件
    ├── config.json              # 插件配置
    └── translations/             # 插件翻译
        ├── zh_CN.json           # 中文翻译
        └── en_US.json           # 英文翻译
```

## 🛠️ 开发环境

### 必要依赖
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from core.plugin_base import PluginBase
```

## 🚀 创建插件

### 1. 创建插件文件

**`plugins/my_plugin/__init__.py`**
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from core.plugin_base import PluginBase

class Plugin(PluginBase):
    def initialize(self) -> bool:
        self.log_info("[插件] 🚀 初始化完成")
        return True
    
    def create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 使用插件本地翻译
        title = QLabel(self.tr("plugin.my_plugin.title"))
        button = QPushButton(self.tr("plugin.my_plugin.button"))
        
        layout.addWidget(title)
        layout.addWidget(button)
        return widget
```

### 2. 创建配置文件

**`plugins/my_plugin/config.json`**
```json
{
  "plugin_info": {
    "name": "my_plugin",
    "display_name": "我的插件",
    "description": "一个示例插件",
    "version": "1.0.0",
    "author": "Your Name"
  },
  "available_config": {
    "enabled": true,
    "auto_save": true
  }
}
```

### 3. 创建翻译文件

**`plugins/my_plugin/translations/zh_CN.json`**
```json
{
  "plugin.my_plugin.title": "我的插件",
  "plugin.my_plugin.button": "点击按钮"
}
```

**`plugins/my_plugin/translations/en_US.json`**
```json
{
  "plugin.my_plugin.title": "My Plugin",
  "plugin.my_plugin.button": "Click Button"
}
```

## 🧩 插件基类方法

### 必须实现的方法
```python
def initialize(self) -> bool:
    """初始化插件，返回是否成功"""
    pass

def create_widget(self) -> QWidget:
    """创建插件界面组件"""
    pass
```

### 常用方法
```python
# 配置管理（available_config 字段）
self.get_setting(key, default)     # 获取可配置项
self.set_setting(key, value)       # 设置可配置项
self.get_plugin_info(key)          # 获取插件信息（只读）

# 本地化翻译
self.tr(key, **kwargs)             # 获取翻译文本
self.set_language(lang_code)       # 设置语言

# 日志记录
self.log_info(message)             # 信息日志
self.log_warning(message)          # 警告日志
self.log_error(message)            # 错误日志
self.log_debug(message)            # 调试日志

# UI交互
self.show_status_message(msg)      # 显示状态消息
```

## 🎨 UI界面开发

### 基础界面示例
```python
def create_widget(self) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # 使用翻译文本
    title = QLabel(self.tr("plugin.my_plugin.title"))
    button = QPushButton(self.tr("plugin.my_plugin.button"))
    button.clicked.connect(self._on_button_clicked)
    
    layout.addWidget(title)
    layout.addWidget(button)
    return widget

def _on_button_clicked(self):
    self.log_info("[插件] 🔘 按钮被点击")
    self.show_status_message(self.tr("plugin.my_plugin.success"))
```

## ⚙️ 配置管理

### 本地化配置文件

每个插件拥有独立的配置文件 `config.json`：

```json
{
  "plugin_info": {
    "name": "my_plugin",
    "display_name": "我的插件",
    "description": "插件描述信息",
    "version": "1.0.0",
    "author": "作者名称"
  },
  "available_config": {
    "enabled": true,
    "auto_save": true,
    "theme_color": "#007bff"
  }
}
```

### 配置操作

```python
class Plugin(PluginBase):
    def __init__(self, app=None):
        super().__init__(app)
        
        # 读取插件配置（从 available_config 字段）
        self.auto_save = self.get_setting('auto_save', True)
        self.theme_color = self.get_setting('theme_color', '#007bff')
        
        # 插件信息（从 plugin_info 字段，只读）
        self.plugin_name = self.get_plugin_info('name')
        self.plugin_version = self.get_plugin_info('version')
    
    def save_settings(self):
        """保存配置到本地文件"""
        # 只能修改 available_config 中的配置项
        self.set_setting('auto_save', self.auto_save)
        self.set_setting('theme_color', self.theme_color)
        self.log_info("[配置] 💾 配置已保存")
    
    def get_plugin_info(self, key: str):
        """获取插件信息（只读）"""
        # 从 plugin_info 字段获取信息
        return self.config.get('plugin_info', {}).get(key)
```

### 🔄 插件配置重构方案

**当前架构问题**：
- 所有插件配置集中在全局 `config/app_config.json` 中
- 翻译文件都在 `resources/translations/` 全局目录
- 插件缺乏独立性，难以独立分发和维护

**重构目标**：
- 🔧 **插件配置本地化**：每个插件目录包含自己的 `config.json`
- 🌍 **翻译文件本地化**：每个插件包含 `translations/` 目录
- 📦 **插件独立性**：插件可独立开发、测试、分发

**新插件目录结构**：
```
plugins/
├── demo_plugin/
│   ├── __init__.py              # 插件主文件
│   ├── config.json              # 插件配置
│   ├── translations/             # 插件翻译
│   │   ├── zh_CN.json
│   │   └── en_US.json
│   └── resources/               # 插件资源
└── my_plugin/
    ├── __init__.py
    ├── config.json
    └── translations/
```

**插件配置文件示例** (`plugins/{plugin_name}/config.json`)：
```json
{
  "plugin_info": {
    "name": "demo_plugin",
    "display_name": "演示插件",
    "description": "用于测试插件系统的演示插件",
    "version": "1.0.0",
    "author": "HSBC IT Support"
  },
  "available_config": {
    "enabled": true,
    "click_count": 0,
    "auto_save": true,
    "theme_color": "#007bff",
    "hotkey": "Ctrl+Shift+D"
  }
}
```

**插件翻译文件示例** (`plugins/{plugin_name}/translations/zh_CN.json`)：
```json
{
  "plugin.demo.name": "演示插件",
  "plugin.demo.description": "用于测试插件系统的演示插件",
  "plugin.demo.click_button": "点击我",
  "plugin.demo.reset_button": "重置计数器"
}
```

**重构后的插件基类使用**：
```python
class Plugin(PluginBase):
    def __init__(self, app=None):
        super().__init__(app)
        # 插件会自动加载自己目录下的配置和翻译文件
        
        # 读取插件配置
        self.click_count = self.get_setting('click_count', 0)
        self.auto_save = self.get_setting('auto_save', True)
        
    def initialize(self) -> bool:
        """初始化插件"""
        self.log_info("[演示插件] 🚀 插件初始化完成")
        return True
        
    def create_widget(self) -> QWidget:
        """创建插件界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 使用插件专用翻译方法
        title = QLabel(self.tr("plugin.demo.name"))
        button = QPushButton(self.tr("plugin.demo.click_button"))
        
        layout.addWidget(title)
        layout.addWidget(button)
        return widget
```

> 📋 **详细重构方案**：参考 `docs/Plugin-Config-Refactor.md` 文档

## 🌍 国际化支持

### 翻译文件
目前插件系统必须且仅仅只支持中文和英文两种语言，通过 `translations/` 目录下的 JSON 文件进行配置。不符合规则的插件将无法使用。
创建 `translations/` 目录：
```
my_plugin/
├── translations/
│   ├── zh_CN.json    # 中文
│   └── en_US.json    # 英文
└── __init__.py
```

**zh_CN.json**:
```json
{
    "plugin.my_plugin.title": "我的插件",
    "plugin.my_plugin.button": "开始",
    "plugin.my_plugin.success": "操作成功！"
}
```

**en_US.json**:
```json
{
    "plugin.my_plugin.title": "My Plugin",
    "plugin.my_plugin.button": "Start",
    "plugin.my_plugin.success": "Success!"
}
```

### 使用翻译
```python
# 在界面中使用
title = QLabel(self.tr("plugin.my_plugin.title"))
button = QPushButton(self.tr("plugin.my_plugin.button"))

# 带参数的翻译
message = self.tr("plugin.my_plugin.error", error="网络错误")
```

## 📝 日志记录

### 日志级别使用

```python
class Plugin(SimplePluginBase):
    def some_operation(self):
        """执行某个操作"""
        try:
            self.log_info("🚀 开始执行操作")
            
            # 执行操作前的调试信息
            self.log_debug("🔍 检查前置条件")
            
            if not self.validate_preconditions():
                self.log_warning("⚠️ 前置条件不满足，使用默认配置")
            
            # 执行主要逻辑
            result = self.perform_main_logic()
            
            self.log_info(f"✅ 操作完成，结果: {result}")
            
        except Exception as e:
            import traceback
            self.log_error(f"❌ 操作失败: {e} - {traceback.format_exc()}")
    
    def validate_preconditions(self) -> bool:
        """验证前置条件"""
        # 验证逻辑
        return True
    
    def perform_main_logic(self):
        """执行主要逻辑"""
        # 主要逻辑
        return "success"
```

### 日志格式规范

```python
# 推荐的日志格式
self.log_info("🚀 [操作名称] 操作描述")     # 开始操作
self.log_info("✅ [操作名称] 操作成功")     # 操作成功
self.log_warning("⚠️ [操作名称] 警告信息") # 警告信息
self.log_error("❌ [操作名称] 错误信息")   # 错误信息
self.log_debug("🔍 [操作名称] 调试信息")   # 调试信息

# 使用表情符号增强可读性
# 🚀 开始/启动    ✅ 成功/完成    ❌ 错误/失败
# ⚠️ 警告        🔍 调试/检查    💾 保存
# 🔄 重置/刷新    📝 记录/写入    🔌 插件相关
```

## 🔧 插件注册与加载

### 插件发现机制

插件管理器会自动扫描 `plugins/` 目录：

```python
# 插件目录结构
plugins/
├── demo_plugin/
│   └── __init__.py      # 包含 Plugin 类
├── my_plugin/
│   └── __init__.py      # 包含 Plugin 类
└── another_plugin/
    ├── __init__.py      # 包含 Plugin 类
    ├── utils.py         # 辅助模块
    └── resources/       # 资源文件
```

### 插件类要求

每个插件的 `__init__.py` 必须包含名为 `Plugin` 的类：

```python
# plugins/my_plugin/__init__.py

class Plugin(PluginBase):  # 必须继承自 PluginBase 或其子类
    """插件主类，名称必须是 Plugin"""
    
    # 插件元信息（用于自动生成 config.json）
    NAME = "my_plugin"
    DISPLAY_NAME = "我的插件"
    DESCRIPTION = "插件描述"
    VERSION = "1.0.0"
    AUTHOR = "作者名称"
    
    def initialize(self) -> bool:
        """初始化插件"""
        self.log_info("[插件] 🚀 初始化完成")
        return True
    
    def create_widget(self) -> QWidget:
        """创建插件界面组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 使用插件本地翻译
        title = QLabel(self.tr("plugin.my_plugin.title"))
        button = QPushButton(self.tr("plugin.my_plugin.button"))
        
        layout.addWidget(title)
        layout.addWidget(button)
        return widget
```

### 插件配置文件规范

#### 📋 配置文件要求

`config.json` 文档**必须存在**，且包含以下字段，否则插件将无法使用：

```json
{
  "plugin_info": {
    "name": "demo_plugin",
    "display_name": "Demo Plugin",
    "description": "A demo plugin for testing the plugin system",
    "version": "1.0.0",
    "author": "HSBC IT Support"
  },
  "available_config": {
    "enabled": true,
    "loaded": true,
  }
}
```

#### 🔧 配置字段说明

**`plugin_info` 字段（只读信息）**：
- `name`: 插件唯一标识符
- `display_name`: 插件显示名称
- `description`: 插件描述信息
- `version`: 插件版本号
- `author`: 插件作者

> ⚠️ **注意**：`plugin_info` 字段不支持运行时修改，仅用于插件信息展示。

**`available_config` 字段（可配置项）**：
- `"enabled"`: **必须字段**，布尔值，控制插件是否启用
- `bool`: 布尔类型配置，在UI中显示为开关
- `string`: 字符串类型配置，在UI中显示为文本输入框（最长100字符）
- `int`: 整数类型配置，在UI中显示为数字输入框
- `list`: 列表类型配置，在UI中显示为下拉选择框
  - 列表最后一个值为默认选项
  - 修改后，新选项会移动到列表末尾
- `"keyboard"`: 键盘快捷键配置，在UI中显示为快捷键输入框

#### 🔄 自动生成机制

如果插件目录下不存在 `config.json`，系统会尝试从插件类的元信息自动生成：

```python
class Plugin(PluginBase):
    # 插件元信息
    NAME = "my_plugin"
    DISPLAY_NAME = "我的插件"
    DESCRIPTION = "插件描述"
    VERSION = "1.0.0"
    AUTHOR = "作者名称"
```

系统读取元信息后，会自动在插件目录下生成对应的 `config.json` 文件。

## 💡 最佳实践

### 错误处理
```python
def _handle_operation(self):
    try:
        result = self._do_something()
        self.log_info("[插件] ✅ 操作成功")
        return result
    except Exception as e:
        self.log_error(f"[插件] ❌ 操作失败: {e} - {traceback.format_exc()}")
        self.show_status_message(self.tr("plugin.my_plugin.error"))
        return None
```

### 日志规范
```python
# 使用标签和emoji
self.log_info("[插件] 🚀 开始初始化")
self.log_warning("[插件] ⚠️ 配置文件不存在，使用默认配置")
self.log_error(f"[插件] ❌ 连接失败: {e} - {traceback.format_exc()}")
```

## 📝 总结

本指南介绍了HSBC Little Worker插件开发的核心要点：

- **插件结构**: 继承PluginBase，实现initialize()和create_widget()方法
- **配置管理**: 使用规范的config.json格式，区分plugin_info（只读）和available_config（可配置）
- **本地化支持**: 每个插件独立的translations翻译目录
- **最佳实践**: 使用标签化日志、规范错误处理、支持多语言

开始开发你的第一个插件吧！ 🚀

## 📚 示例代码

完整的插件示例可以参考 `plugins/demo_plugin/` 目录。

---

## 🎯 总结

通过本指南，你应该能够：

1. ✅ 理解 HSBC Little Worker 的插件系统架构
2. ✅ 创建和开发自己的插件
3. ✅ 实现插件的 UI 界面和功能逻辑
4. ✅ 使用配置管理和国际化功能
5. ✅ 遵循最佳实践和编码规范
6. ✅ 解决常见的开发问题

如果在开发过程中遇到问题，请参考：
- 📚 示例插件代码 (`plugins/demo_plugin/`)
- 📋 插件配置文件规范（本文档「插件配置文件规范」章节）
- 📝 应用程序日志文件
- 🔍 插件管理器的错误信息
- 💬 开发团队的技术支持

祝你插件开发愉快！🚀