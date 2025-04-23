"""
文件扫描器模块，用于扫描系统中的垃圾文件
"""
import os
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Tuple
import re

from utils.system_utils import SystemUtils

class ScanFilter:
    """扫描过滤器类，定义了文件过滤条件"""
    
    def __init__(self, min_size: int = 0, max_size: Optional[int] = None,
                min_age_days: Optional[int] = None, extensions: List[str] = None,
                exclude_exts: List[str] = None):
        """
        初始化扫描过滤器
        
        参数:
            min_size (int): 最小文件大小(字节)
            max_size (int): 最大文件大小(字节)
            min_age_days (int): 最小文件年龄(天)
            extensions (List[str]): 包含的文件扩展名列表
            exclude_exts (List[str]): 排除的文件扩展名列表
        """
        self.min_size = min_size
        self.max_size = max_size
        self.min_age_days = min_age_days
        self.extensions = extensions or []
        self.exclude_exts = exclude_exts or []
        
    def match_file(self, file_path: str, file_size: int, mod_time: datetime) -> bool:
        """
        检查文件是否符合过滤条件
        
        参数:
            file_path (str): 文件路径
            file_size (int): 文件大小
            mod_time (datetime): 修改时间
            
        返回:
            bool: 是否符合条件
        """
        # 检查文件大小
        if self.min_size > 0 and file_size < self.min_size:
            return False
        if self.max_size and file_size > self.max_size:
            return False
            
        # 检查文件年龄
        if self.min_age_days:
            file_age_days = (datetime.now() - mod_time).days
            if file_age_days < self.min_age_days:
                return False
                
        # 检查文件扩展名
        if self.extensions or self.exclude_exts:
            ext = os.path.splitext(file_path)[1].lower()
            
            # 如果指定了包含的扩展名，则文件扩展名必须在列表中
            if self.extensions and ext not in self.extensions:
                return False
                
            # 如果指定了排除的扩展名，则文件扩展名不能在列表中
            if self.exclude_exts and ext in self.exclude_exts:
                return False
                
        return True

class ScanTarget:
    """扫描目标类，定义了一个扫描区域"""
    
    def __init__(self, name: str, path: str, description: str = None, is_system: bool = False, enabled: bool = True):
        """
        初始化扫描目标
        
        参数:
            name (str): 目标名称
            path (str): 目标路径
            description (str): 目标描述
            is_system (bool): 是否为系统路径
            enabled (bool): 是否启用
        """
        self.name = name
        self.path = path
        self.description = description or path
        self.is_system = is_system
        self.enabled = enabled
        self.patterns = []  # 文件匹配模式列表
        self.exclude_patterns = []  # 排除的文件匹配模式
        self.min_size = 0  # 最小文件大小(字节)
        self.max_size = None  # 最大文件大小(字节)
        self.min_age = None  # 最小文件年龄(天)
        self.recursive = True  # 是否递归扫描子目录
        
    def add_pattern(self, pattern: str):
        """
        添加文件匹配模式
        
        参数:
            pattern (str): 文件匹配模式，支持通配符
        """
        if pattern not in self.patterns:
            self.patterns.append(pattern)
            
    def add_exclude_pattern(self, pattern: str):
        """
        添加要排除的文件匹配模式
        
        参数:
            pattern (str): 文件匹配模式，支持通配符
        """
        if pattern not in self.exclude_patterns:
            self.exclude_patterns.append(pattern)
            
    def set_size_filter(self, min_size: int = 0, max_size: Optional[int] = None):
        """
        设置文件大小过滤条件
        
        参数:
            min_size (int): 最小文件大小(字节)
            max_size (int): 最大文件大小(字节)
        """
        self.min_size = min_size
        self.max_size = max_size
        
    def set_age_filter(self, min_age: Optional[int] = None):
        """
        设置文件年龄过滤条件
        
        参数:
            min_age (int): 最小文件年龄(天)
        """
        self.min_age = min_age
        
    def set_recursive(self, recursive: bool):
        """
        设置是否递归扫描子目录
        
        参数:
            recursive (bool): 是否递归扫描
        """
        self.recursive = recursive
        
    def __str__(self):
        return f"{self.name} ({self.path})"

class ScanResult:
    """扫描结果类，保存扫描操作的结果信息"""
    
    def __init__(self, target: ScanTarget):
        """
        初始化扫描结果
        
        参数:
            target (ScanTarget): 扫描目标
        """
        self.target = target
        self.files = []  # 找到的文件列表
        self.file_types = {}  # 文件类型统计
        self.total_size = 0  # 文件总大小
        self.start_time = None
        self.end_time = None
        self.file_info = {}  # 文件信息字典 {文件路径: {大小, 类型, 修改时间}}
        
    def start(self):
        """开始记录扫描时间"""
        self.start_time = datetime.now()
        
    def end(self):
        """结束记录扫描时间"""
        self.end_time = datetime.now()
        
    def add_file(self, file_path: str, file_size: int, file_type: str, mod_time: datetime):
        """
        添加找到的文件
        
        参数:
            file_path (str): 文件路径
            file_size (int): 文件大小
            file_type (str): 文件类型
            mod_time (datetime): 修改时间
        """
        self.files.append(file_path)
        self.total_size += file_size
        
        # 更新文件类型统计
        if file_type in self.file_types:
            self.file_types[file_type]['count'] += 1
            self.file_types[file_type]['size'] += file_size
        else:
            self.file_types[file_type] = {'count': 1, 'size': file_size}
            
        # 保存文件信息
        self.file_info[file_path] = {
            'size': file_size,
            'type': file_type,
            'mod_time': mod_time
        }
        
    def get_file_count(self) -> int:
        """
        获取找到的文件数量
        
        返回:
            int: 文件数量
        """
        return len(self.files)
        
    def get_formatted_size(self) -> str:
        """
        获取格式化的文件总大小
        
        返回:
            str: 格式化后的大小字符串
        """
        return SystemUtils.format_size(self.total_size)
        
    def get_duration(self) -> float:
        """
        获取扫描持续时间（秒）
        
        返回:
            float: 扫描持续时间（秒）
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
        
    def __str__(self):
        return (
            f"{self.target.name}: 找到 {len(self.files)} 个文件，"
            f"共 {self.get_formatted_size()}，"
            f"耗时 {self.get_duration():.2f} 秒"
        )

class Scanner:
    """文件扫描器，用于扫描系统中的垃圾文件"""
    
    # 预定义的常用垃圾文件类型
    TEMP_FILE_PATTERNS = ['*.tmp', '*.temp', '~*', '*.bak', '*.old', '*.swp']
    LOG_FILE_PATTERNS = ['*.log', '*.log.*', '*.trace']
    CACHE_FILE_PATTERNS = ['thumbs.db', '.DS_Store', '*.cache']
    
    def __init__(self):
        """初始化扫描器"""
        self.targets = []  # 扫描目标列表
        self.results = []  # 扫描结果列表
        self.running = False
        self.scan_thread = None
        self.abort_flag = False
        
    def add_target(self, target: ScanTarget):
        """
        添加扫描目标
        
        参数:
            target (ScanTarget): 扫描目标
        """
        self.targets.append(target)
        
    def remove_target(self, target_index: int):
        """
        移除扫描目标
        
        参数:
            target_index (int): 目标索引
        """
        if 0 <= target_index < len(self.targets):
            del self.targets[target_index]
            
    def clear_targets(self):
        """清除所有扫描目标"""
        self.targets = []
        
    def add_temp_files_target(self, enabled: bool = True):
        """
        添加临时文件扫描目标
        
        参数:
            enabled (bool): 是否启用
        """
        # 获取系统临时目录
        temp_dir = SystemUtils.get_temp_dir()
        target = ScanTarget("临时文件", temp_dir, "系统临时文件目录", is_system=True, enabled=enabled)
        
        # 添加临时文件模式
        for pattern in self.TEMP_FILE_PATTERNS:
            target.add_pattern(pattern)
            
        # 设置最小文件年龄为1天
        target.set_age_filter(1)
        
        self.add_target(target)
        return target
        
    def add_log_files_target(self, enabled: bool = True):
        """
        添加日志文件扫描目标
        
        参数:
            enabled (bool): 是否启用
        """
        # 多个日志目录
        log_dirs = SystemUtils.get_log_dirs()
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                dir_name = os.path.basename(log_dir)
                description = f"系统日志文件目录: {log_dir}"
                target = ScanTarget(f"日志文件 ({dir_name})", 
                                   log_dir, 
                                   description,
                                   is_system=True, 
                                   enabled=enabled)
                
                # 添加日志文件模式
                for pattern in self.LOG_FILE_PATTERNS:
                    target.add_pattern(pattern)
                    
                # 设置最小文件年龄为7天
                target.set_age_filter(7)
                
                self.add_target(target)
                
    def add_browser_cache_target(self, enabled: bool = True):
        """
        添加浏览器缓存扫描目标
        
        参数:
            enabled (bool): 是否启用
        """
        # 获取浏览器缓存目录
        cache_dirs = SystemUtils.get_browser_cache_directories()
        
        # 为每个缓存目录创建一个目标
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                browser_name = os.path.basename(os.path.dirname(cache_dir))
                description = f"浏览器缓存目录: {cache_dir}"
                target = ScanTarget(f"{browser_name} 缓存", 
                                   cache_dir, 
                                   description,
                                   is_system=False, 
                                   enabled=enabled)
                
                # 添加缓存文件模式 (所有文件)
                target.add_pattern("*")
                
                # 排除重要文件
                target.add_exclude_pattern("*.ini")
                target.add_exclude_pattern("*.dat")
                
                self.add_target(target)
                
    def add_recycle_bin_target(self, enabled: bool = True):
        """
        添加回收站扫描目标
        
        参数:
            enabled (bool): 是否启用
        """
        # 获取回收站目录
        recycle_bin = SystemUtils.get_recycle_bin_path()
        
        if recycle_bin and os.path.exists(recycle_bin):
            description = "系统回收站目录"
            target = ScanTarget("回收站", 
                                recycle_bin, 
                                description,
                                is_system=True, 
                                enabled=enabled)
            
            # 添加所有文件
            target.add_pattern("*")
            
            # 设置最小文件年龄为7天
            target.set_age_filter(7)
            
            self.add_target(target)
    
    def add_custom_target(self, name: str, path: str, patterns: List[str] = None, 
                        min_age: Optional[int] = None, min_size: int = 0,
                        description: str = None, enabled: bool = True):
        """
        添加自定义扫描目标
        
        参数:
            name (str): 目标名称
            path (str): 目标路径
            patterns (List[str]): 文件匹配模式列表
            min_age (int): 最小文件年龄(天)
            min_size (int): 最小文件大小(字节)
            description (str): 目标描述
            enabled (bool): 是否启用
        """
        if os.path.exists(path):
            description = description or f"用户选择的目录: {path}"
            target = ScanTarget(name, path, description, is_system=False, enabled=enabled)
            
            if patterns:
                for pattern in patterns:
                    target.add_pattern(pattern)
            else:
                # 默认添加所有文件
                target.add_pattern("*")
                
            if min_age is not None:
                target.set_age_filter(min_age)
                
            if min_size > 0:
                target.set_size_filter(min_size)
                
            self.add_target(target)
            return target
        
        return None
        
    def scan(self, filter_obj: Optional[ScanFilter] = None,
            progress_callback: Callable[[int, int, int], None] = None, 
            complete_callback: Callable[[List[ScanResult]], None] = None):
        """
        开始扫描，在新线程中执行
        
        参数:
            filter_obj (ScanFilter): 全局过滤器对象
            progress_callback (callable): 进度回调函数，参数为(当前进度, 总进度, 百分比)
            complete_callback (callable): 完成回调函数，参数为扫描结果列表
        """
        if self.running:
            return False
            
        # 开始扫描线程
        self.abort_flag = False
        self.running = True
        self.scan_thread = threading.Thread(
            target=self._scan_thread,
            args=(filter_obj, progress_callback, complete_callback)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        return True
        
    def _scan_thread(self, filter_obj: Optional[ScanFilter],
                   progress_callback: Callable = None, 
                   complete_callback: Callable = None):
        """
        扫描线程函数
        
        参数:
            filter_obj (ScanFilter): 全局过滤器对象
            progress_callback (callable): 进度回调函数
            complete_callback (callable): 完成回调函数
        """
        self.results = []
        enabled_targets = [t for t in self.targets if t.enabled]
        total_targets = len(enabled_targets)
        current = 0
        
        for target in enabled_targets:
            if self.abort_flag:
                break
                
            # 更新进度
            current += 1
            progress_percent = int((current - 0.5) * 100 / total_targets)
            
            if progress_callback:
                progress_callback(current - 1, total_targets, progress_percent)
                
            # 扫描目标
            result = self._scan_target(target, filter_obj)
            self.results.append(result)
            
            # 更新进度
            progress_percent = int(current * 100 / total_targets)
            
            if progress_callback:
                progress_callback(current, total_targets, progress_percent)
                
            # 添加小延时，避免占用过多资源
            time.sleep(0.1)
            
        # 完成回调
        self.running = False
        
        if complete_callback:
            complete_callback(self.results)
            
    def _scan_target(self, target: ScanTarget, filter_obj: Optional[ScanFilter]) -> ScanResult:
        """
        扫描单个目标
        
        参数:
            target (ScanTarget): 扫描目标
            filter_obj (ScanFilter): 全局过滤器对象
            
        返回:
            ScanResult: 扫描结果
        """
        result = ScanResult(target)
        result.start()
        
        try:
            if os.path.exists(target.path):
                # 扫描目录
                self._scan_directory(target, target.path, result, filter_obj)
        except Exception as e:
            print(f"扫描目标 {target.name} 时出错: {str(e)}")
            
        result.end()
        return result
        
    def _scan_directory(self, target: ScanTarget, directory: str, result: ScanResult, filter_obj: Optional[ScanFilter]):
        """
        扫描目录
        
        参数:
            target (ScanTarget): 扫描目标
            directory (str): 要扫描的目录
            result (ScanResult): 扫描结果
            filter_obj (ScanFilter): 全局过滤器对象
        """
        try:
            # 获取目录内容
            items = os.listdir(directory)
            
            for item in items:
                if self.abort_flag:
                    break
                    
                item_path = os.path.join(directory, item)
                
                try:
                    # 处理文件
                    if os.path.isfile(item_path):
                        self._process_file(target, item_path, result, filter_obj)
                    # 处理目录（递归）
                    elif os.path.isdir(item_path) and target.recursive:
                        self._scan_directory(target, item_path, result, filter_obj)
                except (PermissionError, OSError):
                    # 忽略无权限文件/目录
                    pass
                    
        except (PermissionError, OSError):
            # 忽略无权限目录
            pass
            
    def _process_file(self, target: ScanTarget, file_path: str, result: ScanResult, filter_obj: Optional[ScanFilter]):
        """
        处理单个文件
        
        参数:
            target (ScanTarget): 扫描目标
            file_path (str): 文件路径
            result (ScanResult): 扫描结果
            filter_obj (ScanFilter): 全局过滤器对象
        """
        # 检查是否匹配文件模式
        filename = os.path.basename(file_path)
        
        # 如果没有指定模式，默认匹配所有文件
        if not target.patterns:
            is_match = True
        else:
            is_match = any(self._match_pattern(filename, pattern) for pattern in target.patterns)
            
        # 检查是否应该排除
        if target.exclude_patterns:
            is_excluded = any(self._match_pattern(filename, pattern) for pattern in target.exclude_patterns)
            if is_excluded:
                return
                
        if is_match:
            try:
                # 获取文件信息
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                # 检查文件大小
                if filter_obj and not filter_obj.match_file(file_path, file_size, mod_time):
                    return
                    
                # 检查文件年龄
                if target.min_age:
                    file_age_days = (datetime.now() - mod_time).days
                    if file_age_days < target.min_age:
                        return
                        
                # 获取文件类型
                file_ext = os.path.splitext(filename)[1].lower()
                if not file_ext:
                    file_type = "无扩展名"
                else:
                    file_type = file_ext[1:]  # 去掉点号
                    
                # 添加到结果
                result.add_file(file_path, file_size, file_type, mod_time)
                
            except (PermissionError, OSError, FileNotFoundError):
                # 忽略无法访问的文件
                pass
                
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        检查文件名是否匹配模式
        
        参数:
            filename (str): 文件名
            pattern (str): 匹配模式（支持通配符）
            
        返回:
            bool: 是否匹配
        """
        # 将通配符模式转换为正则表达式
        regex_pattern = pattern.replace('.', '\\.')
        regex_pattern = regex_pattern.replace('*', '.*')
        regex_pattern = regex_pattern.replace('?', '.')
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, filename, re.IGNORECASE))
        
    def abort_scan(self):
        """中止当前扫描操作"""
        if self.running:
            self.abort_flag = True
            
    def is_running(self) -> bool:
        """
        检查是否正在扫描
        
        返回:
            bool: 是否正在扫描
        """
        return self.running
        
    def get_results_summary(self) -> Dict[str, Any]:
        """
        获取扫描结果摘要
        
        返回:
            dict: 包含文件数量、总大小和扫描时间的字典
        """
        total_files = sum(result.get_file_count() for result in self.results)
        total_size = sum(result.total_size for result in self.results)
        total_time = sum(result.get_duration() for result in self.results)
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'formatted_size': SystemUtils.format_size(total_size),
            'total_time': total_time
        }
        
    def get_file_types_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        获取文件类型统计摘要
        
        返回:
            dict: 文件类型统计信息
        """
        types_summary = {}
        
        for result in self.results:
            for file_type, info in result.file_types.items():
                if file_type in types_summary:
                    types_summary[file_type]['count'] += info['count']
                    types_summary[file_type]['size'] += info['size']
                else:
                    types_summary[file_type] = {
                        'count': info['count'],
                        'size': info['size']
                    }
                    
        # 添加格式化大小
        for file_type, info in types_summary.items():
            info['formatted_size'] = SystemUtils.format_size(info['size'])
            
        return types_summary

    def add_common_targets(self):
        """添加常见的扫描目标"""
        # 添加临时文件目标
        self.add_temp_files_target()
        
        # 添加日志文件目标
        self.add_log_files_target()
        
        # 添加浏览器缓存目标
        self.add_browser_cache_target()
        
        # 添加回收站目标
        self.add_recycle_bin_target()