"""
磁盘分析器模块，用于分析磁盘使用情况
"""
import os
import threading
from collections import defaultdict
from utils.system_utils import SystemUtils
from utils.file_utils import FileUtils
from utils.path_utils import PathUtils

class DiskItem:
    """磁盘项类，表示一个文件或目录"""
    
    def __init__(self, path, name=None, is_dir=False, size=0, parent=None):
        """
        初始化磁盘项
        
        参数:
            path (str): 路径
            name (str): 名称
            is_dir (bool): 是否为目录
            size (int): 大小（字节）
            parent (DiskItem): 父项
        """
        self.path = path
        self.name = name or os.path.basename(path) or path
        self.is_dir = is_dir
        self.size = size
        self.parent = parent
        self.children = []
        
    def add_child(self, child):
        """
        添加子项
        
        参数:
            child (DiskItem): 子项
        """
        self.children.append(child)
        child.parent = self
        
    def get_formatted_size(self):
        """
        获取格式化的大小字符串
        
        返回值:
            str: 格式化后的大小字符串
        """
        return SystemUtils.format_size(self.size)
        
    def __str__(self):
        return f"{self.name} ({'目录' if self.is_dir else '文件'}, {self.get_formatted_size()})"

class AnalyzeResult:
    """分析结果类，包含磁盘分析的结果"""
    
    def __init__(self, root_item=None):
        """
        初始化分析结果
        
        参数:
            root_item (DiskItem): 根项
        """
        self.root_item = root_item
        self.file_count = 0
        self.dir_count = 0
        self.total_size = 0
        self.file_types = defaultdict(int)  # 扩展名 -> 大小
        self.largest_files = []  # 最大的文件列表
        self.largest_dirs = []  # 最大的目录列表
        
    def add_file(self, path, size):
        """
        添加文件到结果
        
        参数:
            path (str): 文件路径
            size (int): 文件大小
        """
        self.file_count += 1
        self.total_size += size
        
        # 更新文件类型统计
        _, ext = os.path.splitext(path)
        ext = ext.lower() if ext else '(无扩展名)'
        self.file_types[ext] += size
        
        # 更新最大文件列表
        self._update_largest_files(path, size)
        
    def add_dir(self, path, size):
        """
        添加目录到结果
        
        参数:
            path (str): 目录路径
            size (int): 目录大小
        """
        self.dir_count += 1
        
        # 更新最大目录列表
        self._update_largest_dirs(path, size)
        
    def _update_largest_files(self, path, size, max_count=20):
        """
        更新最大文件列表
        
        参数:
            path (str): 文件路径
            size (int): 文件大小
            max_count (int): 最大保留数量
        """
        self.largest_files.append((path, size))
        self.largest_files.sort(key=lambda x: x[1], reverse=True)
        if len(self.largest_files) > max_count:
            self.largest_files = self.largest_files[:max_count]
            
    def _update_largest_dirs(self, path, size, max_count=20):
        """
        更新最大目录列表
        
        参数:
            path (str): 目录路径
            size (int): 目录大小
            max_count (int): 最大保留数量
        """
        self.largest_dirs.append((path, size))
        self.largest_dirs.sort(key=lambda x: x[1], reverse=True)
        if len(self.largest_dirs) > max_count:
            self.largest_dirs = self.largest_dirs[:max_count]
            
    def get_formatted_total_size(self):
        """
        获取格式化的总大小字符串
        
        返回值:
            str: 格式化后的大小字符串
        """
        return SystemUtils.format_size(self.total_size)
        
    def get_file_types_summary(self):
        """
        获取文件类型摘要
        
        返回值:
            list: 包含文件类型、大小和百分比的列表
        """
        result = []
        
        for ext, size in sorted(self.file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = size / max(self.total_size, 1) * 100
            result.append({
                'extension': ext,
                'size': size,
                'formatted_size': SystemUtils.format_size(size),
                'percentage': percentage
            })
            
        return result
        
    def get_largest_files_summary(self):
        """
        获取最大文件摘要
        
        返回值:
            list: 包含文件路径、大小和百分比的列表
        """
        result = []
        
        for path, size in self.largest_files:
            percentage = size / max(self.total_size, 1) * 100
            result.append({
                'path': path,
                'name': os.path.basename(path),
                'size': size,
                'formatted_size': SystemUtils.format_size(size),
                'percentage': percentage
            })
            
        return result
        
    def get_largest_dirs_summary(self):
        """
        获取最大目录摘要
        
        返回值:
            list: 包含目录路径、大小和百分比的列表
        """
        result = []
        
        for path, size in self.largest_dirs:
            percentage = size / max(self.total_size, 1) * 100
            result.append({
                'path': path,
                'name': os.path.basename(path) or path,
                'size': size,
                'formatted_size': SystemUtils.format_size(size),
                'percentage': percentage
            })
            
        return result

class Analyzer:
    """磁盘分析器，用于分析磁盘使用情况"""
    
    def __init__(self):
        """初始化分析器"""
        self.result = None
        self.is_analyzing = False
        self.analyze_thread = None
        self.analyze_progress_callback = None
        self.analyze_complete_callback = None
        self.aborted = False
        
    def analyze_disk(self, path, max_depth=None, progress_callback=None, complete_callback=None):
        """
        分析磁盘，在新线程中执行
        
        参数:
            path (str): 要分析的路径
            max_depth (int): 最大分析深度
            progress_callback (callable): 进度回调函数
            complete_callback (callable): 完成回调函数
        """
        if self.is_analyzing:
            return
            
        path = PathUtils.normalize_path(path)
        
        self.analyze_progress_callback = progress_callback
        self.analyze_complete_callback = complete_callback
        self.aborted = False
        
        self.analyze_thread = threading.Thread(
            target=self._analyze_thread,
            args=(path, max_depth)
        )
        self.analyze_thread.daemon = True
        self.analyze_thread.start()
        
    def abort_analyze(self):
        """中止分析过程"""
        self.aborted = True
        
    def _analyze_thread(self, path, max_depth=None):
        """
        分析线程的实现
        
        参数:
            path (str): 要分析的路径
            max_depth (int): 最大分析深度
        """
        self.is_analyzing = True
        self.result = AnalyzeResult()
        
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    # 创建根目录项
                    root_item = DiskItem(path, is_dir=True)
                    self.result.root_item = root_item
                    
                    # 分析目录
                    self._analyze_directory(path, root_item, 0, max_depth)
                else:
                    # 单个文件
                    file_size = FileUtils.get_file_size(path)
                    root_item = DiskItem(path, is_dir=False, size=file_size)
                    self.result.root_item = root_item
                    self.result.add_file(path, file_size)
        finally:
            self.is_analyzing = False
            if self.analyze_complete_callback:
                self.analyze_complete_callback(self.result)
                
    def _analyze_directory(self, directory, parent_item, current_depth, max_depth):
        """
        分析目录
        
        参数:
            directory (str): 目录路径
            parent_item (DiskItem): 父项
            current_depth (int): 当前深度
            max_depth (int): 最大深度
        """
        if self.aborted:
            return
            
        if max_depth is not None and current_depth > max_depth:
            return
            
        try:
            dir_size = 0
            
            for item in os.scandir(directory):
                if self.aborted:
                    return
                    
                try:
                    if item.is_file():
                        # 文件
                        file_size = FileUtils.get_file_size(item.path)
                        dir_size += file_size
                        
                        # 创建文件项
                        file_item = DiskItem(item.path, name=item.name, is_dir=False, size=file_size)
                        parent_item.add_child(file_item)
                        
                        # 更新分析结果
                        self.result.add_file(item.path, file_size)
                        
                        # 更新进度
                        self._update_progress(item.path)
                        
                    elif item.is_dir():
                        # 子目录，递归分析
                        dir_item = DiskItem(item.path, name=item.name, is_dir=True)
                        parent_item.add_child(dir_item)
                        
                        self._analyze_directory(item.path, dir_item, current_depth + 1, max_depth)
                        
                        # 更新目录大小
                        dir_size += dir_item.size
                except PermissionError:
                    # 跳过没有权限的项
                    pass
                except Exception as e:
                    # 记录异常但继续分析
                    print(f"分析 {item.path} 时发生错误: {e}")
                    
            # 更新父目录大小
            parent_item.size = dir_size
            
            # 更新分析结果
            self.result.add_dir(directory, dir_size)
            
        except PermissionError:
            # 跳过没有权限的目录
            pass
        except Exception as e:
            # 记录异常但继续分析
            print(f"分析目录 {directory} 时发生错误: {e}")
            
    def _update_progress(self, current_path):
        """
        更新分析进度并调用回调函数
        
        参数:
            current_path (str): 当前正在分析的路径
        """
        if self.analyze_progress_callback:
            self.analyze_progress_callback(current_path, self.result.file_count, self.result.dir_count)
            
    def get_disk_usage(self, path=None):
        """
        获取磁盘使用情况
        
        参数:
            path (str): 路径，默认为系统根目录
            
        返回值:
            tuple: (总大小, 已用大小, 可用大小, 使用百分比)
        """
        if path is None:
            if SystemUtils.is_windows():
                path = 'C:\\'
            else:
                path = '/'
                
        total, used, free = SystemUtils.get_disk_usage(path)
        percent = used / total * 100 if total > 0 else 0
        
        return (total, used, free, percent)
        
    def get_all_disks(self):
        """
        获取所有磁盘列表
        
        返回值:
            list: 磁盘信息列表
        """
        disks = []
        
        if SystemUtils.is_windows():
            # Windows: 获取所有驱动器
            import string
            import ctypes
            
            drives = []
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter + ':\\')
                bitmask >>= 1
                
            for drive in drives:
                try:
                    total, used, free, percent = self.get_disk_usage(drive)
                    disks.append({
                        'path': drive,
                        'name': drive,
                        'total': total,
                        'used': used,
                        'free': free,
                        'percent': percent,
                        'formatted_total': SystemUtils.format_size(total),
                        'formatted_used': SystemUtils.format_size(used),
                        'formatted_free': SystemUtils.format_size(free)
                    })
                except:
                    # 跳过无法访问的驱动器
                    pass
                    
        elif SystemUtils.is_macos() or SystemUtils.is_linux():
            # MacOS/Linux: 获取挂载点
            import psutil
            
            for part in psutil.disk_partitions(all=False):
                if part.fstype and (SystemUtils.is_macos() or 'loop' not in part.device):
                    try:
                        total, used, free, percent = self.get_disk_usage(part.mountpoint)
                        disks.append({
                            'path': part.mountpoint,
                            'name': part.device,
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': percent,
                            'formatted_total': SystemUtils.format_size(total),
                            'formatted_used': SystemUtils.format_size(used),
                            'formatted_free': SystemUtils.format_size(free)
                        })
                    except:
                        # 跳过无法访问的挂载点
                        pass
                        
        return disks 