"""
文件工具模块，提供文件操作相关的工具函数
"""
import os
import shutil
import hashlib
import send2trash
import time
from pathlib import Path
from datetime import datetime
import stat
from typing import Optional, List, Dict, Tuple
import re
import sys
import logging
import mimetypes
import chardet
import tempfile
import json
import zipfile
import tarfile
import random
import string
import struct
import math

class FileUtils:
    """文件工具类，提供各种文件操作函数"""
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小
        
        参数:
            file_path (str): 文件路径
            
        返回:
            int: 文件大小（字节）
        """
        try:
            return os.path.getsize(file_path)
        except (FileNotFoundError, PermissionError, OSError):
            return 0
            
    @staticmethod
    def get_file_modified_time(file_path: str) -> Optional[datetime]:
        """
        获取文件修改时间
        
        参数:
            file_path (str): 文件路径
            
        返回:
            datetime: 文件修改时间
        """
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime)
        except (FileNotFoundError, PermissionError, OSError):
            return None
            
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        获取文件扩展名
        
        参数:
            file_path (str): 文件路径
            
        返回:
            str: 文件扩展名(不含点号)
        """
        _, ext = os.path.splitext(file_path)
        if ext:
            return ext[1:].lower()  # 去掉点号并转为小写
        return ""
        
    @staticmethod
    def move_to_trash(file_path: str) -> bool:
        """
        将文件移动到回收站
        
        参数:
            file_path (str): 文件路径
            
        返回:
            bool: 操作是否成功
        """
        try:
            # 使用send2trash库（需要安装）
            try:
                import send2trash
                send2trash.send2trash(file_path)
                return True
            except ImportError:
                # 如果send2trash不可用，尝试使用原生方式
                if os.name == 'nt':  # Windows
                    import winshell
                    try:
                        winshell.delete_file(file_path, no_confirm=True, allow_undo=True)
                        return True
                    except:
                        # 降级为直接删除
                        os.unlink(file_path)
                        return True
                else:  # Linux/Mac
                    # 在Linux/Mac上，如果没有send2trash，就直接删除
                    os.unlink(file_path)
                    return True
        except Exception as e:
            print(f"移动文件到回收站失败: {str(e)}")
            return False
            
    @staticmethod
    def secure_delete(file_path: str, passes: int = 3) -> bool:
        """
        安全删除文件（多次覆盖后删除）
        
        参数:
            file_path (str): 文件路径
            passes (int): 覆盖次数
            
        返回:
            bool: 操作是否成功
        """
        try:
            # 获取文件大小
            file_size = FileUtils.get_file_size(file_path)
            if file_size == 0:
                # 如果文件大小为0或无法获取，直接删除
                os.unlink(file_path)
                return True
                
            # 打开文件
            with open(file_path, "rb+") as f:
                # 多次覆盖文件内容
                for i in range(passes):
                    # 定位到文件开始
                    f.seek(0)
                    
                    # 使用不同的字节模式覆盖
                    if i == 0:
                        # 第一遍用0覆盖
                        pattern = b'\x00'
                    elif i == 1:
                        # 第二遍用1覆盖
                        pattern = b'\xFF'
                    else:
                        # 其他遍用随机数据覆盖
                        import random
                        pattern = bytes([random.randint(0, 255) for _ in range(min(4096, file_size))])
                    
                    # 写入覆盖数据
                    remaining = file_size
                    pattern_size = len(pattern)
                    
                    while remaining > 0:
                        chunk_size = min(remaining, pattern_size)
                        if chunk_size < pattern_size:
                            f.write(pattern[:chunk_size])
                        else:
                            f.write(pattern)
                        remaining -= chunk_size
                    
                    # 刷新到磁盘
                    f.flush()
                    os.fsync(f.fileno())
                    
            # 最后删除文件
            os.unlink(file_path)
            return True
            
        except Exception as e:
            print(f"安全删除文件失败: {str(e)}")
            return False
            
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除文件
        
        参数:
            file_path (str): 文件路径
            
        返回:
            bool: 操作是否成功
        """
        try:
            if os.path.exists(file_path):
                # 修改文件权限（如果需要）
                try:
                    # 确保文件可写
                    if not os.access(file_path, os.W_OK):
                        current_mode = os.stat(file_path).st_mode
                        os.chmod(file_path, current_mode | stat.S_IWRITE)
                except:
                    pass
                    
                # 删除文件
                os.unlink(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False
            
    @staticmethod
    def rename_file(file_path: str, new_name: str) -> bool:
        """
        重命名文件
        
        参数:
            file_path (str): 原文件路径
            new_name (str): 新文件名（不包含路径）
            
        返回:
            bool: 操作是否成功
        """
        try:
            if os.path.exists(file_path):
                directory = os.path.dirname(file_path)
                new_path = os.path.join(directory, new_name)
                
                # 如果目标文件已存在，先删除
                if os.path.exists(new_path):
                    os.unlink(new_path)
                    
                os.rename(file_path, new_path)
                return True
            return False
        except Exception as e:
            print(f"重命名文件失败: {str(e)}")
            return False
            
    @staticmethod
    def make_backup(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
        """
        创建文件备份
        
        参数:
            file_path (str): 文件路径
            backup_suffix (str): 备份文件后缀
            
        返回:
            str: 备份文件路径，失败返回None
        """
        try:
            if os.path.exists(file_path):
                backup_path = file_path + backup_suffix
                shutil.copy2(file_path, backup_path)
                return backup_path
            return None
        except Exception as e:
            print(f"创建文件备份失败: {str(e)}")
            return None
            
    @staticmethod
    def create_empty_file(file_path: str) -> bool:
        """
        创建空文件
        
        参数:
            file_path (str): 文件路径
            
        返回:
            bool: 操作是否成功
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            with open(file_path, 'w'):
                pass
            return True
        except Exception as e:
            print(f"创建空文件失败: {str(e)}")
            return False
            
    @staticmethod
    def is_file_locked(file_path: str) -> bool:
        """
        检查文件是否被锁定（正在被其他进程使用）
        
        参数:
            file_path (str): 文件路径
            
        返回:
            bool: 文件是否被锁定
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            if os.name == 'nt':  # Windows
                try:
                    # 尝试以独占方式打开文件
                    with open(file_path, 'a+b') as f:
                        # 如果能锁定文件，说明文件未被锁定
                        msvcrt_available = False
                        try:
                            import msvcrt
                            msvcrt_available = True
                            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                        except ImportError:
                            # msvcrt不可用，简单尝试写入
                            if f.writable():
                                original_position = f.tell()
                                f.seek(0, os.SEEK_END)
                                f.seek(original_position)
                        return False
                except (IOError, PermissionError):
                    return True
            else:  # Unix-like
                try:
                    import fcntl
                    with open(file_path, 'a+b') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return False
                except (ImportError, IOError, PermissionError):
                    # 如果fcntl不可用或无法获取锁，假设文件被锁定
                    return True
        except:
            # 出现异常，假设文件被锁定
            return True
            
    @staticmethod
    def get_content_type(file_path: str) -> str:
        """
        获取文件的MIME类型
        
        参数:
            file_path (str): 文件路径
            
        返回:
            str: 文件的MIME类型
        """
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or "application/octet-stream"
        except:
            # 如果无法确定，返回通用二进制类型
            return "application/octet-stream"
            
    @staticmethod
    def list_directory(directory: str, 
                      recursive: bool = False, 
                      include_pattern: str = None,
                      exclude_pattern: str = None) -> List[str]:
        """
        列出目录中的所有文件（可选递归）
        
        参数:
            directory (str): 目录路径
            recursive (bool): 是否递归扫描子目录
            include_pattern (str): 包含的文件模式（正则表达式）
            exclude_pattern (str): 排除的文件模式（正则表达式）
            
        返回:
            List[str]: 文件路径列表
        """
        result = []
        
        try:
            # 编译正则表达式
            include_regex = re.compile(include_pattern) if include_pattern else None
            exclude_regex = re.compile(exclude_pattern) if exclude_pattern else None
            
            if recursive:
                # 递归遍历
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # 检查文件是否匹配模式
                        if include_regex and not include_regex.search(file_path):
                            continue
                        if exclude_regex and exclude_regex.search(file_path):
                            continue
                            
                        result.append(file_path)
            else:
                # 非递归，只列出当前目录
                for item in os.listdir(directory):
                    file_path = os.path.join(directory, item)
                    if os.path.isfile(file_path):
                        # 检查文件是否匹配模式
                        if include_regex and not include_regex.search(file_path):
                            continue
                        if exclude_regex and exclude_regex.search(file_path):
                            continue
                            
                        result.append(file_path)
        except Exception as e:
            print(f"列出目录内容失败: {str(e)}")
            
        return result
        
    @staticmethod
    def count_files_by_type(directory: str, recursive: bool = True) -> Dict[str, int]:
        """
        统计目录中各类型文件的数量
        
        参数:
            directory (str): 目录路径
            recursive (bool): 是否递归扫描子目录
            
        返回:
            Dict[str, int]: 文件类型及数量的字典
        """
        result = {}
        
        try:
            files = FileUtils.list_directory(directory, recursive)
            
            for file_path in files:
                ext = FileUtils.get_file_extension(file_path)
                ext = ext.lower() if ext else "无扩展名"
                
                if ext in result:
                    result[ext] += 1
                else:
                    result[ext] = 1
        except Exception as e:
            print(f"统计文件类型失败: {str(e)}")
            
        return result
        
    @staticmethod
    def extract_text_from_file(file_path: str, max_size: int = 1024*1024) -> Optional[str]:
        """
        从文本文件中提取文本内容
        
        参数:
            file_path (str): 文件路径
            max_size (int): 最大读取大小（字节）
            
        返回:
            str: 文件内容，读取失败返回None
        """
        # 常见的文本文件扩展名
        text_extensions = {
            'txt', 'log', 'ini', 'cfg', 'conf', 'json', 'xml', 'htm', 'html', 
            'css', 'js', 'py', 'java', 'c', 'cpp', 'h', 'cs', 'php', 'pl', 
            'sh', 'bat', 'cmd', 'md', 'csv', 'tsv'
        }
        
        try:
            # 检查文件大小和类型
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return None
                
            file_size = FileUtils.get_file_size(file_path)
            if file_size == 0 or file_size > max_size:
                return None
                
            ext = FileUtils.get_file_extension(file_path)
            if ext not in text_extensions:
                # 可能不是文本文件
                return None
                
            # 尝试以不同编码读取文件
            encodings = ['utf-8', 'gbk', 'latin1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
                    
            return None
        except Exception as e:
            print(f"从文件提取文本失败: {str(e)}")
            return None
    
    @staticmethod
    def get_file_creation_time(file_path):
        """
        获取文件创建时间
        
        参数:
            file_path (str): 文件路径
            
        返回值:
            datetime: 文件创建时间
        """
        try:
            stat_result = os.stat(file_path)
            # 在不同的系统上，创建时间的属性可能不同
            # Windows 使用 st_ctime, Unix使用 st_birthtime （如果可用）
            try:
                creation_time = stat_result.st_birthtime  # macOS
            except AttributeError:
                creation_time = stat_result.st_ctime  # Windows/Linux
                
            return datetime.fromtimestamp(creation_time)
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def get_file_access_time(file_path):
        """
        获取文件最后访问时间
        
        参数:
            file_path (str): 文件路径
            
        返回值:
            datetime: 文件最后访问时间
        """
        try:
            stat_result = os.stat(file_path)
            return datetime.fromtimestamp(stat_result.st_atime)
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def calculate_file_hash(file_path, hash_type='md5', buffer_size=8192):
        """
        计算文件的哈希值
        
        参数:
            file_path (str): 文件路径
            hash_type (str): 哈希算法类型（'md5', 'sha1', 'sha256'）
            buffer_size (int): 读取文件的缓冲区大小
            
        返回值:
            str: 文件的哈希值
        """
        try:
            if hash_type == 'md5':
                hash_obj = hashlib.md5()
            elif hash_type == 'sha1':
                hash_obj = hashlib.sha1()
            elif hash_type == 'sha256':
                hash_obj = hashlib.sha256()
            else:
                hash_obj = hashlib.md5()  # 默认使用MD5
                
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(buffer_size)
                    if not data:
                        break
                    hash_obj.update(data)
                    
            return hash_obj.hexdigest()
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def safe_delete_directory(dir_path):
        """
        安全删除目录（移动到回收站）
        
        参数:
            dir_path (str): 目录路径
            
        返回值:
            bool: 删除成功返回True，否则返回False
        """
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                send2trash.send2trash(dir_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def force_delete_directory(dir_path):
        """
        强制删除目录（不移动到回收站）
        
        参数:
            dir_path (str): 目录路径
            
        返回值:
            bool: 删除成功返回True，否则返回False
        """
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                # 更改目录权限以便删除
                for root, dirs, files in os.walk(dir_path, topdown=False):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            os.chmod(file_path, stat.S_IWRITE)
                        except:
                            pass
                            
                shutil.rmtree(dir_path, ignore_errors=True)
                return not os.path.exists(dir_path)
            return False
        except Exception:
            return False
    
    @staticmethod
    def list_files(directory, recursive=True, include_dirs=False, filter_func=None):
        """
        列出目录中的所有文件
        
        参数:
            directory (str): 目录路径
            recursive (bool): 是否递归搜索子目录
            include_dirs (bool): 是否包含目录在结果中
            filter_func (callable): 过滤函数，接受文件路径作为参数，返回True则包含该文件
            
        返回值:
            list: 文件路径列表
        """
        files = []
        
        try:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                return files
                
            if recursive:
                for root, dirs, filenames in os.walk(directory):
                    # 如果包含目录
                    if include_dirs:
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            if filter_func is None or filter_func(dir_path):
                                files.append(dir_path)
                    
                    # 添加文件
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if filter_func is None or filter_func(file_path):
                            files.append(file_path)
            else:
                # 非递归模式
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if include_dirs or not entry.is_dir():
                            if filter_func is None or filter_func(entry.path):
                                files.append(entry.path)
        except Exception:
            pass
            
        return files
    
    @staticmethod
    def find_files_by_age(directory, days, older_than=True, recursive=True):
        """
        根据文件年龄查找文件
        
        参数:
            directory (str): 目录路径
            days (int): 天数
            older_than (bool): True表示查找比指定天数更老的文件，False表示查找更新的文件
            recursive (bool): 是否递归搜索子目录
            
        返回值:
            list: 文件路径列表
        """
        now = datetime.now()
        seconds = days * 24 * 3600  # 转换为秒
        
        def age_filter(file_path):
            try:
                mtime = FileUtils.get_file_modified_time(file_path)
                if mtime:
                    age = (now - mtime).total_seconds()
                    if older_than:
                        return age > seconds
                    else:
                        return age <= seconds
                return False
            except:
                return False
                
        return FileUtils.list_files(directory, recursive=recursive, filter_func=age_filter)
    
    @staticmethod
    def find_large_files(directory, min_size_mb, recursive=True):
        """
        查找大文件
        
        参数:
            directory (str): 目录路径
            min_size_mb (float): 最小文件大小（MB）
            recursive (bool): 是否递归搜索子目录
            
        返回值:
            list: 文件路径列表
        """
        min_size_bytes = min_size_mb * 1024 * 1024  # 转换为字节
        
        def size_filter(file_path):
            try:
                return os.path.isfile(file_path) and os.path.getsize(file_path) >= min_size_bytes
            except:
                return False
                
        return FileUtils.list_files(directory, recursive=recursive, filter_func=size_filter)
    
    @staticmethod
    def find_empty_directories(directory, recursive=True):
        """
        查找空目录
        
        参数:
            directory (str): 目录路径
            recursive (bool): 是否递归搜索子目录
            
        返回值:
            list: 空目录路径列表
        """
        empty_dirs = []
        
        try:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                return empty_dirs
                
            if recursive:
                for root, dirs, files in os.walk(directory, topdown=False):
                    # 检查当前目录是否为空
                    if not dirs and not files:
                        empty_dirs.append(root)
                    # 或者所有子目录都是空目录
                    elif not files and all(os.path.join(root, d) in empty_dirs for d in dirs):
                        empty_dirs.append(root)
            else:
                # 非递归模式只检查顶层目录
                if not os.listdir(directory):
                    empty_dirs.append(directory)
        except Exception:
            pass
            
        return empty_dirs
    
    @staticmethod
    def find_duplicate_files(directories, recursive=True):
        """
        查找重复文件
        
        参数:
            directories (list): 目录路径列表
            recursive (bool): 是否递归搜索子目录
            
        返回值:
            dict: 键为文件哈希值，值为具有相同哈希值的文件路径列表
        """
        if isinstance(directories, str):
            directories = [directories]
            
        # 第一步：按大小分组
        size_groups = {}
        
        for directory in directories:
            for file_path in FileUtils.list_files(directory, recursive=recursive):
                if os.path.isfile(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        if size not in size_groups:
                            size_groups[size] = []
                        size_groups[size].append(file_path)
                    except:
                        pass
        
        # 第二步：计算相同大小文件的哈希值
        hash_groups = {}
        
        for size, files in size_groups.items():
            if len(files) < 2:  # 跳过唯一大小的文件
                continue
                
            for file_path in files:
                file_hash = FileUtils.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(file_path)
        
        # 第三步：过滤出只有重复文件的组
        duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
        
        return duplicates
    
    @staticmethod
    def compress_files(files, output_path, format='zip'):
        """
        将文件或文件夹压缩为归档文件
        
        参数:
            files (str 或 list): 单个文件/文件夹路径或文件/文件夹路径列表
            output_path (str): 输出压缩文件的路径
            format (str): 压缩格式，支持'zip'或'tar'
            
        返回值:
            bool: 操作成功返回True，否则返回False
        """
        try:
            if isinstance(files, str):
                files = [files]
            
            if format.lower() == 'zip':
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file in files:
                        if os.path.isfile(file):
                            zipf.write(file, os.path.basename(file))
                        elif os.path.isdir(file):
                            for root, _, filenames in os.walk(file):
                                for filename in filenames:
                                    file_path = os.path.join(root, filename)
                                    arcname = os.path.relpath(file_path, os.path.dirname(file))
                                    zipf.write(file_path, arcname)
            elif format.lower() == 'tar':
                with tarfile.open(output_path, 'w:gz') as tar:
                    for file in files:
                        tar.add(file, arcname=os.path.basename(file))
            else:
                logging.error(f"不支持的压缩格式: {format}")
                return False
                
            return True
        except Exception as e:
            logging.error(f"压缩文件失败: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path, extract_to=None, password=None):
        """
        解压缩归档文件
        
        参数:
            archive_path (str): 归档文件路径
            extract_to (str): 解压缩目标目录，默认为归档文件所在目录
            password (str): 如果归档文件有密码保护，提供密码
            
        返回值:
            bool: 操作成功返回True，否则返回False
        """
        try:
            if not extract_to:
                extract_to = os.path.dirname(archive_path)
                
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
                
            file_ext = os.path.splitext(archive_path)[1].lower()
            
            if file_ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    if password:
                        zipf.setpassword(password.encode())
                    zipf.extractall(extract_to)
            elif file_ext in ['.tar', '.gz', '.bz2', '.xz']:
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(path=extract_to)
            else:
                logging.error(f"不支持的归档格式: {file_ext}")
                return False
                
            return True
        except Exception as e:
            logging.error(f"解压缩归档文件失败: {e}")
            return False
    
    @staticmethod
    def get_folder_size(folder_path):
        """
        计算文件夹的总大小
        
        参数:
            folder_path (str): 文件夹路径
            
        返回值:
            int: 文件夹大小（字节）
        """
        try:
            total_size = 0
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            logging.error(f"计算文件夹大小失败: {e}")
            return 0
    
    @staticmethod
    def read_json_file(file_path, default=None):
        """
        读取JSON文件
        
        参数:
            file_path (str): JSON文件路径
            default: 如果文件不存在或读取失败时返回的默认值
            
        返回值:
            dict/list: JSON数据
        """
        try:
            if not os.path.exists(file_path):
                return default
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"读取JSON文件失败: {e}")
            return default
    
    @staticmethod
    def write_json_file(file_path, data, indent=4):
        """
        写入JSON文件
        
        参数:
            file_path (str): JSON文件路径
            data (dict/list): 要写入的数据
            indent (int): 缩进空格数
            
        返回值:
            bool: 操作成功返回True，否则返回False
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            logging.error(f"写入JSON文件失败: {e}")
            return False
    
    @staticmethod
    def check_file_health(file_path):
        """
        检查文件是否损坏
        
        参数:
            file_path (str): 文件路径
            
        返回值:
            bool: 文件健康返回True，损坏返回False
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
                
            # 检查文件是否为空
            if os.path.getsize(file_path) == 0:
                return False
                
            # 尝试打开并读取文件的前1KB
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                
            # 针对不同类型的文件做特定检查
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 检查ZIP文件
            if file_ext == '.zip':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        zipf.testzip()  # 测试zip文件完整性
                    return True
                except:
                    return False
            
            # 检查图片文件
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                try:
                    from PIL import Image
                    Image.open(file_path).verify()
                    return True
                except:
                    return False
            
            # 检查PDF文件
            elif file_ext == '.pdf':
                if data.startswith(b'%PDF'):
                    return True
                return False
            
            # 默认情况下，如果我们能读取文件，则认为它没有损坏
            return True
            
        except Exception as e:
            logging.error(f"检查文件健康状态失败: {e}")
            return False
            
    @staticmethod
    def convert_size_to_human_readable(size_bytes):
        """
        将字节大小转换为人类可读的格式
        
        参数:
            size_bytes (int): 字节大小
            
        返回值:
            str: 人类可读的大小字符串（例如："1.23 MB"）
        """
        if size_bytes == 0:
            return "0 B"
            
        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}" 