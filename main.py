"""
电脑垃圾清理器 - 主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """程序入口函数"""
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用，并在退出时返回状态码
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 