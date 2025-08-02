# HSBC Little Worker 项目结构与部署指南

## 📁 项目目录结构

HSBC Little Worker 采用插件化架构设计，支持模块化开发和动态扩展。项目结构清晰分层，便于维护和扩展。

```
HSBCLittleWorker/
├── main.py                    # 主程序入口
├── pyproject.toml             # uv项目配置文件
├── requirements.txt           # 依赖管理
├── README.md                  # 项目说明
├── config/                    # 配置文件目录
│   ├── __init__.py
│   └── app_config.json        # 应用配置（包含插件配置和全局设置）
├── core/                      # 核心框架
│   ├── __init__.py
│   ├── application.py         # 主应用程序类
│   ├── plugin_manager.py      # 插件管理器
│   ├── plugin_base.py         # 插件基类
│   ├── event_system.py        # 事件系统
│   └── ui/                    # 核心UI组件
│       ├── __init__.py
│       ├── main_window.py     # 主窗口
│       ├── plugin_dock.py     # 插件停靠窗口
│       └── styles/            # 样式文件
│           ├── base.qss       # 基础样式
│           ├── dark_theme.qss # 深色主题
│           ├── light_theme.qss# 浅色主题
│           └── components.qss # 组件样式
├── plugins/                   # 插件目录
│   ├── __init__.py
│   ├── demo_plugin/           # 演示插件
│   │   ├── __init__.py        # 插件主文件（包含Plugin类）
│   │   ├── config.json        # 插件配置
│   │   └── translations/      # 插件翻译
│   │       ├── zh_CN.json     # 中文翻译
│   │       └── en_US.json     # 英文翻译
│   └── capturer/              # 截图工具插件
│       ├── __init__.py        # 插件主文件
│       ├── config.json        # 插件配置
│       ├── translations/      # 插件翻译
│       └── resources/         # 资源文件
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── logger.py              # 日志工具（包含日志清理功能）
│   ├── file_utils.py          # 文件操作
│   ├── image_utils.py         # 图像处理
│   └── hotkey_manager.py      # 快捷键管理
├── resources/                 # 全局资源
│   ├── icons/                 # 图标文件
│   ├── fonts/                 # 字体文件
│   └── translations/          # 国际化文件
│       ├── zh_CN.json         # 中文翻译
│       └── en_US.json         # 英文翻译
├── logs/                      # 日志文件目录
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_core/
│   ├── test_plugins/
│   └── test_utils/
└── docs/                      # 文档
    ├── api.md
    ├── plugin_development.md  # 插件开发指南
    ├── project_structure.md   # 项目结构说明
    └── user_guide.md
```

## 🏗️ 核心架构设计

### 架构概述

HSBC Little Worker 采用分层架构设计，主要包含以下几个层次：

- **应用层 (main.py)**: 应用程序入口，负责初始化和启动
- **核心层 (core/)**: 提供插件管理、事件系统、UI框架等核心功能
- **插件层 (plugins/)**: 各种功能插件，支持动态加载和卸载
- **工具层 (utils/)**: 通用工具和辅助功能
- **资源层 (resources/)**: 静态资源文件

### 插件系统特性

- **动态加载**: 运行时发现和加载插件，无需重启应用
- **配置管理**: 每个插件独立的配置文件和设置项
- **国际化支持**: 插件专属的翻译文件，支持中英文切换
- **生命周期管理**: 完整的插件初始化、运行和清理流程
- **UI集成**: 插件界面无缝集成到主应用窗口
- **日志系统**: 统一的日志记录和管理

### 插件开发规范

每个插件必须包含以下文件：
- `__init__.py`: 包含Plugin类的主文件
- `config.json`: 插件配置文件
- `translations/`: 翻译文件目录
  - `zh_CN.json`: 中文翻译
  - `en_US.json`: 英文翻译

详细的插件开发指南请参考 [plugin_development.md](plugin_development.md)。

## 🔌 插件实现示例

项目包含多个功能插件，展示了插件系统的灵活性和扩展性：

### 演示插件 (demo_plugin)
- **功能**: 展示插件系统的基本功能和开发模式
- **特性**: 计数器功能、配置管理、国际化支持
- **用途**: 作为插件开发的参考模板

### 截图工具插件 (capturer)
- **功能**: 自定义截图工具，支持OCR文字识别和图片编辑
- **特性**: 快捷键支持、悬浮窗口、图片处理
- **技术**: 集成PaddleOCR引擎，支持多种图片格式

### 其他插件
项目支持无限扩展，可以根据需要添加更多功能插件，如：
- 工作日志插件：Markdown编辑器和预览
- 文件管理插件：快速文件操作
- 系统监控插件：资源使用情况监控

每个插件都遵循统一的开发规范，具有独立的配置、翻译和资源文件。

## ⚙️ 配置管理

### 项目配置

**pyproject.toml**: 使用uv作为包管理器，配置项目依赖和元信息
- 主要依赖：PySide6、Pillow、PaddleOCR等
- 开发依赖：pytest、black、flake8等测试和代码格式化工具
- Python版本要求：>=3.8

**requirements.txt**: 传统的pip依赖文件，与pyproject.toml保持同步

### 应用配置

**config/app_config.json**: 全局应用配置
- 插件启用状态和全局设置
- UI主题和语言设置
- 系统级配置项

**插件配置**: 每个插件独立的config.json文件
- plugin_info: 插件基本信息（只读）
- available_config: 可配置项（运行时可修改）
- 支持多种数据类型：布尔值、字符串、整数、列表、快捷键等

### 国际化配置

**全局翻译**: resources/translations/
- zh_CN.json: 中文翻译
- en_US.json: 英文翻译

**插件翻译**: 每个插件的translations/目录
- 插件专属的翻译文件
- 支持参数化翻译文本

## 🚀 启动流程

应用程序启动遵循以下流程：

1. **应用初始化** → 加载全局配置，初始化日志系统
2. **日志清理** → 自动清理五天前的日志文件
3. **插件发现** → 扫描plugins目录，发现可用插件
4. **插件加载** → 动态加载插件模块和配置
5. **UI构建** → 创建主窗口，集成插件界面
6. **事件注册** → 注册快捷键、菜单和事件监听
7. **运行循环** → 启动Qt事件循环，响应用户交互
8. **优雅退出** → 调用插件cleanup方法，保存配置

## 📦 应用程序打包与部署

### PyInstaller 打包建议

为了解决Windows任务管理器中显示"python"进程名的问题，推荐使用PyInstaller将应用程序打包为独立的可执行文件。

#### 打包命令

```bash
# 推荐使用spec文件进行打包
pyinstaller "HSBC Little Worker.spec"

# 或者使用命令行参数（不推荐，建议使用spec文件）
pyinstaller \
  --onefile \
  --windowed \
  --name="HSBC Little Worker" \
  --icon="resources/icon.ico" \
  --add-data="config;config" \
  --add-data="resources;resources" \
  --add-data="plugins;plugins" \
  --hidden-import="webbrowser" \
  --hidden-import="subprocess" \
  --hidden-import="json" \
  --hidden-import="time" \
  --hidden-import="pathlib" \
  --hidden-import="datetime" \
  --hidden-import="typing" \
  --hidden-import="logging" \
  --hidden-import="sys" \
  --hidden-import="os" \
  --hidden-import="streamlit" \
  --hidden-import="pytz" \
  --hidden-import="pandas" \
  --hidden-import="markdown" \
  main.py
```

#### 参数说明

- `--onefile`: 打包为单个可执行文件
- `--windowed`: 无控制台窗口（GUI应用）
- `--name`: 指定可执行文件名称
- `--icon`: 设置应用程序图标
- `--add-data`: 添加必要的资源文件和插件目录
- `--hidden-import`: 显式导入PyInstaller可能遗漏的模块

#### PyInstaller Spec文件配置

推荐使用spec文件进行打包配置，这样可以更好地控制打包过程：

```python
# HSBC Little Worker.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('resources', 'resources'),
        ('plugins', 'plugins'),
    ],
    hiddenimports=[
        'webbrowser', 'subprocess', 'json', 'time', 'pathlib',
        'datetime', 'typing', 'logging', 'sys', 'os',
        'streamlit', 'pytz', 'pandas', 'markdown'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
```

#### 推荐的部署目录结构

```
HSBC Little Worker/
├── HSBC Little Worker.exe    # 主程序
├── plugins/                  # 插件目录（独立于打包文件）
│   ├── demo_plugin/
│   └── capturer/
├── logs/                     # 日志目录
└── user_data/               # 用户数据目录
    └── configs/             # 用户配置文件
```

#### 插件目录处理

**为什么要排除plugins目录？**
- 插件可能会频繁更新，不应与主程序绑定
- 用户可能需要自定义或禁用某些插件
- 便于插件的独立开发和测试
- 减小打包文件体积

#### 打包环境路径适配

为了确保应用程序在打包后能正确访问资源文件和配置文件，需要对路径获取逻辑进行适配：

**资源文件路径适配**

```python
# 在application.py中的_get_resource_path方法
def _get_resource_path(self, filename):
    """获取资源文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境，使用sys._MEIPASS获取临时解压目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
    
    return base_path / "resources" / filename
```

**配置文件路径适配**

```python
# 在application.py中的_get_config_path方法
def _get_config_path(self, filename):
    """获取配置文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
    
    return base_path / "config" / filename
```

**插件目录路径适配**

```python
# 在plugin_manager.py中的_get_plugins_dir方法
def _get_plugins_dir(self):
    """获取插件目录路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
    
    return base_path / "plugins"
```

#### 打包优势

- ✅ **进程名称**: 任务管理器显示"HSBC Little Worker"而非"python"
- ✅ **独立部署**: 无需安装Python环境
- ✅ **版本管理**: 主程序和插件可独立更新
- ✅ **用户友好**: 双击即可运行，无需命令行
- ✅ **安全性**: 减少依赖冲突和环境问题

#### 常见打包问题及解决方案

**1. 模块导入错误**
- 问题：打包后运行时提示"No module named 'xxx'"
- 解决：在spec文件的hiddenimports中添加缺失的模块

**2. 资源文件找不到**
- 问题：打包后无法找到图标、配置文件等资源
- 解决：确保在datas中正确配置资源目录，并使用sys._MEIPASS获取路径

**3. 插件加载失败**
- 问题：打包后插件无法正常加载
- 解决：确保plugins目录被正确打包，并适配插件路径获取逻辑

**4. 系统托盘图标不显示**
- 问题：打包后系统托盘图标无法显示
- 解决：使用_get_resource_path方法获取图标路径，确保图标文件被正确打包

#### 注意事项

- 首次打包可能需要较长时间（5-10分钟）
- 打包后的文件体积会增大（约100-200MB）
- 需要在目标系统上测试兼容性
- 插件开发时仍建议使用源码方式运行
- 建议使用spec文件而非命令行参数进行打包配置
- 打包前确保所有依赖模块都已正确安装
