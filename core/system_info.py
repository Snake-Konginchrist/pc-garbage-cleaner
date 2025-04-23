"""
系统信息模块，用于获取当前系统状态和信息
"""
import os
import sys
import platform
import psutil
import time
import datetime
from utils.system_utils import SystemUtils

class SystemInfo:
    """系统信息类，提供系统状态和信息的获取方法"""
    
    @staticmethod
    def get_system_info():
        """
        获取系统基本信息
        
        返回值:
            dict: 系统信息字典
        """
        system = platform.system()
        info = {
            'system': system,
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'uptime': SystemInfo.get_uptime_string()
        }
        
        # 系统特定信息
        if system == 'Windows':
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    info['product_name'] = winreg.QueryValueEx(key, "ProductName")[0]
                    info['build'] = winreg.QueryValueEx(key, "CurrentBuild")[0]
            except:
                pass
                
        elif system == 'Darwin':  # macOS
            info['macos_version'] = platform.mac_ver()[0]
            
        elif system == 'Linux':
            try:
                import distro
                info['distro'] = distro.name()
                info['distro_version'] = distro.version()
            except ImportError:
                try:
                    with open('/etc/os-release') as f:
                        for line in f:
                            if line.startswith('PRETTY_NAME='):
                                info['distro'] = line.split('=')[1].strip().strip('"')
                except:
                    pass
                    
        return info
    
    @staticmethod
    def get_uptime_string():
        """
        获取系统运行时间的格式化字符串
        
        返回值:
            str: 格式化后的运行时间字符串
        """
        uptime_seconds = time.time() - psutil.boot_time()
        
        days = int(uptime_seconds // (3600 * 24))
        hours = int((uptime_seconds % (3600 * 24)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if days > 0:
            return f"{days}天 {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def get_cpu_info():
        """
        获取CPU信息
        
        返回值:
            dict: CPU信息字典
        """
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
            'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'usage_per_core': [percentage for percentage in psutil.cpu_percent(percpu=True, interval=0.1)],
            'total_usage': psutil.cpu_percent(interval=0.1)
        }
        
        return cpu_info
    
    @staticmethod
    def get_memory_info():
        """
        获取内存信息
        
        返回值:
            dict: 内存信息字典
        """
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'formatted_total': SystemUtils.format_size(memory.total),
            'formatted_available': SystemUtils.format_size(memory.available),
            'formatted_used': SystemUtils.format_size(memory.used),
            'formatted_free': SystemUtils.format_size(memory.free),
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent,
            'formatted_swap_total': SystemUtils.format_size(swap.total),
            'formatted_swap_used': SystemUtils.format_size(swap.used),
            'formatted_swap_free': SystemUtils.format_size(swap.free)
        }
        
        return memory_info
    
    @staticmethod
    def get_disk_info():
        """
        获取磁盘信息
        
        返回值:
            list: 磁盘信息列表
        """
        disks = []
        
        for partition in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in partition.opts or partition.fstype == '':
                    # 跳过CD/DVD驱动器和不可访问的驱动器
                    continue
            else:
                if partition.fstype == '' or 'loop' in partition.device:
                    # 跳过不可访问的分区和循环设备
                    continue
                    
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                disk = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'formatted_total': SystemUtils.format_size(usage.total),
                    'formatted_used': SystemUtils.format_size(usage.used),
                    'formatted_free': SystemUtils.format_size(usage.free)
                }
                
                disks.append(disk)
            except PermissionError:
                # 跳过没有权限的分区
                continue
                
        return disks
    
    @staticmethod
    def get_network_info():
        """
        获取网络信息
        
        返回值:
            dict: 网络信息字典
        """
        network_stats = psutil.net_io_counters()
        network_addrs = psutil.net_if_addrs()
        
        network_info = {
            'bytes_sent': network_stats.bytes_sent,
            'bytes_recv': network_stats.bytes_recv,
            'packets_sent': network_stats.packets_sent,
            'packets_recv': network_stats.packets_recv,
            'errin': network_stats.errin,
            'errout': network_stats.errout,
            'dropin': network_stats.dropin,
            'dropout': network_stats.dropout,
            'formatted_bytes_sent': SystemUtils.format_size(network_stats.bytes_sent),
            'formatted_bytes_recv': SystemUtils.format_size(network_stats.bytes_recv),
            'interfaces': {}
        }
        
        for interface, addrs in network_addrs.items():
            network_info['interfaces'][interface] = []
            for addr in addrs:
                addr_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast,
                    'ptp': addr.ptp
                }
                network_info['interfaces'][interface].append(addr_info)
                
        return network_info
    
    @staticmethod
    def get_process_list(sort_by='memory', descending=True, limit=10):
        """
        获取进程列表
        
        参数:
            sort_by (str): 排序字段，可选值: 'memory', 'cpu', 'pid', 'name'
            descending (bool): 是否降序排序
            limit (int): 最大返回数量，None表示全部返回
            
        返回值:
            list: 进程信息列表
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'cpu_percent', 'create_time']):
            try:
                process_info = proc.info
                
                # 获取内存使用
                if hasattr(process_info['memory_info'], 'rss'):
                    memory_usage = process_info['memory_info'].rss
                else:
                    memory_usage = 0
                    
                # 获取CPU使用
                cpu_usage = process_info['cpu_percent'] / psutil.cpu_count()
                
                # 获取创建时间
                create_time = datetime.datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                
                processes.append({
                    'pid': process_info['pid'],
                    'name': process_info['name'],
                    'username': process_info['username'],
                    'memory_usage': memory_usage,
                    'formatted_memory': SystemUtils.format_size(memory_usage),
                    'cpu_usage': cpu_usage,
                    'create_time': create_time
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 跳过无法访问的进程
                pass
                
        # 排序进程列表
        sort_key = {
            'memory': lambda x: x['memory_usage'],
            'cpu': lambda x: x['cpu_usage'],
            'pid': lambda x: x['pid'],
            'name': lambda x: x['name'].lower()
        }.get(sort_by, lambda x: x['memory_usage'])
        
        processes.sort(key=sort_key, reverse=descending)
        
        # 限制返回数量
        if limit is not None:
            processes = processes[:limit]
            
        return processes
    
    @staticmethod
    def get_system_status():
        """
        获取系统当前状态
        
        返回值:
            dict: 系统状态字典
        """
        status = {
            'cpu': {
                'usage': psutil.cpu_percent(interval=0.1),
                'per_core': psutil.cpu_percent(interval=0.1, percpu=True)
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'formatted_used': SystemUtils.format_size(psutil.virtual_memory().used)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'used': psutil.disk_usage('/').used,
                'formatted_used': SystemUtils.format_size(psutil.disk_usage('/').used)
            },
            'network': {
                'sent': psutil.net_io_counters().bytes_sent,
                'recv': psutil.net_io_counters().bytes_recv,
                'formatted_sent': SystemUtils.format_size(psutil.net_io_counters().bytes_sent),
                'formatted_recv': SystemUtils.format_size(psutil.net_io_counters().bytes_recv)
            },
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': SystemInfo.get_uptime_string()
        }
        
        return status 