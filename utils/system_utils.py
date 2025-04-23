"""
系统工具模块，提供与操作系统相关的功能
"""
import os
import platform
import sys
import psutil
import tempfile
import shutil
from pathlib import Path

class SystemUtils:
    """系统工具类，提供获取系统信息和系统路径的方法"""
    
    @staticmethod
    def get_system_type():
        """
        获取当前操作系统类型
        
        返回值:
            str: 'windows', 'darwin' (MacOS), 'linux' 中的一个
        """
        return platform.system().lower()
    
    @staticmethod
    def is_windows():
        """
        检查当前系统是否为Windows
        
        返回值:
            bool: 是Windows则返回True，否则返回False
        """
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_macos():
        """
        检查当前系统是否为MacOS
        
        返回值:
            bool: 是MacOS则返回True，否则返回False
        """
        return platform.system().lower() == 'darwin'
    
    @staticmethod
    def is_linux():
        """
        检查当前系统是否为Linux
        
        返回值:
            bool: 是Linux则返回True，否则返回False
        """
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def get_temp_directories():
        """
        获取系统的临时目录列表
        
        返回值:
            list: 临时目录路径列表
        """
        temp_dirs = []
        
        # 添加系统临时目录
        temp_dirs.append(tempfile.gettempdir())
        
        # 根据不同系统添加特定的临时目录
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows临时目录
            temp_dirs.append(os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Temp'))
            temp_dirs.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'))
            
        elif system == 'darwin':
            # MacOS临时目录
            temp_dirs.append('/private/tmp')
            temp_dirs.append('/private/var/tmp')
            temp_dirs.append(os.path.expanduser('~/Library/Caches'))
            
        elif system == 'linux':
            # Linux临时目录
            temp_dirs.append('/tmp')
            temp_dirs.append('/var/tmp')
            temp_dirs.append(os.path.expanduser('~/.cache'))
            
        # 过滤掉不存在的目录
        return [d for d in temp_dirs if os.path.exists(d)]
    
    @staticmethod
    def get_downloads_directory():
        """
        获取下载目录的路径
        
        返回值:
            str: 下载目录的路径
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        elif system == 'darwin':
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        elif system == 'linux':
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            return os.path.expanduser('~')
    
    @staticmethod
    def get_browser_cache_directories():
        """
        获取常见浏览器缓存目录列表
        
        返回值:
            list: 浏览器缓存目录路径列表
        """
        cache_dirs = []
        home = os.path.expanduser('~')
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows浏览器缓存目录
            appdata = os.environ.get('LOCALAPPDATA', '')
            cache_dirs.extend([
                # Chrome
                os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                # Firefox
                os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
                # Edge
                os.path.join(appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
            ])
            
        elif system == 'darwin':
            # MacOS浏览器缓存目录
            cache_dirs.extend([
                # Chrome
                os.path.join(home, 'Library', 'Caches', 'Google', 'Chrome'),
                # Firefox
                os.path.join(home, 'Library', 'Caches', 'Firefox'),
                # Safari
                os.path.join(home, 'Library', 'Caches', 'com.apple.Safari'),
            ])
            
        elif system == 'linux':
            # Linux浏览器缓存目录
            cache_dirs.extend([
                # Chrome
                os.path.join(home, '.cache', 'google-chrome'),
                # Firefox
                os.path.join(home, '.mozilla', 'firefox'),
            ])
            
        # 过滤掉不存在的目录
        return [d for d in cache_dirs if os.path.exists(d)]
    
    @staticmethod
    def get_disk_usage(path=None):
        """
        获取指定路径的磁盘使用情况
        
        参数:
            path (str): 要查询的路径，默认为根目录
            
        返回值:
            tuple: (总空间, 已用空间, 可用空间) 单位为字节
        """
        if path is None:
            if SystemUtils.is_windows():
                path = 'C:\\'
            else:
                path = '/'
                
        return shutil.disk_usage(path)
    
    @staticmethod
    def format_size(size_bytes):
        """
        将字节大小转换为人类可读的格式
        
        参数:
            size_bytes (int): 字节大小
            
        返回值:
            str: 格式化后的大小字符串 (例如: "1.23 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def get_process_list():
        """
        获取当前运行的进程列表
        
        返回值:
            list: 进程信息列表，每个元素为一个字典，包含进程ID、名称和内存使用量
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                process_info = proc.info
                processes.append({
                    'pid': process_info['pid'],
                    'name': process_info['name'],
                    'memory': process_info['memory_info'].rss if process_info['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    
    @staticmethod
    def get_temp_dir():
        """
        获取系统主临时目录
        
        返回值:
            str: 临时目录路径
        """
        return tempfile.gettempdir()
        
    @staticmethod
    def get_log_dirs():
        """
        获取系统日志目录列表
        
        返回值:
            list: 日志目录路径列表
        """
        log_dirs = []
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows日志目录
            log_dirs.append(os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Logs'))
            log_dirs.append(os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'debug'))
        elif system == 'darwin':
            # MacOS日志目录
            log_dirs.append('/var/log')
            log_dirs.append(os.path.expanduser('~/Library/Logs'))
        elif system == 'linux':
            # Linux日志目录
            log_dirs.append('/var/log')
            
        # 过滤掉不存在的目录
        return [d for d in log_dirs if os.path.exists(d)]
        
    @staticmethod
    def get_recycle_bin_path():
        """
        获取回收站路径
        
        返回值:
            str: 回收站路径，不存在则返回None
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows回收站
            return os.path.join(os.environ.get('SYSTEMDRIVE', 'C:'), '$Recycle.Bin')
        elif system == 'darwin':
            # MacOS回收站
            return os.path.join(os.path.expanduser('~'), '.Trash')
        elif system == 'linux':
            # Linux回收站
            return os.path.join(os.path.expanduser('~'), '.local', 'share', 'Trash')
            
        return None 