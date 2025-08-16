# 🔌 HSBC Little Worker 插件开发指南

## 📋 目录

- [概述](#概述)
- [插件目录结构](#插件目录结构)
- [开发环境](#开发环境)
- [创建插件](#创建插件)
- [插件基类方法](#插件基类方法)
- [插件生命周期](#插件生命周期)
- [UI界面开发](#ui界面开发)
- [国际化支持](#国际化支持)
- [日志记录](#日志记录)
- [插件注册与加载](#插件注册与加载)
- [最佳实践](#最佳实践)
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
    
    def cleanup(self) -> None:
        """清理插件资源"""
        self.log_info("[插件] 🧹 清理完成")
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
    "enabled": true
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

def cleanup(self) -> None:
    """清理插件资源，应用程序退出时调用"""
    pass
```

### 常用方法
```python
# 配置管理（available_config 字段）
self.get_setting(key, default)     # 获取可配置项
self.get_decrypted_setting(key, default)  # 获取解密后的配置项（自动解密password开头的字段）
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

## 🔄 插件生命周期

插件在应用程序运行期间会经历以下生命周期阶段：

### 1. 发现阶段
插件管理器扫描 `plugins/` 目录，发现所有包含 `Plugin` 类的插件模块。

### 2. 加载阶段
- 读取插件的 `config.json` 配置文件
- 加载插件的翻译文件
- 实例化插件类

### 3. 初始化阶段
调用插件的 `initialize()` 方法：
```python
def initialize(self) -> bool:
    """初始化插件资源"""
    # 初始化数据库连接、网络连接等
    # 启动后台服务或定时器
    # 注册事件监听器
    self.log_info("[插件] 🚀 初始化完成")
    return True  # 返回 True 表示初始化成功
```

### 4. 运行阶段
- 插件界面通过 `create_widget()` 方法集成到主应用
- 插件响应用户交互和系统事件
- 插件可以动态更新配置和状态

### 5. 清理阶段（重要）
当应用程序退出时，插件管理器会调用每个插件的 `cleanup()` 方法：

```python
def cleanup(self) -> None:
    """清理插件资源"""
    try:
        # 停止后台服务和定时器
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer = None
        
        # 关闭网络连接
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            self.connection = None
        
        # 保存配置和状态
        self.save_settings()
        
        # 释放其他资源
        self.log_info("[插件] 🧹 资源清理完成")
        
    except Exception as e:
        self.log_error(f"[插件] ❌ 清理失败: {e}")
```

### ⚠️ 重要说明

**cleanup() 方法是必须实现的**，即使插件没有需要清理的资源，也应该提供一个空实现：

```python
def cleanup(self) -> None:
    """清理插件资源"""
    # 如果没有需要清理的资源，可以只记录日志
    self.log_info("[插件] 🧹 清理完成")
```

**为什么 cleanup() 很重要？**
- 🚫 **防止僵尸进程**：未正确清理的后台服务可能成为僵尸进程
- 💾 **数据安全**：确保重要数据在应用退出前保存
- 🔌 **资源释放**：释放网络连接、文件句柄等系统资源
- 🧹 **内存管理**：避免内存泄漏和资源占用

**常见需要清理的资源**：
- 定时器 (QTimer)
- 网络连接 (HTTP服务器、WebSocket等)
- 文件句柄
- 数据库连接
- 后台线程
- 临时文件

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

**更复杂的翻译文件示例**：

**zh_CN.json**:
```json
{
  "plugin.demo.name": "演示插件",
  "plugin.demo.description": "用于测试插件系统的演示插件",
  "plugin.demo.click_button": "点击我",
  "plugin.demo.reset_button": "重置计数器",
  "plugin.demo.count_display": "点击次数: {count}",
  "plugin.demo.status_message": "操作成功完成"
}
```

**en_US.json**:
```json
{
  "plugin.demo.name": "Demo Plugin",
  "plugin.demo.description": "A demo plugin for testing the plugin system",
  "plugin.demo.click_button": "Click Me",
  "plugin.demo.reset_button": "Reset Counter",
  "plugin.demo.count_display": "Click Count: {count}",
  "plugin.demo.status_message": "Operation completed successfully"
}
```

### 使用翻译
```python
# 在界面中使用
title = QLabel(self.tr("plugin.my_plugin.title"))
button = QPushButton(self.tr("plugin.my_plugin.button"))

# 带参数的翻译
count_label = QLabel(self.tr("plugin.demo.count_display", count=self.click_count))
message = self.tr("plugin.my_plugin.error", error="网络错误")

# 在状态消息中使用
self.show_status_message(self.tr("plugin.demo.status_message"))
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
    
    def cleanup(self) -> None:
        """清理插件资源"""
        self.log_info("[插件] 🧹 清理完成")
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
- `"keyboard"`: 键盘快捷键配置，在UI中显示为快捷键输入框, 支持多个快捷键配置 均以keyboard开头
- `password`: 密码类型配置，在UI中显示为密码输入框，并会根据配置自动加密存储

**完整配置文件示例**：
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
    "keyboard_1": "Ctrl+Shift+D"
  }
}
```

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

## 🔐 密码解密API使用

### 密码字段自动解密

对于以 `password` 开头的配置字段，插件系统提供了自动解密功能：

**配置文件示例**：
```json
{
  "plugin_info": {
    "name": "web_toolkit",
    "display_name": "Web工具包",
    "description": "提供Web相关功能的工具包",
    "version": "1.0.0",
    "author": "HSBC IT Support"
  },
  "available_config": {
    "enabled": true,
    "username_sso": "myuser",
    "password_sso": "Z0FBQUFBQm9vQm1Qcl8waUF0V2UyYzJ1T29kX1NMaG5HSlhXVXVSRU4tbUxIeEIwTE9La29VSGQ0Z0pqLXR1c1ZVOWFtbHV2OEpuVnZORkhyUXphUG5EV2p5Z2pRQjlQNUE9PQ=="
  }
}
```

### 在插件中使用解密API

```python
class Plugin(PluginBase):
    def initialize(self) -> bool:
        # 获取普通配置
        username = self.get_setting("username_sso", "")
        
        # 获取解密后的密码（自动解密password_开头的字段）
        password = self.get_decrypted_setting("password_sso", "")
        
        # 使用解密后的密码进行身份验证
        if self._authenticate(username, password):
            self.log_info("[插件] ✅ 身份验证成功")
            return True
        else:
            self.log_error("[插件] ❌ 身份验证失败")
            return False
    
    def _authenticate(self, username: str, password: str) -> bool:
        """使用明文密码进行身份验证"""
        try:
            # 这里password已经是解密后的明文密码
            # 可以直接用于API调用、数据库连接等
            response = requests.post(
                "https://api.example.com/auth",
                json={"username": username, "password": password}
            )
            return response.status_code == 200
        except Exception as e:
            self.log_error(f"[插件] ❌ 认证请求失败: {e}")
            return False
```

### API方法说明

- **`get_decrypted_setting(key, default)`**: 获取解密后的配置项
  - 对于 `password` 开头的字段，自动解密后返回明文
  - 对于非密码字段，行为与 `get_setting()` 相同
  - 解密失败时返回原始加密值，并记录错误日志

- **安全特性**:
  - 密码在配置文件中以加密形式存储
  - 只有在插件运行时才解密到内存中
  - 解密过程有完整的错误处理和日志记录

### 注意事项

⚠️ **重要提醒**：
- 解密后的密码仅存在于内存中，不要将其写入日志或文件
- 确保在插件cleanup()方法中清理包含密码的变量
- 密码字段必须以 `password` 开头才能被自动识别和解密

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

- **插件结构**: 继承PluginBase，实现initialize()、create_widget()和cleanup()方法
- **插件生命周期**: 理解插件的发现、加载、初始化、运行和清理阶段
- **资源管理**: 正确实现cleanup()方法，防止僵尸进程和资源泄漏
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