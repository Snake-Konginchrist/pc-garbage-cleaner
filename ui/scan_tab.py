"""
扫描选项卡模块，实现垃圾文件扫描功能的界面
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QCheckBox, QTreeWidget, QTreeWidgetItem, 
                            QProgressBar, QGroupBox, QSpinBox,
                            QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot

from core.scanner import Scanner, ScanTarget, ScanFilter
from utils.system_utils import SystemUtils
from utils.file_utils import FileUtils

class ScanUpdateSignals(QObject):
    """扫描更新信号类，用于线程间通信"""
    progress_update = pyqtSignal(int, int, int)  # current, total, percent
    scan_completed = pyqtSignal(list)  # 扫描结果列表

class ScanTab(QWidget):
    """扫描选项卡类，实现垃圾文件扫描功能的界面"""
    
    scan_completed = pyqtSignal(list)  # 扫描完成信号，参数为扫描结果列表
    
    def __init__(self, scanner, parent=None):
        """
        初始化扫描选项卡
        
        参数:
            scanner (Scanner): 扫描器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 保存扫描器实例
        self.scanner = scanner
        self.parent = parent
        
        # 创建信号对象
        self.signals = ScanUpdateSignals()
        self.signals.progress_update.connect(self.update_progress)
        self.signals.scan_completed.connect(self.scan_completed_handler)
        
        # 初始化界面
        self.init_ui()
        
        # 添加常见的扫描目标
        self.scanner.add_common_targets()
        
        # 更新目标列表
        self.update_target_list()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建扫描选项组
        scan_options_group = QGroupBox("扫描选项")
        scan_options_layout = QVBoxLayout()
        
        # 创建目标选择区域
        targets_layout = QHBoxLayout()
        targets_label = QLabel("扫描目标:")
        self.targets_tree = QTreeWidget()
        self.targets_tree.setHeaderLabels(["名称", "路径", "描述"])
        self.targets_tree.setColumnWidth(0, 150)
        self.targets_tree.setColumnWidth(1, 250)
        
        targets_layout.addWidget(targets_label)
        targets_layout.addWidget(self.targets_tree)
        
        # 添加自定义目标按钮
        targets_buttons_layout = QVBoxLayout()
        add_target_button = QPushButton("添加目标")
        add_target_button.clicked.connect(self.add_custom_target)
        remove_target_button = QPushButton("移除目标")
        remove_target_button.clicked.connect(self.remove_selected_target)
        select_all_button = QPushButton("全选")
        select_all_button.clicked.connect(self.select_all_targets)
        deselect_all_button = QPushButton("取消全选")
        deselect_all_button.clicked.connect(self.deselect_all_targets)
        
        targets_buttons_layout.addWidget(add_target_button)
        targets_buttons_layout.addWidget(remove_target_button)
        targets_buttons_layout.addWidget(select_all_button)
        targets_buttons_layout.addWidget(deselect_all_button)
        targets_buttons_layout.addStretch()
        
        targets_layout.addLayout(targets_buttons_layout)
        
        scan_options_layout.addLayout(targets_layout)
        
        # 创建过滤器选项区域
        filter_layout = QHBoxLayout()
        
        # 最小文件大小选项
        min_size_layout = QVBoxLayout()
        min_size_label = QLabel("最小文件大小:")
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000)
        self.min_size_spin.setValue(0)
        self.min_size_unit = QComboBox()
        self.min_size_unit.addItems(["KB", "MB", "GB"])
        self.min_size_unit.setCurrentIndex(1)  # 默认为MB
        
        min_size_layout.addWidget(min_size_label)
        min_size_box = QHBoxLayout()
        min_size_box.addWidget(self.min_size_spin)
        min_size_box.addWidget(self.min_size_unit)
        min_size_layout.addLayout(min_size_box)
        
        filter_layout.addLayout(min_size_layout)
        
        # 最小文件年龄选项
        min_age_layout = QVBoxLayout()
        min_age_label = QLabel("最小文件年龄:")
        self.min_age_spin = QSpinBox()
        self.min_age_spin.setRange(0, 3650)
        self.min_age_spin.setValue(0)
        self.min_age_unit = QComboBox()
        self.min_age_unit.addItems(["天", "周", "月", "年"])
        self.min_age_unit.setCurrentIndex(0)  # 默认为天
        
        min_age_layout.addWidget(min_age_label)
        min_age_box = QHBoxLayout()
        min_age_box.addWidget(self.min_age_spin)
        min_age_box.addWidget(self.min_age_unit)
        min_age_layout.addLayout(min_age_box)
        
        filter_layout.addLayout(min_age_layout)
        
        # 文件类型选项
        file_type_layout = QVBoxLayout()
        file_type_label = QLabel("文件类型:")
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["所有文件", "临时文件", "备份文件", "日志文件"])
        self.file_type_combo.setCurrentIndex(0)  # 默认为所有文件
        
        file_type_layout.addWidget(file_type_label)
        file_type_layout.addWidget(self.file_type_combo)
        
        filter_layout.addLayout(file_type_layout)
        
        # 递归扫描选项
        recursive_layout = QVBoxLayout()
        recursive_label = QLabel("")
        self.recursive_check = QCheckBox("递归扫描子目录")
        self.recursive_check.setChecked(True)
        
        recursive_layout.addWidget(recursive_label)
        recursive_layout.addWidget(self.recursive_check)
        
        filter_layout.addLayout(recursive_layout)
        
        scan_options_layout.addLayout(filter_layout)
        
        scan_options_group.setLayout(scan_options_layout)
        main_layout.addWidget(scan_options_group)
        
        # 创建进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("准备就绪")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # 创建扫描结果区域
        results_group = QGroupBox("扫描结果")
        results_layout = QVBoxLayout()
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["目标", "文件数量", "大小"])
        self.results_tree.setColumnWidth(0, 200)
        self.results_tree.setColumnWidth(1, 100)
        
        results_layout.addWidget(self.results_tree)
        
        # 添加统计信息标签
        self.stats_label = QLabel("总计: 0个文件, 0 KB")
        results_layout.addWidget(self.stats_label)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # 创建操作按钮区域
        buttons_layout = QHBoxLayout()
        
        self.scan_button = QPushButton("开始扫描")
        self.scan_button.clicked.connect(self.start_scan)
        
        self.stop_button = QPushButton("停止扫描")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        
        self.clean_button = QPushButton("清理选中项")
        self.clean_button.clicked.connect(self.clean_selected)
        self.clean_button.setEnabled(False)
        
        buttons_layout.addWidget(self.scan_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.clean_button)
        
        main_layout.addLayout(buttons_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
    def update_target_list(self):
        """更新目标列表"""
        self.targets_tree.clear()
        
        for target in self.scanner.targets:
            item = QTreeWidgetItem(self.targets_tree)
            item.setText(0, target.name)
            item.setText(1, target.path)
            item.setText(2, target.description)
            item.setCheckState(0, Qt.Checked if target.enabled else Qt.Unchecked)
            
            # 系统目录标记
            if target.is_system:
                item.setBackground(0, Qt.yellow)
                
    def update_scanner_from_ui(self):
        """根据界面设置更新扫描器"""
        # 更新目标启用状态
        for i in range(self.targets_tree.topLevelItemCount()):
            item = self.targets_tree.topLevelItem(i)
            target = self.scanner.targets[i]
            target.enabled = item.checkState(0) == Qt.Checked
            
        # 获取过滤器参数
        min_size = self.min_size_spin.value()
        min_size_unit = self.min_size_unit.currentText()
        
        # 转换单位为字节
        if min_size_unit == "KB":
            min_size *= 1024
        elif min_size_unit == "MB":
            min_size *= 1024 * 1024
        elif min_size_unit == "GB":
            min_size *= 1024 * 1024 * 1024
            
        # 获取最小年龄参数
        min_age = self.min_age_spin.value()
        min_age_unit = self.min_age_unit.currentText()
        
        # 转换单位为天
        if min_age_unit == "周":
            min_age *= 7
        elif min_age_unit == "月":
            min_age *= 30
        elif min_age_unit == "年":
            min_age *= 365
            
        # 创建过滤器
        extensions = None
        exclude_exts = None
        
        # 根据文件类型设置扩展名过滤
        file_type = self.file_type_combo.currentText()
        if file_type == "临时文件":
            extensions = [".tmp", ".temp", ".bak", ".dmp", ".log", "~"]
        elif file_type == "备份文件":
            extensions = [".bak", ".old", ".backup", ".save"]
        elif file_type == "日志文件":
            extensions = [".log", ".logs"]
            
        # 创建过滤器实例
        self.filter = ScanFilter(
            min_size=min_size,
            min_age_days=min_age,
            extensions=extensions,
            exclude_exts=exclude_exts
        )
        
    def add_custom_target(self):
        """添加自定义扫描目标"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择扫描目录", os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if dir_path:
            # 创建新目标
            target_name = os.path.basename(dir_path) or dir_path
            description = f"用户选择的目录: {dir_path}"
            
            # 调用scanner的add_custom_target方法
            self.scanner.add_custom_target(
                name=f"自定义目标: {target_name}",
                path=dir_path,
                description=description,
                enabled=True,
                patterns=None,  # 默认匹配所有文件
                min_age=None,
                min_size=0
            )
            
            # 更新列表
            self.update_target_list()
            
    def remove_selected_target(self):
        """移除选中的扫描目标"""
        selected_items = self.targets_tree.selectedItems()
        
        if not selected_items:
            return
            
        # 获取选中项的索引
        indices = []
        for item in selected_items:
            index = self.targets_tree.indexOfTopLevelItem(item)
            indices.append(index)
            
        # 按索引从大到小排序，这样删除时不会影响前面的索引
        indices.sort(reverse=True)
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(indices)} 个扫描目标吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # 删除目标
        for index in indices:
            # 防止索引越界
            if 0 <= index < len(self.scanner.targets):
                del self.scanner.targets[index]
                
        # 更新列表
        self.update_target_list()
        
    def select_all_targets(self):
        """选中所有扫描目标"""
        for i in range(self.targets_tree.topLevelItemCount()):
            item = self.targets_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Checked)
            
    def deselect_all_targets(self):
        """取消选中所有扫描目标"""
        for i in range(self.targets_tree.topLevelItemCount()):
            item = self.targets_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Unchecked)
            
    def start_scan(self):
        """开始扫描操作"""
        # 确保至少有一个目标被选中
        has_selected = False
        for i in range(self.targets_tree.topLevelItemCount()):
            item = self.targets_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                has_selected = True
                break
                
        if not has_selected:
            QMessageBox.warning(self, "警告", "请至少选择一个扫描目标")
            return
            
        # 更新扫描器设置
        self.update_scanner_from_ui()
        
        # 更新界面状态
        self.progress_bar.setValue(0)
        self.progress_label.setText("正在扫描...")
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.clean_button.setEnabled(False)
        self.results_tree.clear()
        self.stats_label.setText("总计: 0个文件, 0 KB")
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("正在扫描...")
            
        # 开始扫描，使用信号对象作为回调
        self.scanner.scan(
            filter_obj=self.filter,
            progress_callback=self.progress_callback,
            complete_callback=self.complete_callback
        )
        
    def stop_scan(self):
        """停止扫描操作"""
        self.scanner.abort_scan()
        self.progress_label.setText("扫描已中止")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("扫描已中止")
            
    def progress_callback(self, current, total, percent):
        """进度回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.progress_update.emit(current, total, percent)
    
    def complete_callback(self, results):
        """完成回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.scan_completed.emit(results)
        
    @pyqtSlot(int, int, int)
    def update_progress(self, current, total, percent):
        """
        更新扫描进度（在主线程中执行）
        
        参数:
            current (int): 当前进度
            total (int): 总进度
            percent (int): 百分比
        """
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"正在扫描... {current}/{total} ({percent}%)")
        
    @pyqtSlot(list)
    def scan_completed_handler(self, results):
        """
        扫描完成处理函数（在主线程中执行）
        
        参数:
            results (list): 扫描结果列表
        """
        # 更新界面状态
        self.progress_bar.setValue(100)
        self.progress_label.setText("扫描完成")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 显示结果
        self.show_scan_results(results)
        
        # 发送扫描完成信号
        self.scan_completed.emit(results)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("扫描完成")
            
    def show_scan_results(self, results):
        """
        显示扫描结果
        
        参数:
            results (list): 扫描结果列表
        """
        self.results_tree.clear()
        
        # 获取结果摘要
        summary = self.scanner.get_results_summary()
        total_files = summary['total_files']
        total_size = summary['total_size']
        formatted_size = summary['formatted_size']
        
        # 更新统计信息
        self.stats_label.setText(f"总计: {total_files}个文件, {formatted_size}")
        
        # 如果没有结果
        if not results:
            return
            
        # 添加结果到树
        for result in results:
            item = QTreeWidgetItem(self.results_tree)
            item.setText(0, result.target.name)
            item.setText(1, str(result.get_file_count()))
            item.setText(2, result.get_formatted_size())
            
            # 系统目录标记
            if result.target.is_system:
                item.setBackground(0, Qt.yellow)
                
            # 添加文件子项
            for file_path in result.files[:100]:  # 限制显示数量，避免过多
                file_item = QTreeWidgetItem(item)
                file_item.setText(0, os.path.basename(file_path))
                file_item.setText(1, "")
                file_size = FileUtils.get_file_size(file_path)
                file_item.setText(2, SystemUtils.format_size(file_size))
                
            # 如果文件太多，添加省略提示
            if len(result.files) > 100:
                more_item = QTreeWidgetItem(item)
                more_item.setText(0, f"... 还有 {len(result.files) - 100} 个文件未显示")
                
        # 展开第一级
        self.results_tree.expandToDepth(0)
        
        # 启用清理按钮
        self.clean_button.setEnabled(True)
        
    def clean_selected(self):
        """清理选中的项目"""
        # 获取选中的结果
        selected_results = []
        
        for i in range(self.results_tree.topLevelItemCount()):
            item = self.results_tree.topLevelItem(i)
            if item.isSelected():
                selected_results.append(i)
                
        # 如果没有选中项
        if not selected_results:
            QMessageBox.warning(self, "警告", "请选择要清理的项目")
            return
            
        # 切换到清理选项卡
        if self.parent:
            self.parent.tabs.setCurrentIndex(1)
            # 传递选中的结果索引给清理选项卡
            self.parent.clean_tab.clean_selected_results(selected_results) 