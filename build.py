#!/usr/bin/env python3
"""
斯黄电脑垃圾清理器 - 多平台打包脚本
支持Windows、macOS和Linux平台的应用程序打包
"""
import os
import sys
import json
import shutil
import platform
import argparse
import subprocess
from pathlib import Path

# 从JSON文件加载应用信息
def load_app_info():
    try:
        with open('app_info.json', 'r', encoding='utf-8') as f:
            app_info = json.load(f)
        return app_info
    except Exception as e:
        print(f"无法加载应用信息: {e}")
        print("将使用默认配置")
        # 返回默认配置
        return {
            "app_name": "斯黄电脑垃圾清理器",
            "app_name_en": "SK PC Garbage Cleaner",
            "version": "1.0.0",
            "main_script": "main.py",
            "icon_dir": "ui/resources",
            "icon_file_windows": "ui/resources/icon.ico",
            "icon_file_macos": "ui/resources/icon.icns",
            "icon_file_linux": "ui/resources/icon.png"
        }

# 加载应用信息
APP_INFO = load_app_info()

# 从APP_INFO获取各种配置
APP_NAME = APP_INFO["app_name"]
APP_NAME_EN = APP_INFO["app_name_en"]
APP_NAME_EN_EXE = APP_INFO["app_name_en_exe"]
APP_NAME_INSTALLER = APP_INFO["app_name_installer"]
VERSION = APP_INFO["version"]
MAIN_SCRIPT = APP_INFO["main_script"]
ICON_DIR = APP_INFO["icon_dir"]
ICON_FILE_WINDOWS = APP_INFO["icon_file_windows"]
ICON_FILE_MACOS = APP_INFO["icon_file_macos"]
ICON_FILE_LINUX = APP_INFO["icon_file_linux"]

def check_requirements():
    """检查必要的依赖是否已安装"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def get_platform():
    """获取当前操作系统平台"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def build_windows(args):
    """为Windows构建应用程序"""
    print("开始为Windows构建应用程序...")
    
    # 默认使用英文名称，并添加版本号
    app_name_en_exe = f"{APP_NAME_EN_EXE}-windows-v{VERSION}"
    
    # 检查图标文件是否存在
    if not os.path.exists(ICON_FILE_WINDOWS):
        print(f"警告: 图标文件 {ICON_FILE_WINDOWS} 不存在，将使用默认图标")
        icon_param = ""
    else:
        icon_param = f"--icon={ICON_FILE_WINDOWS}"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        f"--name={app_name_en_exe}",
        "--windowed",
        "--onefile",  # 默认生成单个可执行文件
        icon_param,
        f"--add-data={ICON_DIR};{ICON_DIR}",
    ]
    
    # 根据参数添加选项
    if args.console:
        cmd.remove("--windowed")
    if args.upx:
        cmd.append("--upx-dir=upx")
    
    # 添加主脚本
    cmd.append(MAIN_SCRIPT)
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    # 执行构建命令
    print(f"执行命令: {' '.join(cmd)}")
    # 修改为使用Python模块方式调用PyInstaller
    python_cmd = [sys.executable, "-m", "PyInstaller"]
    python_cmd.extend(cmd[1:])  # 去掉原命令中的"pyinstaller"
    subprocess.call(python_cmd)
    
    print("Windows应用程序构建完成!")
    print(f"可执行文件位于: dist/{app_name_en_exe}.exe")

def build_macos(args):
    """为macOS构建应用程序"""
    print("开始为macOS构建应用程序...")
    
    # 默认使用英文名称
    app_name_en = APP_NAME_EN

    # 检查图标文件是否存在
    if not os.path.exists(ICON_FILE_MACOS):
        print(f"警告: 图标文件 {ICON_FILE_MACOS} 不存在，将使用默认图标")
        icon_param = ""
    else:
        icon_param = f"--icon={ICON_FILE_MACOS}"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        f"--name={app_name_en}",
        "--windowed",
        icon_param,
        f"--add-data={ICON_DIR}:{ICON_DIR}",
    ]
    
    # 根据参数添加选项
    if args.onefile:
        cmd.append("--onefile")
    if args.console:
        cmd.remove("--windowed")
    if args.upx:
        cmd.append("--upx-dir=upx")
    
    # 添加主脚本
    cmd.append(MAIN_SCRIPT)
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    # 执行构建命令
    print(f"执行命令: {' '.join(cmd)}")
    # 修改为使用Python模块方式调用PyInstaller
    python_cmd = [sys.executable, "-m", "PyInstaller"]
    python_cmd.extend(cmd[1:])  # 去掉原命令中的"pyinstaller"
    subprocess.call(python_cmd)
    
    print("macOS应用程序构建完成!")
    print(f"应用程序位于: dist/{app_name_en}.app")
    
    # 默认创建DMG安装包，除非明确指定不创建
    if not args.no_dmg:
        # 动态添加版本号到安装程序名称
        installer_name = f"{APP_NAME_INSTALLER}-macos-v{VERSION}"
        create_dmg(installer_name)
    else:
        print("已跳过DMG安装包创建")

def create_dmg(app_name):
    """创建macOS DMG安装包"""
    try:
        print("正在创建DMG安装包...")
        
        # 检查是否在macOS系统上
        current_platform = platform.system().lower()
        if current_platform != "darwin":
            print("警告: 创建DMG安装包只能在macOS系统上进行")
            print("当前在非macOS系统上尝试构建macOS应用，将跳过DMG安装包创建")
            print("提示: 如果你需要为macOS创建完整安装包，请在macOS系统上运行此脚本")
            return
        
        # 检查create-dmg是否安装
        result = subprocess.run(["which", "create-dmg"], capture_output=True, text=True)
        if not result.stdout:
            print("需要安装create-dmg工具")
            print("可以通过Homebrew安装: brew install create-dmg")
            return
        
        # 构建DMG创建命令
        dmg_cmd = [
            "create-dmg",
            f"--volname", f"{app_name}",
            "--window-pos", "200", "120",
            "--window-size", "800", "400",
            "--icon-size", "100",
            f"--icon", f"{app_name}.app", "200", "190",
            f"--hide-extension", f"{app_name}.app",
            "--app-drop-link", "600", "185",
            f"{app_name}.dmg",
            f"dist/{app_name}.app"
        ]
        
        # 执行DMG创建命令
        subprocess.call(dmg_cmd)
        print(f"DMG安装包创建完成: {app_name}.dmg")
    except Exception as e:
        print(f"创建DMG时出错: {e}")

def build_linux(args):
    """为Linux构建应用程序"""
    print("开始为Linux构建应用程序...")
    
    # Linux平台始终使用英文名称，避免编码问题
    app_name_en_exe = APP_NAME_EN_EXE
    
    # 检查图标文件是否存在
    if os.path.exists(ICON_FILE_LINUX):
        icon_param = f"--icon={ICON_FILE_LINUX}"
    else:
        print(f"警告: 图标文件 {ICON_FILE_LINUX} 不存在，将使用默认图标")
        icon_param = ""
    
    # 构建命令
    cmd = [
        "pyinstaller",
        f"--name={app_name_en_exe}",
        "--windowed",
        icon_param,
        f"--add-data={ICON_DIR}:{ICON_DIR}",
    ]
    
    # 根据参数添加选项
    if args.onefile:
        cmd.append("--onefile")
    if args.console:
        cmd.remove("--windowed")
    if args.upx:
        cmd.append("--upx-dir=upx")
    
    # 添加主脚本
    cmd.append(MAIN_SCRIPT)
    
    # 过滤空字符串
    cmd = [c for c in cmd if c]
    
    # 执行构建命令
    print(f"执行命令: {' '.join(cmd)}")
    # 修改为使用Python模块方式调用PyInstaller
    python_cmd = [sys.executable, "-m", "PyInstaller"]
    python_cmd.extend(cmd[1:])  # 去掉原命令中的"pyinstaller"
    subprocess.call(python_cmd)
    
    print("Linux应用程序构建完成!")
    print(f"可执行文件位于: dist/{app_name_en_exe}")
    
    # 默认创建DEB安装包，除非明确指定不创建
    if not args.no_deb:
        # 动态添加版本号到安装程序名称
        installer_name = f"{APP_NAME_INSTALLER}-linux-v{VERSION}"
        create_deb_package(installer_name, VERSION)
    else:
        print("已跳过DEB安装包创建")

def create_deb_package(app_name, version):
    """创建Debian/Ubuntu DEB安装包"""
    try:
        print("正在创建DEB安装包...")
        
        # 检查是否在Linux系统上
        current_platform = platform.system().lower()
        if current_platform != "linux":
            print("警告: 创建DEB安装包只能在Linux系统上进行")
            print("当前在非Linux系统上尝试构建Linux应用，将跳过DEB安装包创建")
            print("提示: 如果你需要为Linux创建完整安装包，请在Linux系统上运行此脚本")
            return
        
        # 创建目录结构
        pkg_name = f"{app_name}_{version}-1"
        pkg_dir = Path(pkg_name)
        bin_dir = pkg_dir / "usr" / "local" / "bin"
        app_dir = pkg_dir / "usr" / "share" / "applications"
        debian_dir = pkg_dir / "DEBIAN"
        
        # 创建目录
        bin_dir.mkdir(parents=True, exist_ok=True)
        app_dir.mkdir(parents=True, exist_ok=True)
        debian_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制可执行文件
        shutil.copytree(f"dist/{app_name}", bin_dir / app_name)
        
        # 创建desktop文件
        desktop_content = f"""[Desktop Entry]
Name={APP_INFO['app_name_en']}
Name[zh_CN]={APP_INFO['app_name']}
Comment={APP_INFO.get('description', 'Clean garbage files from your computer')}
Comment[zh_CN]={APP_INFO.get('description_zh', '清理计算机垃圾文件')}
Exec=/usr/local/bin/{app_name}/{app_name}
Icon=/usr/local/bin/{app_name}/{ICON_DIR}/icon.png
Terminal=false
Type=Application
Categories=Utility;
"""
        with open(app_dir / f"{app_name}.desktop", "w") as f:
            f.write(desktop_content)
        
        # 创建控制文件
        maintainer = APP_INFO.get('maintainer', 'Unknown')
        maintainer_email = APP_INFO.get('maintainer_email', 'unknown@example.com')
        
        control_content = f"""Package: {app_name}
Version: {version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3
Maintainer: {maintainer} <{maintainer_email}>
Description: {APP_INFO.get('app_name_en', app_name)}
 {APP_INFO.get('description', 'A tool for cleaning garbage files from your computer.')}
 {APP_INFO.get('description_zh', '支持Windows、MacOS和Linux系统的电脑垃圾清理工具。')}
"""
        with open(debian_dir / "control", "w") as f:
            f.write(control_content)
        
        # 检查dpkg-deb命令是否可用
        try:
            subprocess.run(["dpkg-deb", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("错误: 找不到dpkg-deb命令")
            print("请确保已安装Debian/Ubuntu包管理工具")
            return
            
        # 构建DEB包
        subprocess.call(["dpkg-deb", "--build", pkg_name])
        print(f"DEB安装包创建完成: {pkg_name}.deb")
    except Exception as e:
        print(f"创建DEB包时出错: {e}")

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    # 删除PyInstaller生成的目录
    for dir_to_remove in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_to_remove):
            shutil.rmtree(dir_to_remove)
    
    # 删除spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
    
    print("构建文件已清理完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description=f"{APP_NAME}打包脚本")
    
    parser.add_argument("--platform", choices=["windows", "macos", "linux", "all"], 
                        help="选择打包平台，默认为当前平台", default=get_platform())
    parser.add_argument("--onefile", action="store_true", help="打包为单个可执行文件")
    parser.add_argument("--console", action="store_true", help="显示控制台窗口")
    parser.add_argument("--upx", action="store_true", help="使用UPX压缩可执行文件")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--no-dmg", action="store_true", help="macOS平台不创建DMG安装包")
    parser.add_argument("--no-deb", action="store_true", help="Linux平台不创建DEB安装包")
    parser.add_argument("--use-english-name", action="store_true", 
                        help="统一使用英文名称作为应用程序名称")
    
    args = parser.parse_args()
    
    # 清理构建文件
    if args.clean:
        clean_build()
        return
    
    # 检查依赖
    check_requirements()
    
    # 根据平台构建应用
    if args.platform == "windows" or args.platform == "all":
        build_windows(args)
    
    if args.platform == "macos" or args.platform == "all":
        build_macos(args)
    
    if args.platform == "linux" or args.platform == "all":
        build_linux(args)

if __name__ == "__main__":
    main() 