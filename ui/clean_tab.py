"""
清理选项卡模块，实现垃圾文件清理功能的界面
"""
import os
import shutil
import threading
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QCheckBox, QTreeWidget, QTreeWidgetItem, 
                            QProgressBar, QGroupBox, QMessageBox, QSplitter,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QColor, QBrush

from core.cleaner import Cleaner, CleanTask, CleanResult
from utils.system_utils import SystemUtils
from utils.file_utils import FileUtils

class CleanUpdateSignals(QObject):
    """清理更新信号类，用于线程间通信"""
    progress_update = pyqtSignal(int, int, int)  # current, total, percent
    clean_completed = pyqtSignal(list)  # 清理结果列表

class CleanTab(QWidget):
    """清理选项卡类，实现垃圾文件清理功能的界面"""
    
    clean_completed = pyqtSignal(list)  # 清理完成信号，参数为清理结果列表
    
    def __init__(self, cleaner, parent=None):
        """
        初始化清理选项卡
        
        参数:
            cleaner (Cleaner): 清理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 保存实例引用
        self.cleaner = cleaner
        self.parent = parent
        
        # 获取scanner引用
        if parent:
            self.scanner = parent.scanner
        else:
            self.scanner = None
        
        # 创建信号对象
        self.signals = CleanUpdateSignals()
        self.signals.progress_update.connect(self.update_progress)
        self.signals.clean_completed.connect(self.clean_completed_handler)
        
        # 保存扫描结果
        self.scan_results = []
        
        # 清理任务列表
        self.clean_tasks = []
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建文件列表区域
        files_group = QGroupBox("待清理文件")
        files_layout = QVBoxLayout()
        
        # 文件表格
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels(["选择", "文件名", "路径", "大小", "类型"])
        
        # 设置列宽
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.files_table.setColumnWidth(0, 50)
        self.files_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.files_table.setColumnWidth(1, 150)
        self.files_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.files_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.files_table.setColumnWidth(3, 100)
        self.files_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.files_table.setColumnWidth(4, 100)
        
        files_layout.addWidget(self.files_table)
        
        # 添加文件统计信息
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("总计: 0个文件, 0 KB")
        self.select_all_check = QCheckBox("全选")
        self.select_all_check.stateChanged.connect(self.toggle_select_all)
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.select_all_check)
        
        files_layout.addLayout(stats_layout)
        
        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group)
        
        # 创建进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("准备就绪")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # 创建清理结果区域
        results_group = QGroupBox("清理结果")
        results_layout = QVBoxLayout()
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["目标", "文件数量", "大小", "状态"])
        self.results_tree.setColumnWidth(0, 200)
        self.results_tree.setColumnWidth(1, 100)
        self.results_tree.setColumnWidth(2, 100)
        
        results_layout.addWidget(self.results_tree)
        
        # 添加结果统计信息标签
        self.results_stats_label = QLabel("总计: 0个文件, 0 KB")
        results_layout.addWidget(self.results_stats_label)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # 创建操作按钮区域
        buttons_layout = QHBoxLayout()
        
        self.back_button = QPushButton("返回扫描")
        self.back_button.clicked.connect(self.back_to_scan)
        
        self.clean_button = QPushButton("开始清理")
        self.clean_button.clicked.connect(self.start_clean)
        self.clean_button.setEnabled(False)
        
        self.stop_button = QPushButton("停止清理")
        self.stop_button.clicked.connect(self.stop_clean)
        self.stop_button.setEnabled(False)
        
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.clean_button)
        buttons_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(buttons_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
    def set_scan_results(self, results):
        """
        设置扫描结果
        
        参数:
            results (list): 扫描结果列表
        """
        self.scan_results = results
        self.update_files_table()
        
    def update_from_scan_results(self, results):
        """
        从扫描结果更新界面
        
        参数:
            results (list): 扫描结果列表
        """
        # 这个方法在用户从扫描选项卡切换到清理选项卡时被调用
        self.set_scan_results(results)
        
    def update_files_table(self):
        """更新文件表格"""
        self.files_table.setRowCount(0)  # 清空表格
        
        # 如果没有结果
        if not self.scan_results:
            self.stats_label.setText("总计: 0个文件, 0 KB")
            self.clean_button.setEnabled(False)
            return
            
        # 获取所有文件
        all_files = []
        for result in self.scan_results:
            for file_path in result.files:
                try:
                    # 获取文件信息
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.dirname(file_path)
                    file_size = FileUtils.get_file_size(file_path)
                    file_type = FileUtils.get_file_extension(file_path)
                    
                    all_files.append({
                        "path": file_path,
                        "name": file_name,
                        "dir": file_dir,
                        "size": file_size,
                        "type": file_type,
                        "result": result  # 保存对应的扫描结果引用
                    })
                except Exception as e:
                    print(f"获取文件信息出错: {file_path} - {str(e)}")
        
        # 更新表格
        self.files_table.setRowCount(len(all_files))
        
        # 添加文件到表格
        for i, file_info in enumerate(all_files):
            # 创建复选框
            check_box = QCheckBox()
            check_box.setChecked(True)
            check_box_cell = QWidget()
            layout = QHBoxLayout(check_box_cell)
            layout.addWidget(check_box)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.files_table.setCellWidget(i, 0, check_box_cell)
            
            # 添加其他信息
            name_item = QTableWidgetItem(file_info["name"])
            name_item.setData(Qt.UserRole, file_info)  # 存储完整信息
            self.files_table.setItem(i, 1, name_item)
            
            self.files_table.setItem(i, 2, QTableWidgetItem(file_info["dir"]))
            self.files_table.setItem(i, 3, QTableWidgetItem(SystemUtils.format_size(file_info["size"])))
            self.files_table.setItem(i, 4, QTableWidgetItem(file_info["type"]))
            
            # 系统文件标记
            if file_info["result"].target.is_system:
                for col in range(1, 5):
                    if self.files_table.item(i, col):
                        self.files_table.item(i, col).setBackground(QBrush(QColor(255, 255, 200)))
        
        # 更新统计信息
        total_size = sum(file_info["size"] for file_info in all_files)
        self.stats_label.setText(f"总计: {len(all_files)}个文件, {SystemUtils.format_size(total_size)}")
        
        # 启用清理按钮
        self.clean_button.setEnabled(True)
        
    def toggle_select_all(self, state):
        """
        切换全选状态
        
        参数:
            state (int): 复选框状态
        """
        for row in range(self.files_table.rowCount()):
            check_box = self.files_table.cellWidget(row, 0).findChild(QCheckBox)
            if check_box:
                check_box.setChecked(state == Qt.Checked)
                
    def clean_selected_results(self, result_indices):
        """
        清理选中的扫描结果
        
        参数:
            result_indices (list): 要清理的扫描结果索引列表
        """
        # 确保scanner和results存在
        if not self.scanner or not hasattr(self.scanner, 'results'):
            return
            
        # 确保索引有效
        valid_indices = [i for i in result_indices if 0 <= i < len(self.scanner.results)]
        
        if not valid_indices:
            return
            
        # 获取要清理的扫描结果
        results = [self.scanner.results[i] for i in valid_indices]
        self.set_scan_results(results)
        
    def back_to_scan(self):
        """返回扫描选项卡"""
        if self.parent:
            self.parent.tabs.setCurrentIndex(0)
            
    def get_selected_files(self):
        """获取用户选中的文件列表"""
        selected_files = []
        
        for row in range(self.files_table.rowCount()):
            check_box = self.files_table.cellWidget(row, 0).findChild(QCheckBox)
            if check_box and check_box.isChecked():
                name_item = self.files_table.item(row, 1)
                if name_item:
                    file_info = name_item.data(Qt.UserRole)
                    selected_files.append(file_info)
                    
        return selected_files
        
    def start_clean(self):
        """开始清理操作"""
        # 获取选中的文件
        selected_files = self.get_selected_files()
        
        if not selected_files:
            QMessageBox.warning(self, "警告", "请选择要清理的文件")
            return
            
        # 清理前确认
        reply = QMessageBox.question(
            self, "确认清理", 
            f"确定要清理选中的 {len(selected_files)} 个文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # 创建清理任务
        self.clean_tasks = []
        for file_info in selected_files:
            task = CleanTask(file_info["path"])
            self.clean_tasks.append(task)
            
        # 更新界面状态
        self.progress_bar.setValue(0)
        self.progress_label.setText("正在清理...")
        self.clean_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.results_tree.clear()
        self.results_stats_label.setText("总计: 0个文件, 0 KB")
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("正在清理...")
            
        # 开始清理，使用信号对象作为回调
        self.cleaner.clean(
            self.clean_tasks,
            progress_callback=self.progress_callback,
            complete_callback=self.complete_callback
        )
    
    def progress_callback(self, current, total, percent):
        """进度回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.progress_update.emit(current, total, percent)
    
    def complete_callback(self, results):
        """完成回调函数，将在后台线程中调用，发送信号到主线程"""
        self.signals.clean_completed.emit(results)
    
    @pyqtSlot(int, int, int)
    def update_progress(self, current, total, percent):
        """
        更新清理进度（在主线程中执行）
        
        参数:
            current (int): 当前进度
            total (int): 总进度
            percent (int): 百分比
        """
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"正在清理... {current}/{total} ({percent}%)")
        
    @pyqtSlot(list)
    def clean_completed_handler(self, results):
        """
        清理完成处理函数（在主线程中执行）
        
        参数:
            results (list): 清理结果列表
        """
        # 更新界面状态
        self.progress_bar.setValue(100)
        self.progress_label.setText("清理完成")
        self.clean_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 显示结果
        self.show_clean_results(results)
        
        # 发送清理完成信号
        self.clean_completed.emit(results)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("清理完成")
            
        # 从表格中移除已清理的文件
        self.remove_cleaned_files(results)
        
    def show_clean_results(self, results):
        """
        显示清理结果
        
        参数:
            results (list): 清理结果列表
        """
        self.results_tree.clear()
        
        # 获取结果分类
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        success_size = sum(r.size for r in results if r.success)
        
        # 创建成功节点
        if success_count > 0:
            success_item = QTreeWidgetItem(self.results_tree)
            success_item.setText(0, "清理成功")
            success_item.setText(1, str(success_count))
            success_item.setText(2, SystemUtils.format_size(success_size))
            success_item.setText(3, "完成")
            success_item.setBackground(0, QBrush(QColor(200, 255, 200)))
            
            # 添加文件子项
            for result in results:
                if result.success:
                    file_item = QTreeWidgetItem(success_item)
                    file_item.setText(0, os.path.basename(result.file_path))
                    file_item.setText(1, "")
                    file_item.setText(2, SystemUtils.format_size(result.size))
                    file_item.setText(3, "成功")
            
        # 创建失败节点
        if failed_count > 0:
            failed_item = QTreeWidgetItem(self.results_tree)
            failed_item.setText(0, "清理失败")
            failed_item.setText(1, str(failed_count))
            failed_item.setText(2, "")
            failed_item.setText(3, "失败")
            failed_item.setBackground(0, QBrush(QColor(255, 200, 200)))
            
            # 添加文件子项
            for result in results:
                if not result.success:
                    file_item = QTreeWidgetItem(failed_item)
                    file_item.setText(0, os.path.basename(result.file_path))
                    file_item.setText(1, "")
                    file_item.setText(2, "")
                    file_item.setText(3, f"失败: {result.error}")
                    
        # 展开第一级
        self.results_tree.expandToDepth(0)
        
        # 更新统计信息
        self.results_stats_label.setText(
            f"总计: {success_count}个文件清理成功, {SystemUtils.format_size(success_size)}, "
            f"{failed_count}个文件清理失败"
        )
        
    def remove_cleaned_files(self, results):
        """
        从表格中删除已清理的文件
        
        参数:
            results (list): 清理结果列表
        """
        # 获取成功清理的文件路径
        cleaned_paths = set(r.file_path for r in results if r.success)
        
        # 从表格中删除
        rows_to_remove = []
        for row in range(self.files_table.rowCount()):
            name_item = self.files_table.item(row, 1)
            if name_item:
                file_info = name_item.data(Qt.UserRole)
                if file_info["path"] in cleaned_paths:
                    rows_to_remove.append(row)
        
        # 从下往上删除行，避免索引变化
        for row in sorted(rows_to_remove, reverse=True):
            self.files_table.removeRow(row)
            
        # 更新统计信息
        remaining_size = 0
        for row in range(self.files_table.rowCount()):
            name_item = self.files_table.item(row, 1)
            if name_item:
                file_info = name_item.data(Qt.UserRole)
                remaining_size += file_info["size"]
                
        self.stats_label.setText(f"总计: {self.files_table.rowCount()}个文件, {SystemUtils.format_size(remaining_size)}")
        
        # 如果表格为空，禁用清理按钮
        if self.files_table.rowCount() == 0:
            self.clean_button.setEnabled(False)
        
    def stop_clean(self):
        """停止清理操作"""
        self.cleaner.abort_clean()
        self.progress_label.setText("清理已中止")
        self.clean_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 设置父窗口状态
        if self.parent:
            self.parent.set_status("清理已中止")
            
        # 从表格中移除已清理的文件
        self.remove_cleaned_files([]) 