"""
主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_window import MainWindow
    from template_manager import TemplateManager
    from utils import show_error
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)


def check_dependencies():
    """检查依赖"""
    try:
        from PIL import Image, ImageTk, ImageDraw, ImageFont
        return True
    except ImportError:
        return False


def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        error_msg = """
缺少必要的依赖库！

请安装以下库：
pip install Pillow

或者运行：
pip install -r requirements.txt
        """
        
        # 尝试显示GUI错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("依赖错误", error_msg)
            root.destroy()
        except:
            print(error_msg)
        
        sys.exit(1)
    
    try:
        # 创建并运行应用
        app = MainWindow()
        
        # 创建默认模板（首次运行）
        template_manager = TemplateManager()
        template_manager.create_default_templates()
        
        # 运行应用
        app.run()
        
    except Exception as e:
        error_msg = f"程序启动失败: {e}"
        print(error_msg)
        
        # 尝试显示GUI错误对话框
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
