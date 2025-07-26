# LittleCapturer
专业的截图工具插件，超越Windows系统自带截图功能，提供更多的截图选项和自定义功能。

## Plugin说明
Plugin应当有两种启动方式，可以通过HSBC LittleWorker的插件管理界面来启动，也可以直接通过plugin入口脚本（`LittleCapturer.py`）单独启动程序。

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
