# Support Web Toolkit
该插件是一个Streamlit APP，激活时将会启动一个Streamlit APP，用户可以在APP中使用一些工作中可能用到的工具。例如json格式化工具、时差转换、markdown文本撰写转格式、待办事项管理等。
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
  - `Todo List`：用户可以在该工具中管理待办事项，支持添加、编辑、删除、完成任务，以及设置优先级（urgent/medium/low），数据持久化保存。
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
    "description": "IT Support Web Toolkit, 提供一些常用的工具，例如json格式化工具、时差转换、markdown文本撰写转格式、待办事项管理等。",
   },
   "available_config": {
      "enabled": true,
      "port": 8501,
      "host": ["localhost", "0.0.0.0", "localhost"],  # 插件启动的host，默认localhost, 可以配置为0.0.0.0，这样可以通过ip访问
   }
```
## Streamlit APP
每一个工具都对应一个path：
- `json格式化工具`：`/1_JSON_Formatter`
- `时差转换工具`：`/2_Timezone_Converter`
- `Markdown编辑`：`/3_Markdown_Editor`
- `Todo List`：`/4_Todo_List` 
- `Data Viewer`：`/5_Data_Viewer`
- `Libre CMD`：`/6_Libre_CMD`


## 结构

```txt
plugins/support_web_toolkit/
├── streamlit_app.py          # 主页
├── pages/
│   ├── 1_JSON_Formatter.py
│   ├── 2_Timezone_Converter.py
│   ├── 3_Markdown_Editor.py
│   ├── 4_Todo_List.py
│   ├── 5_Data_Viewer.py
│   └── 6_Libre_CMD.py
├── common.py                 # 公共函数和翻译工具
└── translations/             # 多语言翻译文件
    ├── zh_CN.json
    └── en_US.json
```

## Libre CMD
Libre CMD是一个命令行工具，用户可以在该工具中输入命令，程序会在指定的服务器上执行命令，并将结果返回给用户。 这是一个比较特殊的工具，它的配置除了在 config.json（username_sso 和 password_sso）中，其他的固定配置则需要保存到 libre_cmd.json。    

### Libre CMD 目的
注意，该项目的目的仅仅是用于IT SUPPORT一些简单的日常查询和监控，具体权限会受到用户在服务器的登陆账号限制, 做到一次设定，多次使用，避免了打开putty，手动输入账号，查询文档等一系列操作花的时间。 
但本项目并不能进行复杂的命令行结果显示，过滤等，这违背了设计的初衷。 对于一些日期时间相关的查询，本项目并不能进行格式化，用户需要手动在命令中添加日期时间参数。


### Libre CMD 配置说明
该文件由用户通过页面设定，实时保存，实时读取。 
文件格式为json，示例如下：

```json
{
    "servers": ["192.168.3.14", "gbl1020203.system.hsbc.com"],
    "libre_cmd": {
      "Monthly HUB File Check": {
        "description": "检查HUB文件内容",
        "server": "192.168.3.14",
        "steps": [
          {
            "command": "cd /home/tearsyu/Documents/tests/hsbc_workflow && cat WORKFLOW_TRIGGER_LOG_20250731.csv",
            "output_type": "csv",
            "delimiter": "|"
          },
          {
            "command": "cd Documents && ls -alht",
            "output_type": "text",
          "delimiter": null
        }
      ]
    },
    "Check system status": {
      "description": "检查系统状态",
      "server": "192.168.3.14",
      "steps": [
        {
          "command": "cd /home/tearsyu/Documents/tests/hsbc_workflow && cat hsbc_test.json",
          "output_type": "json",
          "delimiter": null

        },
        {
          "command": "top",
          "output_type": "text",
          "delimiter": null
        }
      ]
    }
  }
}

```

- servers: 用户保存的服务器列表，用户可以在页面中添加、删除、修改服务器。
- libre_cmd: 用户保存的命令列表，用户可以在页面中添加、删除、修改一个cmd workflow。
  - description: 关于这一个cmd workflow的简单描述，最多100字。
  - server: 命令执行的服务器，用户可以在servers中选择，也可以手动填写，如果是手动填写且不存在于servers，则自动添加到servers列表。
  - steps: 命令的执行步骤描述。
    - command: 需要运行的命令行。
    - output_type: 命令的输出类型，目前一共支持csv, json, text三种格式。
    - delimiter: 如果用户选择csv格式，则需要指定csv的分隔符，否则无法创建该workflow. 
    - timeout: 命令执行的超时时间，单位为秒，默认60秒。


### library
- UI: streamlit
- 命令执行库: paramiko

### 输出格式说明
- csv: streamlit内置的表格显示，最多显示1000行
- json: 键值对格式，streamlit内置的json显示框, 如果json字符长度超过10000则保存到Downloads目录下。
- text: 普通文本格式，直接在页面中展示，最多10000字符, 如果字符长度超过10000则保存到Downloads目录下。
- 其他格式: 其他格式暂不支持，后续根据需求添加。


### UI设计
- 标题栏下是一个按钮，点击后进入 Libre CMD的配置页面, 可添加servers，或者导入，编辑，删除，添加cmd workflow。
- 按钮下是一个下拉列表，用户可以选择已经保存的cmd workflow。
- 选择cmd workflow后，会显示该workflow的标题，description，一个复制按钮（用于复制该workflow的json配置），以及每个step的command，等待用户点击执行。
- 每执行完一个step，根据需求展示输出，如果出错则终止执行，展示错误信息。

如果用户更换cmd workflow，应当清空之前所有和上一个cmd workflow相关的内容，重新再生成。

### TODO
[✓] - execute cmd tab界面，可以临时修改cmd和server内容（已完成：添加了临时编辑功能，可在执行前修改服务器地址和命令内容，修改不会保存到配置文件）
[✓] - configuration tab界面，增加workflow的修改功能（已完成：在配置页面中，可以修改工作流，并保存到libre_cmd.json文件中）
[✓] - UI再调整调整，没想好，但目前的不太好看
[✓] - 对于top这类命令，会报错，需要考虑怎么显示的问题
[✓] - 测试ls -alht 这类命令是否能通过csv方式显示
[] - 多测试一些命令，增加最佳实践文档，如何写一个workflow

