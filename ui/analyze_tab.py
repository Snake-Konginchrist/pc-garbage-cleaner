"""
分析选项卡模块，实现磁盘分析功能的界面
"""
import os
import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QTreeWidget, QTreeWidgetItem, 
                            QProgressBar, QFileDialog, QSplitter, QFrame,
                            QTabWidget, QGroupBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QColor, QBrush, QPainter, QPen, QPixmap

from core.analyzer import Analyzer
from utils.system_utils import SystemUtils
from utils.file_utils import FileUtils
from utils.size_utils import SizeUtils

class AnalyzeUpdateSignals(QObject):
    """分析更新信号类，用于线程间通信"""
    progress_update = pyqtSignal(str, int, int)  # current_path, file_count, dir_count
    analyze_completed = pyqtSignal(object)  # 分析结果

class AnalyzeTab(QWidget):
    """分析选项卡类，实现磁盘分析功能的界面"""
    
    analyze_completed = pyqtSignal(object)  # 分析完成信号
    
    def __init__(self, analyzer, parent=None):
        """
        初始化分析选项卡
        
        参数:
            analyzer (Analyzer): 分析器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 保存实例引用
        self.analyzer = analyzer
        self.parent = parent
        
        # 创建信号对象
        self.signals = AnalyzeUpdateSignals()
        self.signals.progress_update.connect(self.update_progress)
        self.signals.analyze_completed.connect(self.analyze_completed_handler)
        
        # 分析结果
        self.analyze_result = None
        
        # 当前选中的磁盘路径
        self.current_path = ""
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建选项区域
        options_group = QGroupBox("分析选项")
        options_layout = QVBoxLayout()
        
        # 创建路径选择区域
        path_layout = QHBoxLayout()
        self.path_label = QLabel("选择路径:")
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMinimumWidth(300)
        
        # 添加系统盘
        for disk in self.analyzer.get_all_disks():
            self.path_combo.addItem(f"{disk['name']} ({disk['formatted_free']} 可用 / {disk['formatted_total']} 总)", disk['path'])
            
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.browse_button)
        
        options_layout.addLayout(path_layout)
        
        # 创建分析选项区域
        analyze_options_layout = QHBoxLayout()
        
        # 最大深度选项
        self.depth_label = QLabel("最大深度:")
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 10)
        self.depth_spin.setValue(3)
        self.depth_spin.setToolTip("扫描的最大文件夹深度")
        
        # 显示隐藏文件选项
        self.show_hidden_check = QCheckBox("显示隐藏文件")
        self.show_hidden_check.setChecked(False)
        
        # 分析按钮
        self.analyze_button = QPushButton("开始分析")
        self.analyze_button.clicked.connect(self.start_analyze)
        
        # 停止按钮
        self.stop_button = QPushButton("停止分析")
        self.stop_button.clicked.connect(self.stop_analyze)
        self.stop_button.setEnabled(False)
        
        analyze_options_layout.addWidget(self.depth_label)
        analyze_options_layout.addWidget(self.depth_spin)
        analyze_options_layout.addWidget(self.show_hidden_check)
        analyze_options_layout.addStretch()
        analyze_options_layout.addWidget(self.analyze_button)
        analyze_options_layout.addWidget(self.stop_button)
        
        options_layout.addLayout(analyze_options_layout)
        
        # 添加进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("准备就绪")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        options_layout.addLayout(progress_layout)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # 创建结果选项卡
        self.results_tabs = QTabWidget()
        
        # 创建文件树选项卡
        self.tree_tab = QWidget()
        tree_layout = QVBoxLayout()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["名称", "大小", "百分比", "类型"])
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.setColumnWidth(1, 100)
        self.file_tree.setColumnWidth(2, 80)
        self.file_tree.itemExpanded.connect(self.on_item_expanded)
        
        tree_layout.addWidget(self.file_tree)
        self.tree_tab.setLayout(tree_layout)
        
        # 创建文件类型选项卡
        self.types_tab = QWidget()
        types_layout = QVBoxLayout()
        
        self.types_tree = QTreeWidget()
        self.types_tree.setHeaderLabels(["类型", "文件数量", "总大小", "百分比"])
        self.types_tree.setColumnWidth(0, 150)
        self.types_tree.setColumnWidth(1, 100)
        self.types_tree.setColumnWidth(2, 100)
        
        types_layout.addWidget(self.types_tree)
        self.types_tab.setLayout(types_layout)
        
        # 添加到结果选项卡
        self.results_tabs.addTab(self.tree_tab, "文件树")
        self.results_tabs.addTab(self.types_tab, "文件类型")
        
        main_layout.addWidget(self.results_tabs)
        
        # 创建总结区域
        summary_group = QGroupBox("分析总结")
        summary_layout = QVBoxLayout()
        
        self.summary_label = QLabel('请选择一个目录并点击"开始分析"按钮')
        summary_layout.addWidget(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # 设置主布局
        self.setLayout(main_layout)
        
    def browse_path(self):
        """浏览并选择路径"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择要分析的目录", 
            self.path_combo.currentText() or os.path.expanduser("~")
        )
        
        if directory:
            # 检查目录是否已在下拉列表中
            index = self.path_combo.findText(directory)
            if index >= 0:
                self.path_combo.setCurrentIndex(index)
            else:
                self.path_combo.addItem(directory)
                self.path_combo.setCurrentText(directory)
                
    def start_analyze(self):
        """开始分析操作"""
        # 获取选中的路径
        path = self.path_combo.currentText()
        
        if not path or not os.path.exists(path):
            if self.parent:
                self.parent.set_status("请选择有效的路径")
            return
            
        # 保存当前路径
        self.current_path = path
        
        # 获取分析深度
        max_depth = self.depth_spin.value()
        
        # 更新界面状态
        self.progress_bar.setValue(0)
        self.progress_label.setText("正在分析...")
        self.analyze_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # 清空结果显示
        self.file_tree.clear()
        self.types_tree.clear()
        self.summary_label.setText("正在分析...")
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status(f"正在分析 {path}...")
            
        # 开始分析，使用信号对象作为回调
        show_hidden = self.show_hidden_check.isChecked()
        self.analyzer.analyze_disk(
            path, 
            max_depth=max_depth,
            show_hidden=show_hidden,
            progress_callback=self.progress_callback,
            complete_callback=self.complete_callback
        )
        
    def stop_analyze(self):
        """停止分析操作"""
        self.analyzer.abort_analyze()
        self.progress_label.setText("分析已中止")
        self.analyze_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("分析已中止")
            
    def progress_callback(self, current_path, file_count, dir_count):
        """进度回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.progress_update.emit(current_path, file_count, dir_count)
    
    def complete_callback(self, result):
        """完成回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.analyze_completed.emit(result)
        
    @pyqtSlot(str, int, int)
    def update_progress(self, current_path, file_count, dir_count):
        """
        更新分析进度（在主线程中执行）
        
        参数:
            current_path (str): 当前正在分析的路径
            file_count (int): 已扫描的文件数量
            dir_count (int): 已扫描的目录数量
        """
        # 更新进度标签
        base_path = os.path.basename(current_path) or current_path
        self.progress_label.setText(f"正在分析: {base_path}")
        
        # 更新总结信息
        self.summary_label.setText(f"已扫描 {file_count} 个文件, {dir_count} 个目录")
        
        # 进度条根据文件数更新
        if file_count > 0:
            # 设置一个虚拟进度，因为我们不知道总文件数
            progress = min(99, file_count % 100)
            self.progress_bar.setValue(progress)
            
    @pyqtSlot(object)
    def analyze_completed_handler(self, result):
        """
        分析完成处理函数（在主线程中执行）
        
        参数:
            result: 分析结果
        """
        # 保存结果
        self.analyze_result = result
        
        # 更新界面状态
        self.progress_bar.setValue(100)
        self.progress_label.setText("分析完成")
        self.analyze_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 显示结果
        self.show_analyze_results(result)
        
        # 发送分析完成信号
        self.analyze_completed.emit(result)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("分析完成")
            
    def show_analyze_results(self, result):
        """
        显示分析结果
        
        参数:
            result: 分析结果
        """
        if not result:
            return
            
        # 更新文件树
        self.update_file_tree(result)
        
        # 更新文件类型统计
        self.update_types_tree(result)
        
        # 更新总结信息
        self.update_summary(result)
        
    def update_file_tree(self, result):
        """
        更新文件树显示
        
        参数:
            result: 分析结果
        """
        self.file_tree.clear()
        
        if not result or not result.root_item:
            return
            
        # 创建根节点
        root_name = os.path.basename(result.root_item.path) or result.root_item.path
        root_item = QTreeWidgetItem(self.file_tree)
        root_item.setText(0, root_name)
        root_item.setText(1, SizeUtils.bytes_to_human_readable(result.root_item.size))
        root_item.setText(2, "100%")
        root_item.setText(3, "目录")
        root_item.setData(0, Qt.UserRole, result.root_item)
        
        # 添加子项
        self.add_children_to_tree(root_item, result.root_item.children, result.root_item.size)
        
        # 展开根节点
        root_item.setExpanded(True)
        
    def add_children_to_tree(self, parent_item, children, total_size):
        """
        添加子项到树
        
        参数:
            parent_item: 父树项
            children: 子项列表
            total_size: 总大小，用于计算百分比
        """
        # 按大小排序
        sorted_children = sorted(children, key=lambda x: x.size, reverse=True)
        
        for child in sorted_children:
            # 只添加前50个子项，避免界面过于复杂
            if parent_item.childCount() >= 50:
                # 添加"更多..."项
                more_item = QTreeWidgetItem(parent_item)
                more_item.setText(0, f"更多项目 ({len(sorted_children) - 50})")
                more_item.setForeground(0, QBrush(QColor(128, 128, 128)))
                break
                
            item = QTreeWidgetItem(parent_item)
            item.setText(0, child.name)
            item.setText(1, SizeUtils.bytes_to_human_readable(child.size))
            
            # 计算百分比
            if total_size > 0:
                percent = (child.size / total_size) * 100
                item.setText(2, f"{percent:.1f}%")
            else:
                item.setText(2, "0%")
                
            # 设置类型和图标
            if child.is_dir:
                item.setText(3, "目录")
            else:
                ext = FileUtils.get_file_extension(child.path)
                item.setText(3, ext or "文件")
                
            # 存储原始数据项
            item.setData(0, Qt.UserRole, child)
            
            # 如果有子项，添加一个空项目，等待展开时再添加实际子项
            if child.is_dir and child.children:
                QTreeWidgetItem(item)
                
    def on_item_expanded(self, item):
        """
        树项展开事件处理
        
        参数:
            item: 被展开的树项
        """
        # 获取原始数据项
        data_item = item.data(0, Qt.UserRole)
        
        # 如果第一个子项是空项，表示需要加载子项
        if item.childCount() == 1 and item.child(0).text(0) == "":
            # 删除空项
            item.removeChild(item.child(0))
            
            # 添加实际子项
            if data_item and data_item.children:
                self.add_children_to_tree(item, data_item.children, data_item.size)
                
    def update_types_tree(self, result):
        """
        更新文件类型统计树
        
        参数:
            result: 分析结果
        """
        self.types_tree.clear()
        
        if not result or not result.file_types:
            return
            
        # 获取文件类型统计
        type_stats = result.file_types
        total_size = sum(stats['size'] for ext, stats in type_stats.items())
        
        # 按大小排序
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True)
        
        for ext, stats in sorted_types:
            item = QTreeWidgetItem(self.types_tree)
            
            # 设置类型名称
            if not ext:
                item.setText(0, "无扩展名")
            else:
                item.setText(0, ext.upper())
                
            # 设置文件数量
            item.setText(1, str(stats['count']))
            
            # 设置大小
            item.setText(2, SizeUtils.bytes_to_human_readable(stats['size']))
            
            # 设置百分比
            if total_size > 0:
                percent = (stats['size'] / total_size) * 100
                item.setText(3, f"{percent:.1f}%")
            else:
                item.setText(3, "0%")
                
        # 展开类型树
        self.types_tree.expandAll()
        
    def update_summary(self, result):
        """
        更新分析总结信息
        
        参数:
            result: 分析结果
        """
        if not result:
            return
            
        # 创建总结文本
        disk_usage = self.analyzer.get_disk_usage(self.current_path)
        total_space, used_space, free_space, percent_used = disk_usage
        
        summary_text = (
            f"<b>路径:</b> {result.path}<br>"
            f"<b>总文件数:</b> {result.file_count:,} 个文件<br>"
            f"<b>总目录数:</b> {result.dir_count:,} 个目录<br>"
            f"<b>总大小:</b> {SizeUtils.bytes_to_human_readable(result.total_size)}<br>"
            f"<b>磁盘总空间:</b> {SizeUtils.bytes_to_human_readable(total_space)}<br>"
            f"<b>已用空间:</b> {SizeUtils.bytes_to_human_readable(used_space)} ({percent_used:.1f}%)<br>"
            f"<b>可用空间:</b> {SizeUtils.bytes_to_human_readable(free_space)}<br>"
            f"<b>分析时间:</b> {result.duration:.2f} 秒"
        )
        
        self.summary_label.setText(summary_text) 