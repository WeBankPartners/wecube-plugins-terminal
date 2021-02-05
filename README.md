
# Terminal插件
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![](https://img.shields.io/badge/language-python-orang.svg)



## 简介

Terminal插件提供了远程终端接入能力，在用户既有权限内更加方便的进行终端操作。 

主要功能：

1. 多标签ssh终端会话
2. 支持文件上传/下载
3. 支持连接 & 文件传输统一权限控制
4. 支持空闲会话回收
5. 支持文件传输记录 & 历史会话 审计
6. 支持实时终端输入的高危命令检测



## 概念说明

**a) 系统参数**

需要修改插件的系统参数以正确启动插件服务

| 名称                             | 默认值                        | 描述                                                         |
| -------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| TERMINAL_ASSET_TYPE              | wecmdb:host_resource_instance | 终端资产类型，比如cmdb插件中的主机资源，格式为package:entity |
| TERMINAL_FIELD_NAME              | name                          | 从TERMINAL_ASSET_TYPE数据中提取的名称字段                    |
| TERMINAL_FIELD_IP                | ip_address                    | 从TERMINAL_ASSET_TYPE数据中提取的登陆IP字段                  |
| TERMINAL_FIELD_PORT              | login_port                    | 从TERMINAL_ASSET_TYPE数据中提取的登陆端口字段                |
| TERMINAL_FIELD_USER              | user_name                     | 从TERMINAL_ASSET_TYPE数据中提取的登陆用户名字段              |
| TERMINAL_FIELD_PASSWORD          | user_password                 | 从TERMINAL_ASSET_TYPE数据中提取的登陆密码字段，支持qcloud/saltstack的{cipher_a}加密数据 |
| TERMINAL_FIELD_DESC              | description                   | 从TERMINAL_ASSET_TYPE数据中提取的描述字段                    |
| TERMINAL_SESSION_TIMEOUT         | 1800                          | 出于安全的考虑，会话不会长期有效，此变量控制一个会话在持续多少秒过程中如果用户无任何操作，服务器将主动断开会话连接 |
| TERMINAL_WEBSOCKET_URL           | ws://127.0.0.1:19002          | WebSocket连接地址，插件在19002端口注册了websocket服务，以提供ssh会话能力，请根据实际访问IP进行更改，格式为ws://IP:PORT。 |
| TERMINAL_COMMAND_CHECK           | ON                            | 是否启用终端实时高危命令检测，可选ON/OFF                     |
| TERMINAL_BOXES                   | all                           | 使用哪些高危命令插件的box进行命令检测，默认为all表示所有已启用的box，可以更改为box id列表，以","符号进行分隔，比如：1,2,3表示仅使用1/2/3这3个box进行检测。 |
| TERMINAL_FILE_DOWNLOAD_MAX_BYTES | 104857600                     | 出于安全的考虑，文件下载可以进行单个下载文件的大小限制，单位为byte，默认100MB |

至少需要修改TERMINAL_WEBSOCKET_URL参数才能正常使用插件。



## 痛点解决

插件提供了常见的安全终端功能：文件传输 & 终端连接的权限管理，以及文件传输记录 & 历史会话回放的审计能力，会话回收。

安全终端常见方式是使用了正则模式进行高危命令识别，通常是进行事后的或者极少一部分实时输入的命令分析进行审计，而terminal中实现了更多的用户输入模式，能实时解析大部分命令，并对接[高危命令检测插件](https://github.com/WeBankPartners/wecube-plugins-itsdangerous)实现优于正则的高危命令识别能力，让操作更加安全。



## 反馈

如果您遇到问题，请给我们提[Issue](https://github.com/WeBankPartners/wecube-plugins-terminal/issues/new/choose)，我们会第一时间反馈。