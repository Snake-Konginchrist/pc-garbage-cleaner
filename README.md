# 电脑垃圾清理器

一个跨平台的电脑垃圾清理应用，支持Windows、MacOS和Linux系统。

## 功能特点

- 扫描并清理系统临时文件
- 清理应用程序缓存
- 清理浏览器缓存和历史记录
- 查找并删除大文件和重复文件
- 清理下载文件夹
- 磁盘空间分析与可视化
- 简洁美观的图形用户界面
- 系统运行状态监控

## 系统要求

- Python 3.7+
- 支持Windows、MacOS和Linux系统

## 安装说明

1. 克隆此仓库：
```
git clone https://gitee.com/Snake-Konginchrist/pc-garbage-cleaner.git
cd pc-garbage-cleaner
```

2. 安装依赖：
```
pip install -r requirements.txt
```

3. 运行应用：
```
python main.py
```

## 项目结构

```
pc_garbage_cleaner/
│
├── main.py                 # 应用程序入口点
├── requirements.txt        # 项目依赖
│
├── core/                   # 核心功能模块
│   ├── __init__.py
│   ├── scanner.py          # 文件扫描器
│   ├── cleaner.py          # 文件清理器
│   ├── analyzer.py         # 磁盘分析器
│   └── system_info.py      # 系统信息获取
│
├── ui/                     # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── scan_tab.py         # 扫描选项卡
│   ├── clean_tab.py        # 清理选项卡
│   ├── analyze_tab.py      # 分析选项卡
│   └── resources/          # UI资源(图标等)
│
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── file_utils.py       # 文件操作工具
│   ├── path_utils.py       # 路径处理工具
│   └── system_utils.py     # 系统相关工具
│
└── tests/                  # 测试模块
    ├── __init__.py
    ├── test_scanner.py
    ├── test_cleaner.py
    └── test_analyzer.py
```

## 使用方法

1. 启动应用后，选择"扫描"选项卡进行垃圾文件扫描
2. 在扫描结果中勾选需要清理的项目
3. 点击"清理"按钮执行清理操作
4. 使用"分析"选项卡查看磁盘空间使用情况

## 安全说明

- 应用会在删除重要文件前请求确认
- 建议在首次使用时先查看扫描结果而不直接清理
- 某些系统文件夹可能需要管理员权限才能清理

## 许可证

MIT 

## 应用程序打包指南

项目提供了一个便捷的打包脚本`build.py`，可以轻松打包为各平台的应用程序：

### 基本用法

在命令行中运行：
```bash
python build.py
```

这将根据你当前的操作系统平台，将应用程序打包成对应平台的可执行文件。

### 命令行参数

脚本支持以下命令行参数：

1. `--platform`: 选择打包平台
   - 可选值: `windows`, `macos`, `linux`, `all`
   - 默认为当前平台
   - 例如: `python build.py --platform windows`

2. `--onefile`: 打包为单个可执行文件
   - 例如: `python build.py --onefile`

3. `--console`: 显示控制台窗口
   - 默认为无控制台(GUI模式)
   - 例如: `python build.py --console`

4. `--upx`: 使用UPX压缩可执行文件
   - 需要安装UPX
   - 例如: `python build.py --upx`

5. `--clean`: 清理构建文件
   - 删除previous builds, spec文件等
   - 例如: `python build.py --clean`

6. `--no-dmg`: 跳过为macOS创建DMG安装包
   - 仅macOS平台有效
   - 默认情况下会创建DMG安装包
   - 需要安装create-dmg工具
   - 例如: `python build.py --platform macos --no-dmg`

7. `--no-deb`: 跳过为Linux创建DEB安装包
   - 仅Linux平台有效
   - 默认情况下会创建DEB安装包
   - 例如: `python build.py --platform linux --no-deb`

8. `--use-english-name`: 统一使用英文名称作为应用程序名称
   - 例如: `python build.py --use-english-name`

### 常用打包命令示例

1. 为Windows打包为单个可执行文件：
```bash
python build.py --platform windows --onefile
```

2. 清理旧的构建文件：
```bash
python build.py --clean
```

3. 为当前平台打包（带控制台窗口，用于调试）：
```bash
python build.py --console
```

4. 为所有平台打包（如果你在开发环境中有所有平台的依赖）：
```bash
python build.py --platform all
```

5. 为macOS打包但不创建DMG安装包：
```bash
python build.py --platform macos --no-dmg
```

6. 为Linux打包但不创建DEB安装包：
```bash
python build.py --platform linux --no-deb
```

执行打包后，可执行文件将位于`dist`目录下。

### 注意事项

1. 在使用前需要安装PyInstaller（脚本会检查并尝试安装）
2. 图标文件应放在`ui/resources`目录中
3. 创建DMG需要在macOS上安装`create-dmg`工具
4. 创建DEB包需要在Linux上安装`dpkg-deb`工具
5. 打包前请确保应用能正常运行
6. 跨平台构建说明：
   - 在Windows上可以构建Windows应用程序
   - 在macOS上可以构建macOS和Windows应用程序
   - 在Linux上可以构建Linux和Windows应用程序
   - 创建DMG安装包只能在macOS系统上完成
   - 创建DEB安装包只能在Linux系统上完成
   - 跨平台构建时，脚本会自动跳过无法在当前系统执行的步骤，并提供适当的提示信息

查看所有选项:
```bash
python build.py --help
```

## 故障排除

如果遇到图形界面显示问题，请确保安装了正确版本的PyQt5：

```bash
pip uninstall PyQt5 PyQt5-sip
pip install PyQt5
```

## 贡献指南

欢迎提交Pull Request或Issue。

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。