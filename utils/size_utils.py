"""
文件大小转换和计算工具
"""
from typing import Tuple, List, Union, Dict


class SizeUtils:
    """处理文件大小的工具类"""
    
    # 字节单位转换常量
    BYTE = 1
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024
    TB = 1024 * 1024 * 1024 * 1024
    
    @staticmethod
    def bytes_to_human_readable(size_in_bytes: int, decimal_places: int = 2) -> str:
        """
        将字节大小转换为人类可读的格式
        
        参数:
            size_in_bytes (int): 字节大小
            decimal_places (int): 小数位数
            
        返回:
            str: 格式化后的大小字符串，如 "1.5 MB"
        """
        if size_in_bytes < 0:
            return "未知大小"
            
        if size_in_bytes == 0:
            return "0 B"
            
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        size = float(size_in_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        # 格式化小数位数
        if unit_index == 0:  # 如果是字节，不显示小数
            return f"{int(size)} {units[unit_index]}"
        else:
            format_str = f"{{:.{decimal_places}f}} {{}}".format(size, units[unit_index])
            result = format_str.format(size, units[unit_index])
            # 去掉末尾的0
            if "." in result:
                result = result.rstrip("0").rstrip(".") + " " + units[unit_index]
            return result
            
    @staticmethod
    def human_readable_to_bytes(size_str: str) -> int:
        """
        将人类可读的大小字符串转换为字节数
        
        参数:
            size_str (str): 大小字符串，如 "1.5 MB"
            
        返回:
            int: 字节大小
        """
        # 净化输入字符串
        size_str = size_str.strip().upper()
        
        # 处理空字符串
        if not size_str:
            return 0
            
        # 定义单位映射
        units = {
            "B": SizeUtils.BYTE,
            "BYTE": SizeUtils.BYTE,
            "BYTES": SizeUtils.BYTE,
            "K": SizeUtils.KB,
            "KB": SizeUtils.KB,
            "KIB": SizeUtils.KB,
            "M": SizeUtils.MB,
            "MB": SizeUtils.MB,
            "MIB": SizeUtils.MB,
            "G": SizeUtils.GB,
            "GB": SizeUtils.GB,
            "GIB": SizeUtils.GB,
            "T": SizeUtils.TB,
            "TB": SizeUtils.TB,
            "TIB": SizeUtils.TB
        }
        
        try:
            # 找到数字和单位
            import re
            match = re.match(r"([\d.]+)\s*([A-Za-z]+)", size_str)
            
            if match:
                size_val = float(match.group(1))
                unit = match.group(2).upper()
                
                # 计算字节数
                if unit in units:
                    return int(size_val * units[unit])
                else:
                    # 如果单位不识别，假设为字节
                    return int(size_val)
            else:
                # 如果没有单位，假设为字节
                return int(float(size_str))
                
        except (ValueError, TypeError):
            return 0
            
    @staticmethod
    def format_size_range(min_size: int, max_size: int) -> str:
        """
        格式化大小范围
        
        参数:
            min_size (int): 最小大小（字节）
            max_size (int): 最大大小（字节）
            
        返回:
            str: 格式化的大小范围
        """
        if min_size < 0 or max_size < 0:
            return "未知大小范围"
            
        if min_size == max_size:
            return SizeUtils.bytes_to_human_readable(min_size)
            
        min_str = SizeUtils.bytes_to_human_readable(min_size)
        max_str = SizeUtils.bytes_to_human_readable(max_size)
        
        return f"{min_str} - {max_str}"
        
    @staticmethod
    def add_sizes(sizes: List[int]) -> int:
        """
        计算大小列表的总和
        
        参数:
            sizes (List[int]): 大小列表（字节）
            
        返回:
            int: 总大小（字节）
        """
        # 过滤无效值
        valid_sizes = [size for size in sizes if isinstance(size, (int, float)) and size >= 0]
        
        if not valid_sizes:
            return 0
            
        return sum(valid_sizes)
        
    @staticmethod
    def get_size_category(size_in_bytes: int) -> str:
        """
        根据文件大小获取分类
        
        参数:
            size_in_bytes (int): 文件大小（字节）
            
        返回:
            str: 大小分类（"极小"、"小"、"中等"、"大"、"极大"）
        """
        if size_in_bytes < 0:
            return "未知"
            
        if size_in_bytes == 0:
            return "空"
            
        if size_in_bytes < 10 * SizeUtils.KB:  # 10KB以下
            return "极小"
        elif size_in_bytes < 1 * SizeUtils.MB:  # 1MB以下
            return "小"
        elif size_in_bytes < 100 * SizeUtils.MB:  # 100MB以下
            return "中等"
        elif size_in_bytes < 1 * SizeUtils.GB:  # 1GB以下
            return "大"
        else:  # 1GB及以上
            return "极大"
            
    @staticmethod
    def parse_size_filter(size_filter: str) -> Tuple[int, int]:
        """
        解析大小过滤器字符串
        
        参数:
            size_filter (str): 过滤器字符串，如 ">10MB", "<1GB", "10MB-1GB"
            
        返回:
            Tuple[int, int]: (最小大小, 最大大小)，以字节为单位
        """
        if not size_filter or not isinstance(size_filter, str):
            return (0, float('inf'))
            
        size_filter = size_filter.strip()
        
        # 检查是否是范围格式
        if "-" in size_filter:
            parts = size_filter.split("-", 1)
            min_size = SizeUtils.human_readable_to_bytes(parts[0].strip())
            max_size = SizeUtils.human_readable_to_bytes(parts[1].strip())
            return (min_size, max_size)
            
        # 检查是否是大于格式
        if size_filter.startswith(">"):
            min_size = SizeUtils.human_readable_to_bytes(size_filter[1:].strip())
            return (min_size, float('inf'))
            
        # 检查是否是小于格式
        if size_filter.startswith("<"):
            max_size = SizeUtils.human_readable_to_bytes(size_filter[1:].strip())
            return (0, max_size)
            
        # 如果没有特殊格式，假设是精确大小
        exact_size = SizeUtils.human_readable_to_bytes(size_filter)
        return (exact_size, exact_size)
        
    @staticmethod
    def format_percentage(part: int, total: int, decimal_places: int = 1) -> str:
        """
        计算并格式化百分比
        
        参数:
            part (int): 部分大小
            total (int): 总大小
            decimal_places (int): 小数位数
            
        返回:
            str: 格式化的百分比字符串
        """
        if total <= 0 or part < 0:
            return "0%"
            
        percentage = (part / total) * 100
        
        # 格式化小数位数
        format_str = f"{{:.{decimal_places}f}}%"
        result = format_str.format(percentage)
        
        # 如果是整数百分比，去掉小数部分
        if result.endswith(".0%"):
            result = result[:-3] + "%"
            
        return result
        
    @staticmethod
    def get_size_distribution(sizes: Dict[str, int]) -> Dict[str, Tuple[int, str]]:
        """
        计算大小分布
        
        参数:
            sizes (Dict[str, int]): 名称和大小的字典
            
        返回:
            Dict[str, Tuple[int, str]]: 名称、大小和百分比的字典
        """
        result = {}
        
        # 计算总大小
        total_size = SizeUtils.add_sizes(list(sizes.values()))
        
        # 计算每个项目的百分比
        for name, size in sizes.items():
            percentage = SizeUtils.format_percentage(size, total_size)
            result[name] = (size, percentage)
            
        return result 