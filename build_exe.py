"""
打包脚本，用于将水印程序打包成Windows可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """构建可执行文件"""
    # 安装PyInstaller
    install_pyinstaller()
    
    # 切换到项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # 使用PyInstaller构建
    print("正在构建可执行文件...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=watermark_app",
        "--windowed",  # 无控制台窗口
        "--add-data=templates;templates",  # 添加模板文件
        "--add-data=config.json;.",  # 添加配置文件
        "--hidden-import=PIL._tkinter_finder",  # 添加隐藏导入
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("构建完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def main():
    """主函数"""
    print("开始打包水印应用程序...")
    
    # 构建可执行文件
    success = build_executable()
    
    if success:
        # 显示输出位置
        project_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.join(project_dir, "dist")
        exe_path = os.path.join(dist_dir, "watermark_app.exe")
        
        if os.path.exists(exe_path):
            print(f"成功创建可执行文件: {exe_path}")
            print("您可以在该目录中找到打包好的应用程序")
        else:
            print("构建可能失败，请检查输出日志")
    else:
        print("打包过程失败，请检查错误信息")

if __name__ == "__main__":
    main()