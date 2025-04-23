# 电脑垃圾清理器 - 程序设计说明文档

## 1. 系统概述

### 1.1 项目简介

电脑垃圾清理器是一个跨平台的应用程序，支持Windows、MacOS和Linux系统，旨在帮助用户扫描、分析和清理计算机中的垃圾文件，优化系统性能并释放磁盘空间。本程序使用Python语言开发，具有直观的图形用户界面，并提供了多种垃圾文件清理功能。

### 1.2 系统功能

本系统主要功能包括：

- 扫描并清理系统临时文件
- 清理应用程序缓存
- 清理浏览器缓存和历史记录
- 查找并删除大文件和重复文件
- 清理下载文件夹
- 磁盘空间使用分析与可视化
- 系统运行状态监控

### 1.3 适用环境

- 操作系统：Windows、MacOS、Linux
- 运行环境：Python 3.7及以上版本
- 依赖库：PyQt5、psutil、send2trash、matplotlib、numpy

## 2. 系统设计

### 2.1 系统架构

本系统采用模块化设计，整体架构分为以下几个部分：

1. **核心功能模块**：实现垃圾文件的扫描、清理和磁盘分析等核心功能
2. **用户界面模块**：提供图形化用户界面，实现用户交互
3. **工具模块**：提供文件操作、路径处理和系统相关的通用工具函数
4. **测试模块**：提供系统功能测试

系统采用MVC设计模式，分离了数据模型、界面视图和控制逻辑，使代码结构清晰，便于维护和扩展。

### 2.2 目录结构

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

### 2.3 模块设计

#### 2.3.1 核心功能模块

核心功能模块包含四个主要组件：

1. **Scanner（扫描器）**：负责扫描系统中的垃圾文件
2. **Cleaner（清理器）**：负责清理已扫描到的垃圾文件
3. **Analyzer（分析器）**：负责分析磁盘空间使用情况
4. **SystemInfo（系统信息）**：负责获取系统状态信息

#### 2.3.2 用户界面模块

用户界面模块基于PyQt5框架实现，包含以下组件：

1. **MainWindow（主窗口）**：程序的主窗口，包含选项卡布局
2. **ScanTab（扫描选项卡）**：实现文件扫描功能的界面
3. **CleanTab（清理选项卡）**：实现文件清理功能的界面
4. **AnalyzeTab（分析选项卡）**：实现磁盘分析功能的界面

#### 2.3.3 工具模块

工具模块提供通用功能支持，包含：

1. **FileUtils（文件工具）**：提供文件操作相关功能
2. **PathUtils（路径工具）**：提供路径处理相关功能
3. **SystemUtils（系统工具）**：提供系统相关功能

## 3. 详细设计

### 3.1 核心功能模块

#### 3.1.1 Scanner（扫描器）

Scanner模块实现了对系统垃圾文件的扫描功能。它定义了以下主要类：

- **ScanTarget**：扫描目标类，表示一个需要扫描的目标目录
- **ScanResult**：扫描结果类，存储扫描发现的垃圾文件信息
- **ScanFilter**：扫描过滤器类，用于过滤扫描结果
- **Scanner**：扫描器主类，实现扫描功能

主要功能方法：
- `add_target(target)`: 添加扫描目标
- `add_common_targets()`: 添加常见的垃圾文件扫描目标
- `scan(filter_obj, progress_callback, complete_callback)`: 开始扫描过程
- `abort_scan()`: 中止扫描过程

扫描过程采用多线程实现，避免界面阻塞，并通过回调函数更新进度和结果。

#### 3.1.2 Cleaner（清理器）

Cleaner模块实现了对扫描发现的垃圾文件的清理功能。它定义了以下主要类：

- **CleanTask**：清理任务类，表示一个需要执行的清理任务
- **CleanResult**：清理结果类，存储清理操作的结果
- **Cleaner**：清理器主类，实现清理功能

主要功能方法：
- `add_task(task)`: 添加清理任务
- `from_scan_results(scan_results, selected_results)`: 从扫描结果创建清理任务
- `clean(progress_callback, complete_callback)`: 开始清理过程
- `abort_clean()`: 中止清理过程

清理过程也采用多线程实现，支持安全删除（移动到回收站）和强制删除两种方式。

#### 3.1.3 Analyzer（分析器）

Analyzer模块实现了对磁盘空间使用情况的分析功能。它定义了以下主要类：

- **DiskItem**：磁盘项类，表示一个文件或目录
- **AnalyzeResult**：分析结果类，存储分析结果
- **Analyzer**：分析器主类，实现分析功能

主要功能方法：
- `analyze_disk(path, max_depth, progress_callback, complete_callback)`: 分析指定路径
- `abort_analyze()`: 中止分析过程
- `get_disk_usage(path)`: 获取磁盘使用情况
- `get_all_disks()`: 获取所有磁盘列表

磁盘分析功能支持限制分析深度，能够识别最大的文件和目录，以及不同文件类型的空间占用情况。

#### 3.1.4 SystemInfo（系统信息）

SystemInfo模块实现了获取系统状态信息的功能。它定义了以下主要类：

- **SystemInfo**：系统信息类，提供系统状态和信息的获取方法

主要功能方法：
- `get_system_info()`: 获取系统基本信息
- `get_cpu_info()`: 获取CPU信息
- `get_memory_info()`: 获取内存信息
- `get_disk_info()`: 获取磁盘信息
- `get_network_info()`: 获取网络信息
- `get_process_list(sort_by, descending, limit)`: 获取进程列表
- `get_system_status()`: 获取系统当前状态

该模块利用psutil库获取系统状态信息，支持Windows、MacOS和Linux系统。

### 3.2 工具模块

#### 3.2.1 FileUtils（文件工具）

FileUtils模块提供文件操作相关的功能，包括文件属性获取、文件哈希计算、文件删除、文件查找等。

主要功能方法：
- `get_file_size(file_path)`: 获取文件大小
- `get_file_creation_time(file_path)`: 获取文件创建时间
- `get_file_modification_time(file_path)`: 获取文件最后修改时间
- `calculate_file_hash(file_path, hash_type, buffer_size)`: 计算文件哈希值
- `safe_delete_file(file_path)`: 安全删除文件（移动到回收站）
- `force_delete_file(file_path)`: 强制删除文件
- `list_files(directory, recursive, include_dirs, filter_func)`: 列出目录中的文件
- `find_files_by_age(directory, days, older_than, recursive)`: 根据文件年龄查找文件
- `find_large_files(directory, min_size_mb, recursive)`: 查找大文件
- `find_duplicate_files(directories, recursive)`: 查找重复文件

#### 3.2.2 PathUtils（路径工具）

PathUtils模块提供路径处理相关的功能，包括路径规范化、应用程序路径获取、系统目录判断等。

主要功能方法：
- `normalize_path(path)`: 规范化路径
- `get_user_home_dir()`: 获取用户主目录路径
- `get_app_data_dir(app_name)`: 获取应用程序数据目录
- `get_app_config_dir(app_name)`: 获取应用程序配置目录
- `get_app_cache_dir(app_name)`: 获取应用程序缓存目录
- `get_app_logs_dir(app_name)`: 获取应用程序日志目录
- `get_common_system_dirs()`: 获取常见的系统目录列表
- `is_system_directory(path)`: 检查指定路径是否为系统目录

#### 3.2.3 SystemUtils（系统工具）

SystemUtils模块提供系统相关的功能，包括系统类型判断、系统路径获取、磁盘使用情况获取等。

主要功能方法：
- `get_system_type()`: 获取当前操作系统类型
- `is_windows()`, `is_macos()`, `is_linux()`: 检查当前系统类型
- `get_temp_directories()`: 获取系统的临时目录列表
- `get_downloads_directory()`: 获取下载目录的路径
- `get_browser_cache_directories()`: 获取常见浏览器缓存目录列表
- `get_disk_usage(path)`: 获取指定路径的磁盘使用情况
- `format_size(size_bytes)`: 将字节大小转换为人类可读的格式

## 4. 数据结构设计

### 4.1 ScanTarget类

```python
class ScanTarget:
    def __init__(self, name, path, description=None, is_system=False, recursive=True, enabled=True):
        self.name = name                # 目标名称
        self.path = path                # 目标路径
        self.description = description  # 目标描述
        self.is_system = is_system      # 是否为系统目录
        self.recursive = recursive      # 是否递归扫描子目录
        self.enabled = enabled          # 是否启用此目标
```

### 4.2 ScanResult类

```python
class ScanResult:
    def __init__(self, target, files=None, total_size=0, file_count=0):
        self.target = target            # 扫描目标
        self.files = files or []        # 扫描到的文件列表
        self.total_size = total_size    # 文件总大小（字节）
        self.file_count = file_count    # 文件数量
```

### 4.3 CleanTask类

```python
class CleanTask:
    def __init__(self, name, files=None, size=0, target_path=None, enabled=True, is_system=False):
        self.name = name                # 任务名称
        self.files = files or []        # 要清理的文件列表
        self.size = size                # 文件总大小（字节）
        self.target_path = target_path  # 目标路径
        self.enabled = enabled          # 是否启用此任务
        self.is_system = is_system      # 是否为系统目录
        self.success_count = 0          # 成功清理的文件数量
        self.failed_count = 0           # 清理失败的文件数量
        self.cleaned_size = 0           # 已清理的文件大小
```

### 4.4 DiskItem类

```python
class DiskItem:
    def __init__(self, path, name=None, is_dir=False, size=0, parent=None):
        self.path = path                # 路径
        self.name = name or os.path.basename(path) or path  # 名称
        self.is_dir = is_dir            # 是否为目录
        self.size = size                # 大小（字节）
        self.parent = parent            # 父项
        self.children = []              # 子项列表
```

## 5. 接口设计

### 5.1 模块接口

#### 5.1.1 Scanner模块接口

```python
# 创建扫描器实例
scanner = Scanner()

# 添加扫描目标
scanner.add_target(ScanTarget("临时文件", "/tmp", "系统临时文件"))

# 添加常见目标
scanner.add_common_targets()

# 创建扫描过滤器
filter_obj = ScanFilter(min_size=1024, min_age_days=30)

# 开始扫描
def progress_callback(current, total, percent):
    print(f"扫描进度: {percent}%")

def complete_callback(results):
    print(f"扫描完成，发现 {len(results)} 个目标")

scanner.scan(filter_obj, progress_callback, complete_callback)

# 中止扫描
scanner.abort_scan()

# 获取结果摘要
summary = scanner.get_results_summary()
```

#### 5.1.2 Cleaner模块接口

```python
# 创建清理器实例
cleaner = Cleaner(use_safe_delete=True)

# 从扫描结果创建任务
cleaner.from_scan_results(scanner.results, [0, 1, 2])

# 开始清理
def progress_callback(current, total, percent):
    print(f"清理进度: {percent}%")

def complete_callback(results):
    print(f"清理完成，成功: {sum(r.success_count for r in results)}, 失败: {sum(r.failed_count for r in results)}")

cleaner.clean(progress_callback, complete_callback)

# 中止清理
cleaner.abort_clean()

# 获取结果摘要
summary = cleaner.get_results_summary()
```

#### 5.1.3 Analyzer模块接口

```python
# 创建分析器实例
analyzer = Analyzer()

# 开始分析
def progress_callback(current_path, file_count, dir_count):
    print(f"正在分析: {current_path}")

def complete_callback(result):
    print(f"分析完成，文件数: {result.file_count}, 目录数: {result.dir_count}")

analyzer.analyze_disk("C:\\", max_depth=3, progress_callback=progress_callback, complete_callback=complete_callback)

# 中止分析
analyzer.abort_analyze()

# 获取磁盘使用情况
total, used, free, percent = analyzer.get_disk_usage("C:\\")

# 获取所有磁盘
disks = analyzer.get_all_disks()
```

### 5.2 用户界面接口

用户界面通过PyQt5实现，主要包括主窗口和三个功能选项卡：

1. **主窗口（MainWindow）**：程序的主窗口，包含菜单栏、工具栏和状态栏
2. **扫描选项卡（ScanTab）**：用于配置和执行扫描操作
3. **清理选项卡（CleanTab）**：用于查看扫描结果并执行清理操作
4. **分析选项卡（AnalyzeTab）**：用于分析和可视化磁盘空间使用情况

## 6. 异常处理

系统在各个模块中都实现了全面的异常处理机制，主要包括：

1. **文件操作异常**：处理文件不存在、权限不足、IO错误等异常
2. **系统资源访问异常**：处理无法访问系统资源的异常
3. **多线程异常**：确保线程安全，处理线程异常不影响主程序
4. **用户输入异常**：验证和处理用户输入的错误

异常处理采用了以下策略：

- 对于非关键操作，捕获异常并记录日志，允许程序继续运行
- 对于关键操作，捕获异常并提示用户，必要时中止操作
- 使用多层嵌套的try-except结构，确保异常被适当处理

## 7. 安全性考虑

由于垃圾清理涉及文件删除操作，系统实现了多重安全机制：

1. **安全删除模式**：默认使用安全删除（移动到回收站），而非直接删除
2. **系统目录保护**：对系统目录进行特殊标记，清理前要求额外确认
3. **操作确认**：重要操作前要求用户确认
4. **只读模式**：支持只扫描不清理的只读模式，便于用户先检查

## 8. 跨平台适配

系统设计时考虑了跨平台兼容性，主要通过以下方式实现：

1. **路径处理**：使用os.path和pathlib，确保路径在不同系统下正确处理
2. **系统API**：针对Windows、MacOS和Linux系统分别实现相应功能
3. **UI适配**：PyQt5具有良好的跨平台特性，界面在不同系统下保持一致
4. **资源定位**：通过PathUtils定位应用资源，确保在不同系统下正确找到资源文件

## 9. 性能优化

为了提高系统性能，实现了以下优化：

1. **多线程处理**：扫描、清理和分析过程均采用多线程实现，避免界面阻塞
2. **延迟加载**：UI组件和资源采用延迟加载策略，减少启动时间
3. **缓存机制**：对频繁访问的数据实现缓存，减少重复计算
4. **批量处理**：文件操作采用批量处理模式，减少系统调用开销
5. **进度反馈**：长时间操作提供进度反馈，避免用户感觉程序无响应

## 10. 使用说明

### 10.1 启动程序

1. 确保已安装Python 3.7及以上版本
2. 安装依赖库：`pip install -r requirements.txt`
3. 运行主程序：`python main.py`

### 10.2 扫描垃圾文件

1. 在扫描选项卡中，选择要扫描的目标
2. 根据需要配置扫描过滤器（最小文件大小、最小文件年龄等）
3. 点击"开始扫描"按钮
4. 扫描完成后，将显示扫描结果

### 10.3 清理垃圾文件

1. 在清理选项卡中，查看扫描结果列表
2. 勾选需要清理的项目
3. 选择清理模式（安全删除或强制删除）
4. 点击"开始清理"按钮
5. 确认清理操作
6. 清理完成后，将显示清理结果

### 10.4 分析磁盘空间

1. 在分析选项卡中，选择要分析的磁盘或目录
2. 设置分析深度（可选）
3. 点击"开始分析"按钮
4. 分析完成后，将显示磁盘空间使用情况的可视化图表
5. 可查看最大文件、最大目录和文件类型分布等详细信息

## 11. 结束语

电脑垃圾清理器是一个功能完善、界面友好的跨平台工具，能够有效帮助用户清理垃圾文件，优化系统性能。系统采用模块化设计，代码结构清晰，具有良好的可维护性和可扩展性。

---

文档编制：2025年4月23日
版本：1.0.0
