# HSBC Little Worker 插件化项目结构

## 📁 项目目录结构

```
HSBCLittleWorker/
├── main.py                    # 主程序入口
├── pyproject.toml             # uv项目配置文件
├── requirements.txt           # 依赖管理
├── README.md                  # 项目说明
├── config/                    # 配置文件目录
│   ├── __init__.py
│   ├── settings.py            # 全局配置
│   └── plugin_config.json     # 插件配置
├── core/                      # 核心框架
│   ├── __init__.py
│   ├── application.py         # 主应用程序类
│   ├── plugin_manager.py      # 插件管理器
│   ├── base_plugin.py         # 插件基类
│   ├── event_system.py        # 事件系统
│   └── ui/                    # 核心UI组件
│       ├── __init__.py
│       ├── main_window.py     # 主窗口
│       ├── plugin_dock.py     # 插件停靠窗口
│       └── styles/            # 样式文件
│           ├── dark_theme.qss
│           └── light_theme.qss
├── plugins/                   # 插件目录
│   ├── __init__.py
│   ├── capturer/              # 截图工具插件
│   │   ├── __init__.py
│   │   ├── plugin.py          # 插件主文件
│   │   ├── capture_widget.py  # 截图界面
│   │   ├── editor_widget.py   # 图片编辑器
│   │   ├── floating_widget.py # 悬浮窗口
│   │   ├── ocr_engine.py      # OCR引擎
│   │   └── resources/         # 资源文件
│   │       ├── icons/
│   │       └── templates/
│   └── worknote/              # 工作日志插件
│       ├── __init__.py
│       ├── plugin.py          # 插件主文件
│       ├── editor_widget.py   # Markdown编辑器
│       ├── preview_widget.py  # 预览窗口
│       ├── syntax_highlighter.py # 语法高亮
│       ├── template_manager.py    # 模板管理
│       ├── export_manager.py      # 导出功能
│       └── resources/         # 资源文件
│           ├── templates/     # 日志模板
│           └── styles/        # 编辑器样式
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── logger.py              # 日志工具
│   ├── file_utils.py          # 文件操作
│   ├── image_utils.py         # 图像处理
│   └── hotkey_manager.py      # 快捷键管理
├── resources/                 # 全局资源
│   ├── icons/                 # 图标文件
│   ├── fonts/                 # 字体文件
│   └── translations/          # 国际化文件
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_core/
│   ├── test_plugins/
│   └── test_utils/
└── docs/                      # 文档
    ├── api.md
    ├── plugin_development.md
    └── user_guide.md
```

## 🏗️ 核心架构设计

### 1. 主应用程序 (main.py)
```python
from core.application import LittleWorkerApp

if __name__ == "__main__":
    app = LittleWorkerApp()
    app.run()
```

### 2. 插件基类 (core/base_plugin.py)
```python
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget

class BasePlugin(ABC):
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.name = ""
        self.version = "1.0.0"
        self.description = ""
        self.enabled = True
        
    @abstractmethod
    def initialize(self):
        """插件初始化"""
        pass
        
    @abstractmethod
    def create_widget(self) -> QWidget:
        """创建插件主界面"""
        pass
        
    @abstractmethod
    def get_menu_actions(self):
        """获取菜单动作"""
        pass
        
    def cleanup(self):
        """插件清理"""
        pass
```

### 3. 插件管理器 (core/plugin_manager.py)
```python
import importlib
import os
from typing import Dict, List
from .base_plugin import BasePlugin

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dir = "plugins"
        
    def discover_plugins(self):
        """发现并加载插件"""
        for item in os.listdir(self.plugin_dir):
            if os.path.isdir(os.path.join(self.plugin_dir, item)):
                self.load_plugin(item)
                
    def load_plugin(self, plugin_name: str):
        """加载单个插件"""
        try:
            module = importlib.import_module(f"plugins.{plugin_name}.plugin")
            plugin_class = getattr(module, f"{plugin_name.title()}Plugin")
            plugin = plugin_class(self)
            plugin.initialize()
            self.plugins[plugin_name] = plugin
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            
    def get_plugin(self, name: str) -> BasePlugin:
        return self.plugins.get(name)
        
    def get_all_plugins(self) -> List[BasePlugin]:
        return list(self.plugins.values())
```

## 🔌 插件实现示例

### 截图工具插件 (plugins/capturer/plugin.py)
```python
from core.base_plugin import BasePlugin
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from .capture_widget import CaptureWidget

class CapturerPlugin(BasePlugin):
    def __init__(self, plugin_manager):
        super().__init__(plugin_manager)
        self.name = "截图工具"
        self.description = "自定义截图工具，支持OCR和图片编辑"
        
    def initialize(self):
        # 注册快捷键 Alt+Shift+A
        self.plugin_manager.register_hotkey("Alt+Shift+A", self.start_capture)
        
    def create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        capture_btn = QPushButton("开始截图")
        capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(capture_btn)
        
        return widget
        
    def start_capture(self):
        # 隐藏主窗口
        self.plugin_manager.hide_main_window()
        
        # 延迟启动截图
        QTimer.singleShot(200, self._do_capture)
        
    def _do_capture(self):
        self.capture_widget = CaptureWidget()
        self.capture_widget.show()
        
    def get_menu_actions(self):
        return [("截图", self.start_capture)]
```

### 工作日志插件 (plugins/worknote/plugin.py)
```python
from core.base_plugin import BasePlugin
from PySide6.QtWidgets import QWidget, QSplitter
from .editor_widget import MarkdownEditor
from .preview_widget import MarkdownPreview

class WorknotePlugin(BasePlugin):
    def __init__(self, plugin_manager):
        super().__init__(plugin_manager)
        self.name = "工作日志"
        self.description = "Markdown格式的工作日志工具"
        
    def initialize(self):
        pass
        
    def create_widget(self) -> QWidget:
        splitter = QSplitter()
        
        self.editor = MarkdownEditor()
        self.preview = MarkdownPreview()
        
        # 连接编辑器和预览
        self.editor.textChanged.connect(self.preview.update_content)
        
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([1, 1])
        
        return splitter
        
    def get_menu_actions(self):
        return [
            ("新建日志", self.new_note),
            ("打开日志", self.open_note),
            ("保存日志", self.save_note),
            ("导出PDF", self.export_pdf)
        ]
```

## ⚙️ 配置管理

### pyproject.toml (uv项目配置)
```toml
[project]
name = "hsbc-little-worker"
version = "1.0.0"
description = "HSBC个人工作小工具集合"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.8"
dependencies = [
    "PySide6>=6.5.0",
    "marko>=2.0.0",
    "Pillow>=9.0.0",
    "paddleocr>=2.6.0",
    "numpy>=1.21.0",
    "opencv-python>=4.5.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0"
]
```

### 插件配置 (config/plugin_config.json)
```json
{
    "plugins": {
        "capturer": {
            "enabled": true,
            "hotkey": "Alt+Shift+A",
            "ocr_engine": "paddleocr",
            "auto_save": true
        },
        "worknote": {
            "enabled": true,
            "default_template": "daily_report",
            "auto_backup": true,
            "export_formats": ["pdf", "html"]
        }
    },
    "ui": {
        "theme": "dark",
        "language": "zh_CN"
    }
}
```

## 🚀 启动流程

1. **主程序启动** → 初始化核心框架
2. **插件发现** → 扫描plugins目录
3. **插件加载** → 使用importlib动态加载
4. **UI构建** → 创建主窗口和插件界面
5. **事件注册** → 注册快捷键和菜单
6. **运行循环** → 启动Qt事件循环

这个架构具有以下优势：
- ✅ **高度模块化**：每个工具都是独立插件
- ✅ **易于扩展**：新增功能只需添加插件
- ✅ **松耦合**：插件间通过事件系统通信
- ✅ **配置灵活**：支持插件启用/禁用和参数配置
- ✅ **维护简单**：核心框架和业务逻辑分离