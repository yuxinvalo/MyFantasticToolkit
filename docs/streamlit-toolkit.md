# Support Web Toolkit
该插件是一个Streamlit APP，激活时将会启动一个Streamlit APP，用户可以在APP中使用一些工作中可能用到的工具。例如json格式化工具、时差转换、markdown文本撰写转格式等。
enable=False时，插件会优雅地关闭Streamlit APP。

## 插件说明
插件启动方式，可以通过HSBC LittleWorker的插件管理界面点击功能按钮，从而启动脚本（`StreamlitToolkit.py`）打开浏览器展示Streamlit APP。  
对于插件页，需要支持多语言，目前支持中文和英文。   
对于打开的streamlit app，需要支持多语言，目前支持中文和英文，但中英文切换需要在WEB页面中切换，不受主程序的影响。

- 用户点击侧边栏的`WebToolkit`按钮，程序打开插件页面。
- 插件页面展示Streamlit APP的工具按钮：
  - `JSON格式化工具`：用户可以在该工具中输入JSON字符串，程序会将JSON字符串格式化输出。
  - `时差转换工具`：用户可以在该工具中输入时间字符串，程序会将时间字符串转换为指定时区的时间。
  - `Markdown编辑`：用户可以在该工具中输入Markdown文本，并展示效果，可下载为md或者Html格式。
- 插件页面会有一个log区域，用于展示插件的运行日志。
- 插件页面会有一个实时展示APP运行状态的区域，用于展示APP是否正在运行，以及运行状态的描述。
- 用户点击任意工具按钮，程序会检测streamlit app是否正在运行，如果正在运行，则打开对应的工具页面，否则需要先启动streamlit app，再打开对应工具页面。

## 插件配置
插件配置项如下：

```json
 "plugin_info": {
    "name": "WebToolkit",
    "display_name": "Finance IT Support Web Toolkit",
    "version": "1.0.0",
    "author": "Tearsyu",
    "description": "IT Support Web Toolkit, 提供一些常用的工具，例如json格式化工具、时差转换、markdown文本撰写转格式等。",
   },
   "available_config": {
      "enabled": true,
      "port": 8501,
      "host": ["localhost", "0.0.0.0", "localhost"],  # 插件启动的host，默认localhost, 可以配置为0.0.0.0，这样可以通过ip访问
   }
```
## Streamlit APP
每一个工具都对应一个path，例如：
- `json格式化工具`：`/json-formatter`
- `时差转换工具`：`/timezone-converter`
- `Markdown编辑`：`/markdown-editor` 

## 结构

```txt
plugins/support_web_toolkit/
├── streamlit_app.py          # 主页
├── pages/
│   ├── 1_🔧_JSON_Formatter.py
│   ├── 2_🌍_Timezone_Converter.py
│   └── 3_📝_Markdown_Editor.py
└── utils/
    ├── i18n.py              # 翻译工具
    └── common.py            # 公共函数
```

### 🎯 实施步骤
1. 第一阶段 ：创建基础 Streamlit 应用和路由系统
2. 第二阶段 ：实现 JSON 格式化工具
3. 第三阶段 ：实现时差转换工具
4. 第四阶段 ：实现 Markdown 编辑器
5. 第五阶段 ：完善多语言支持和错误处理