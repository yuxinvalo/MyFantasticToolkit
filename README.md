# HSBC Little Worker Project
这是一个python开发的个人工作小工具集合。属于集成式的小工具箱。

## Proposal
这是一个基于Python的HSBC小工项目，用于IT SUPPORT的个人工作，由于HSBC是银行。
对于隐私非常看重，很多好用的工具是需要自己开发的，所以就有了这个项目，仅用于个人，不涉及网络传输，以及任何机密信息。 

## 工具模块

### 自定义截图工具
自定义截图工具不同于WINDOWS系统的截图工具:
- 点击截图按钮或者快捷键ALT+SHIFT+A后隐藏自身，鼠标左键拖动自定义截图区域
- 截图完成后生成一个新的widget，widget包含截图主体，且有工具栏
- 工具栏包括将图片钉在屏幕上，识别图片文字，允许文字复制，画笔涂改图片（可Redo），保存图片。 

### 工作日志工具
IT SUPPORT需要每日监控业务数据的ETL过程，为了记录下每日的工作情况，需要一个小日记本记录，方便handover给下一个组。
日志是markdown格式撰写，且可以自定义工作日志模板。 可以导出为markdown, pdf等格式。
关于Markdown工作日志：
- 实时预览 ：集成markdown解析器（如marko）+ QWebEngineView 显示HTML
- 语法高亮 ：使用 QSyntaxHighlighter 为markdown语法着色
- 工具栏 ：添加常用markdown格式化按钮


## 软件设计
软件设计应该是一个插件化的架构，每个工具都是一个插件，插件之间可以调用，也可以独立运行。   
软件图标： resources/icon.svg

## 技术栈
软件定义是需要简单易用，尽量轻量级，UI风格扁平化。由于内部限制，方便开发和维护，只使用python。 
- UI： pyside6
- markdown解析器：marko
- 项目管理：uv
- 插件化架构：python的importlib模块

