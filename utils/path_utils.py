"""
路径工具模块，提供路径处理相关的功能
"""
import os
import sys
from pathlib import Path
from utils.system_utils import SystemUtils

class PathUtils:
    """路径工具类，提供路径处理的方法"""
    
    @staticmethod
    def normalize_path(path):
        """
        规范化路径，使其在不同系统中保持一致
        
        参数:
            path (str): 原始路径
            
        返回值:
            str: 规范化后的路径
        """
        if path:
            return os.path.normpath(os.path.expanduser(str(path)))
        return path
    
    @staticmethod
    def get_user_home_dir():
        """
        获取用户主目录路径
        
        返回值:
            str: 用户主目录路径
        """
        return os.path.expanduser('~')
    
    @staticmethod
    def get_app_data_dir(app_name='PCGarbageCleaner'):
        """
        获取应用程序数据目录
        
        参数:
            app_name (str): 应用程序名称
            
        返回值:
            str: 应用程序数据目录路径
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows: %APPDATA%/AppName
            base_dir = os.environ.get('APPDATA', '')
            if not base_dir:
                base_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')
        elif system == 'darwin':
            # MacOS: ~/Library/Application Support/AppName
            base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
        else:
            # Linux: ~/.local/share/AppName
            base_dir = os.path.join(os.path.expanduser('~'), '.local', 'share')
            
        app_dir = os.path.join(base_dir, app_name)
        
        # 确保目录存在
        os.makedirs(app_dir, exist_ok=True)
        
        return app_dir
    
    @staticmethod
    def get_app_config_dir(app_name='PCGarbageCleaner'):
        """
        获取应用程序配置目录
        
        参数:
            app_name (str): 应用程序名称
            
        返回值:
            str: 应用程序配置目录路径
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows: %LOCALAPPDATA%/AppName
            base_dir = os.environ.get('LOCALAPPDATA', '')
            if not base_dir:
                base_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
        elif system == 'darwin':
            # MacOS: ~/Library/Preferences/AppName
            base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Preferences')
        else:
            # Linux: ~/.config/AppName
            base_dir = os.path.join(os.path.expanduser('~'), '.config')
            
        config_dir = os.path.join(base_dir, app_name)
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        return config_dir
    
    @staticmethod
    def get_app_cache_dir(app_name='PCGarbageCleaner'):
        """
        获取应用程序缓存目录
        
        参数:
            app_name (str): 应用程序名称
            
        返回值:
            str: 应用程序缓存目录路径
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows: %LOCALAPPDATA%/AppName/Cache
            base_dir = os.environ.get('LOCALAPPDATA', '')
            if not base_dir:
                base_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
            cache_dir = os.path.join(base_dir, app_name, 'Cache')
        elif system == 'darwin':
            # MacOS: ~/Library/Caches/AppName
            base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Caches')
            cache_dir = os.path.join(base_dir, app_name)
        else:
            # Linux: ~/.cache/AppName
            base_dir = os.path.join(os.path.expanduser('~'), '.cache')
            cache_dir = os.path.join(base_dir, app_name)
            
        # 确保目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        return cache_dir
    
    @staticmethod
    def get_app_logs_dir(app_name='PCGarbageCleaner'):
        """
        获取应用程序日志目录
        
        参数:
            app_name (str): 应用程序名称
            
        返回值:
            str: 应用程序日志目录路径
        """
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows: %LOCALAPPDATA%/AppName/Logs
            base_dir = os.environ.get('LOCALAPPDATA', '')
            if not base_dir:
                base_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
            logs_dir = os.path.join(base_dir, app_name, 'Logs')
        elif system == 'darwin':
            # MacOS: ~/Library/Logs/AppName
            base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Logs')
            logs_dir = os.path.join(base_dir, app_name)
        else:
            # Linux: ~/.local/share/AppName/logs
            base_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', app_name)
            logs_dir = os.path.join(base_dir, 'logs')
            
        # 确保目录存在
        os.makedirs(logs_dir, exist_ok=True)
        
        return logs_dir
        
    @staticmethod
    def get_relative_path(path, base_path):
        """
        获取相对路径
        
        参数:
            path (str): 原始路径
            base_path (str): 基准路径
            
        返回值:
            str: 相对路径
        """
        try:
            return os.path.relpath(path, base_path)
        except ValueError:
            return path
    
    @staticmethod
    def get_common_system_dirs():
        """
        获取常见的系统目录列表
        
        返回值:
            list: 系统目录路径列表
        """
        system_dirs = []
        system = SystemUtils.get_system_type()
        
        if system == 'windows':
            # Windows系统目录
            windows_dir = os.environ.get('WINDIR', 'C:\\Windows')
            system_dirs.extend([
                windows_dir,
                os.path.join(windows_dir, 'System32'),
                os.path.join(windows_dir, 'SysWOW64'),
                os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
            ])
        elif system == 'darwin':
            # MacOS系统目录
            system_dirs.extend([
                '/System',
                '/Library',
                '/Applications',
                '/usr/bin',
                '/usr/lib',
                '/usr/local'
            ])
        elif system == 'linux':
            # Linux系统目录
            system_dirs.extend([
                '/bin',
                '/usr/bin',
                '/sbin',
                '/usr/sbin',
                '/lib',
                '/usr/lib',
                '/usr/local',
                '/opt'
            ])
            
        return [d for d in system_dirs if os.path.exists(d)]
    
    @staticmethod
    def is_system_directory(path):
        """
        检查指定路径是否为系统目录
        
        参数:
            path (str): 目录路径
            
        返回值:
            bool: 是系统目录则返回True，否则返回False
        """
        # 规范化路径
        path = PathUtils.normalize_path(path)
        
        # 获取系统目录列表
        system_dirs = PathUtils.get_common_system_dirs()
        
        # 检查路径是否是系统目录或其子目录
        for sys_dir in system_dirs:
            if path == sys_dir or path.startswith(sys_dir + os.sep):
                return True
                
        return False 