"""
主窗口模块，实现应用程序的主界面
"""
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, 
                            QAction, QMessageBox, QFileDialog, QMenu, 
                            QStatusBar, QToolBar, QLabel, QWidget)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer

# 导入功能选项卡
from ui.scan_tab import ScanTab
from ui.clean_tab import CleanTab
from ui.analyze_tab import AnalyzeTab

# 导入核心功能模块
from core.scanner import Scanner
from core.cleaner import Cleaner
from core.analyzer import Analyzer
from core.system_info import SystemInfo

# 导入工具模块
from utils.system_utils import SystemUtils
from utils.file_utils import FileUtils
from utils.path_utils import PathUtils

class MainWindow(QMainWindow):
    """主窗口类，实现应用程序的主界面"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口标题和图标
        self.setWindowTitle("斯黄电脑垃圾清理器")
        self.setWindowIcon(QIcon("ui/resources/icon.png"))
        
        # 设置窗口尺寸
        self.resize(1024, 768)
        
        # 创建核心功能模块实例
        self.scanner = Scanner()
        self.cleaner = Cleaner()
        self.analyzer = Analyzer()
        
        # 初始化界面
        self.init_ui()
        
        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 设置系统信息更新定时器
        self.info_timer = QTimer()
        self.info_timer.timeout.connect(self.update_system_info)
        self.info_timer.start(5000)  # 每5秒更新一次
        
        # 首次更新系统信息
        self.update_system_info()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建选项卡
        self.create_tabs()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 扫描操作
        scan_action = QAction("扫描", self)
        scan_action.triggered.connect(self.start_scan)
        file_menu.addAction(scan_action)
        
        # 清理操作
        clean_action = QAction("清理", self)
        clean_action.triggered.connect(self.start_clean)
        file_menu.addAction(clean_action)
        
        # 分析操作
        analyze_action = QAction("分析", self)
        analyze_action.triggered.connect(self.start_analyze)
        file_menu.addAction(analyze_action)
        
        file_menu.addSeparator()
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        
        # 设置操作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        # 关于操作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        # 如果需要完全删除工具栏，可以将整个方法改为：
        # pass
        
        # 或者只保留一部分按钮
        tool_bar = QToolBar("工具栏")
        self.addToolBar(tool_bar)
        
        # 扫描操作
        scan_action = QAction(QIcon("ui/resources/scan.png"), "扫描", self)
        scan_action.triggered.connect(self.start_scan)
        tool_bar.addAction(scan_action)
        
        # 清理操作
        clean_action = QAction(QIcon("ui/resources/clean.png"), "清理", self)
        clean_action.triggered.connect(self.start_clean)
        tool_bar.addAction(clean_action)
        
        # 分析操作
        analyze_action = QAction(QIcon("ui/resources/analyze.png"), "分析", self)
        analyze_action.triggered.connect(self.start_analyze)
        tool_bar.addAction(analyze_action)
        
    def create_tabs(self):
        """创建选项卡"""
        self.tabs = QTabWidget()
        
        # 创建扫描选项卡
        self.scan_tab = ScanTab(self.scanner, self)
        self.tabs.addTab(self.scan_tab, "扫描")
        
        # 创建清理选项卡
        self.clean_tab = CleanTab(self.cleaner, self)
        self.tabs.addTab(self.clean_tab, "清理")
        
        # 创建分析选项卡
        self.analyze_tab = AnalyzeTab(self.analyzer, self)
        self.tabs.addTab(self.analyze_tab, "分析")
        
        # 连接选项卡切换信号
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # 设置中央部件
        self.setCentralWidget(self.tabs)
        
    def on_tab_changed(self, index):
        """
        选项卡切换事件处理
        
        参数:
            index (int): 新选项卡的索引
        """
        # 如果切换到清理选项卡，且有扫描结果，则更新清理选项卡
        if index == 1 and self.scanner.results:
            self.clean_tab.update_from_scan_results(self.scanner.results)
            
    def start_scan(self):
        """开始扫描操作"""
        # 切换到扫描选项卡
        self.tabs.setCurrentIndex(0)
        # 调用扫描选项卡的扫描方法
        self.scan_tab.start_scan()
        
    def start_clean(self):
        """开始清理操作"""
        # 切换到清理选项卡
        self.tabs.setCurrentIndex(1)
        # 调用清理选项卡的清理方法
        self.clean_tab.start_clean()
        
    def start_analyze(self):
        """开始分析操作"""
        # 切换到分析选项卡
        self.tabs.setCurrentIndex(2)
        # 调用分析选项卡的分析方法
        self.analyze_tab.start_analyze()
        
    def show_settings(self):
        """显示设置对话框"""
        QMessageBox.information(self, "设置", "设置功能尚未实现")
        
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>斯黄电脑垃圾清理器</h2>
        <p>版本: 1.0.0</p>
        <p>一个跨平台的电脑垃圾清理工具</p>
        <p>支持Windows、MacOS和Linux系统</p>
        <p>© 2025 All Rights Reserved</p>
        """
        
        QMessageBox.about(self, "关于", about_text)
        
    def update_system_info(self):
        """更新系统信息"""
        try:
            # 获取内存信息
            memory_info = SystemInfo.get_memory_info()
            
            # 获取磁盘信息（系统盘）
            if SystemUtils.is_windows():
                system_path = "C:\\"
            else:
                system_path = "/"
                
            disk_usage = self.analyzer.get_disk_usage(system_path)
            
            # 获取CPU使用率
            cpu_info = SystemInfo.get_cpu_info()
            
            # 更新状态栏
            status_text = f"CPU: {cpu_info['total_usage']:.1f}% | 内存: {memory_info['percent']:.1f}% | 磁盘: {disk_usage[3]:.1f}%"
            self.status_label.setText(status_text)
        except Exception as e:
            # 忽略更新错误
            pass
            
    def closeEvent(self, event):
        """
        窗口关闭事件处理
        
        参数:
            event: 关闭事件
        """
        # 确认是否退出
        reply = QMessageBox.question(
            self, "确认退出", 
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 停止所有可能正在进行的操作
            if self.scanner.is_running:
                self.scanner.abort_scan()
                
            if self.cleaner.is_running:
                self.cleaner.abort_clean()
                
            if self.analyzer.is_analyzing:
                self.analyzer.abort_analyze()
                
            # 停止定时器
            self.info_timer.stop()
            
            event.accept()
        else:
            event.ignore()
            
    def set_status(self, message):
        """
        设置状态栏消息
        
        参数:
            message (str): 状态消息
        """
        self.status_label.setText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 