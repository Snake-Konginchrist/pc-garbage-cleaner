"""
清理器核心模块，用于处理文件清理操作
"""
import os
import threading
import time
import shutil
from datetime import datetime
import shutil
from enum import Enum
from typing import List, Callable, Optional, Dict, Any
from send2trash import send2trash

from utils.file_utils import FileUtils
from utils.system_utils import SystemUtils

class CleanTask:
    """清理任务类，表示要清理的单个文件"""
    
    def __init__(self, file_path: str, metadata: Dict[str, Any] = None):
        """
        初始化清理任务
        
        参数:
            file_path (str): 文件路径
            metadata (dict): 额外的元数据信息
        """
        self.file_path = file_path
        self.metadata = metadata or {}
        
        # 尝试获取文件大小
        try:
            self.size = os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            self.size = 0

class CleanResult:
    """清理结果类，表示单个文件的清理结果"""
    
    def __init__(self, task: CleanTask, success: bool = True, error: str = None):
        """
        初始化清理结果
        
        参数:
            task (CleanTask): 清理任务
            success (bool): 是否成功
            error (str): 错误信息
        """
        self.file_path = task.file_path
        self.size = task.size
        self.metadata = task.metadata
        self.success = success
        self.error = error
        self.timestamp = datetime.now()

class CleanMethod(Enum):
    """清理方法枚举"""
    RECYCLE_BIN = 1  # 移动到回收站
    PERMANENT = 2    # 永久删除
    RENAME = 3       # 重命名（后缀添加.bak）
    SECURE = 4       # 安全删除（覆盖后删除）

class Cleaner:
    """清理器类，处理文件清理操作"""
    
    def __init__(self, method: CleanMethod = CleanMethod.RECYCLE_BIN):
        """
        初始化清理器
        
        参数:
            method (CleanMethod): 默认清理方法
        """
        self.method = method
        self.running = False
        self.clean_thread = None
        self.abort_flag = False
        
    def set_method(self, method: CleanMethod):
        """
        设置清理方法
        
        参数:
            method (CleanMethod): 清理方法
        """
        self.method = method
        
    def clean(self, 
             tasks: List[CleanTask], 
             method: CleanMethod = None,
             progress_callback: Callable[[int, int, int], None] = None,
             complete_callback: Callable[[List[CleanResult]], None] = None):
        """
        开始清理操作
        
        参数:
            tasks (List[CleanTask]): 清理任务列表
            method (CleanMethod): 清理方法，如果为None则使用默认方法
            progress_callback (callable): 进度回调函数，参数为(当前进度, 总进度, 百分比)
            complete_callback (callable): 完成回调函数，参数为清理结果列表
        """
        if self.running:
            return False
            
        # 设置清理方法
        clean_method = method or self.method
        
        # 开始清理线程
        self.abort_flag = False
        self.running = True
        self.clean_thread = threading.Thread(
            target=self._clean_thread,
            args=(tasks, clean_method, progress_callback, complete_callback)
        )
        self.clean_thread.daemon = True
        self.clean_thread.start()
        
        return True
        
    def _clean_thread(self, 
                     tasks: List[CleanTask], 
                     method: CleanMethod,
                     progress_callback: Callable = None,
                     complete_callback: Callable = None):
        """
        清理线程函数
        
        参数:
            tasks (List[CleanTask]): 清理任务列表
            method (CleanMethod): 清理方法
            progress_callback (callable): 进度回调函数
            complete_callback (callable): 完成回调函数
        """
        results = []
        total = len(tasks)
        
        for i, task in enumerate(tasks):
            # 检查是否中止
            if self.abort_flag:
                break
                
            # 更新进度
            current = i + 1
            percent = int((current / total) * 100) if total > 0 else 100
            
            if progress_callback:
                progress_callback(current, total, percent)
                
            # 执行清理
            result = self._clean_file(task, method)
            results.append(result)
            
            # 线程休眠一小段时间，避免占用过多资源
            time.sleep(0.01)
            
        # 完成回调
        self.running = False
        
        if complete_callback:
            complete_callback(results)
            
    def _clean_file(self, task: CleanTask, method: CleanMethod) -> CleanResult:
        """
        清理单个文件
        
        参数:
            task (CleanTask): 清理任务
            method (CleanMethod): 清理方法
            
        返回:
            CleanResult: 清理结果
        """
        try:
            file_path = task.file_path
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return CleanResult(task, False, "文件不存在")
                
            # 根据清理方法执行不同的操作
            if method == CleanMethod.RECYCLE_BIN:
                # 移动到回收站
                send2trash(file_path)
                
            elif method == CleanMethod.PERMANENT:
                # 永久删除
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                    
            elif method == CleanMethod.RENAME:
                # 重命名
                new_path = file_path + ".bak"
                # 如果已存在，尝试添加时间戳
                if os.path.exists(new_path):
                    timestamp = int(time.time())
                    new_path = f"{file_path}.{timestamp}.bak"
                os.rename(file_path, new_path)
                
            elif method == CleanMethod.SECURE:
                # 安全删除（先覆盖后删除）
                if not os.path.isdir(file_path):
                    self._secure_delete(file_path)
                else:
                    # 对于目录，只能普通删除
                    shutil.rmtree(file_path)
                    
            # 返回成功结果
            return CleanResult(task, True)
            
        except Exception as e:
            # 返回失败结果
            return CleanResult(task, False, str(e))
            
    def _secure_delete(self, file_path: str, passes: int = 3):
        """
        安全删除文件（多次覆盖后删除）
        
        参数:
            file_path (str): 文件路径
            passes (int): 覆盖次数
        """
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 打开文件并多次覆盖
            with open(file_path, "r+b") as f:
                # 多次覆盖
                for p in range(passes):
                    # 随机数据模式
                    if p == 0:
                        pattern = 0xFF  # 全1
                    elif p == 1:
                        pattern = 0x00  # 全0
                    else:
                        pattern = 0xAA  # 交替10101010
                        
                    # 写入模式数据
                    f.seek(0)
                    chunk_size = min(file_size, 1024 * 1024)  # 最大1MB分块
                    bytes_left = file_size
                    
                    while bytes_left > 0:
                        write_size = min(bytes_left, chunk_size)
                        f.write(bytes([pattern]) * write_size)
                        bytes_left -= write_size
                        
                    # 刷新到磁盘
                    f.flush()
                    os.fsync(f.fileno())
                    
            # 删除文件
            os.remove(file_path)
            
        except Exception as e:
            # 如果安全删除失败，尝试普通删除
            os.remove(file_path)
            
    def abort_clean(self):
        """中止当前清理操作"""
        if self.running:
            self.abort_flag = True
            
    def is_running(self) -> bool:
        """
        检查是否正在清理
        
        返回:
            bool: 是否正在清理
        """
        return self.running 