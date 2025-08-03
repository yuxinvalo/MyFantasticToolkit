# HSBC Little Worker Project

🛠️ A Python-based personal work toolkit collection with a plugin-based architecture design as an integrated toolbox.

## 📋 Project Overview

This is a Python toolkit project specifically designed for the HSBC IT SUPPORT team. Due to the bank's strict requirements for privacy and security, many practical tools need to be developed internally. This project is committed to providing a secure and efficient personal work toolkit collection that **runs completely locally without any network transmission or confidential information processing**.

### ✨ Core Features

- 🔌 **Plugin Architecture**: Modular design, easy to extend and maintain
- 🛡️ **Secure & Reliable**: Completely local operation, no network dependencies
- 🎨 **Modern UI**: Flat interface design based on PySide6
- 🌍 **Internationalization**: Support for Chinese/English interface switching
- ⚙️ **Flexible Configuration**: Support for plugin enable/disable and personalized settings

## 🚀 Current Status

### ✅ Implemented Features

- **Core Framework**: Complete plugin-based application framework
- **Plugin Manager**: Dynamic plugin loading, unloading, and configuration management
- **Internationalization System**: Multi-language support (Chinese/English)
- **Configuration Management**: JSON format configuration file system
- **Logging System**: Complete logging and management
- **Demo Plugin**: Example demonstrating plugin development and integration

### 📦 Project Structure

```
HSBCLittleWorker/
├── main.py                    # 🚀 Main program entry
├── pyproject.toml             # 📋 uv project configuration
├── config/                    # ⚙️ Configuration directory
│   └── app_config.json        # Application configuration (includes plugin config and global settings)
├── core/                      # 🏗️ Core framework
│   ├── application.py         # Main application class
│   ├── plugin_manager.py      # Plugin manager
│   ├── plugin_base.py         # Plugin base class
│   ├── main_window.py         # Main window
│   ├── i18n.py               # Internationalization management
│   └── settings_dialog.py     # Settings dialog
├── plugins/                   # 🔌 Plugin directory
│   └── demo_plugin/           # Demo plugin
├── utils/                     # 🛠️ Utility modules
│   └── logger.py              # Logging utility
├── resources/                 # 📁 Resource files
│   ├── icon.svg              # Application icon
│   └── translations/          # Internationalization files
└── docs/                      # 📚 Documentation
```

## 🎯 Pending Implementation List

### 🖼️ Custom Screenshot Tool Plugin

**Feature Description**: Professional screenshot tool that surpasses Windows built-in screenshot functionality

**Core Features**:
- 🎯 Hotkey trigger (ALT+SHIFT+A) automatically hides main window
- 🖱️ Mouse drag custom screenshot area selection
- 🛠️ Post-screenshot editing toolbar including:
  - 📌 Pin image on screen (floating display)
  - 🔍 OCR text recognition and copy functionality
  - ✏️ Paint brush editing tools (support undo/redo)
  - 💾 Image save and export functionality

### 📝 Work Log Tool Plugin

**Feature Description**: Markdown log tool designed specifically for IT SUPPORT daily work

**Application Scenarios**: Recording ETL process monitoring, problem handling, work handover, etc.

**Core Features**:
- 📄 Markdown format writing with rich text formatting support
- 👀 Real-time preview (marko parser + QWebEngineView)
- 🎨 Syntax highlighting (QSyntaxHighlighter)
- 🛠️ Formatting toolbar (common Markdown shortcut buttons)
- 📋 Custom work log template system
- 📤 Multi-format export (Markdown, PDF, HTML)

## 🛠️ Technology Stack

**Design Philosophy**: Simple to use, lightweight, flat UI design

**Core Technologies**:
- **UI Framework**: PySide6 - Modern Python GUI framework
- **Markdown Parsing**: marko - High-performance Markdown parser
- **Project Management**: uv - Modern Python package management tool
- **Plugin System**: importlib - Python native dynamic import module
- **Internationalization**: Self-developed i18n system supporting JSON format translation files
- **Logging System**: Python logging + custom formatting

## 🚀 Quick Start

### Requirements
- Python 3.8+
- Windows 10/11

### Installation & Running

```bash
# Clone project
git clone <repository-url>
cd HSBCLittleWorker

# Install dependencies (using uv)
uv sync

# Run application
python main.py
```

## 📖 More Information

- 📋 [Detailed Project Structure](project_structure.md)
- 🔌 [Plugin Development Guide](docs/plugin_development.md)
- 📚 [User Manual](docs/user_guide.md)

---

**Note**: This project is exclusively for HSBC internal IT SUPPORT team use, strictly adhering to banking security regulations, and does not involve any sensitive data processing.